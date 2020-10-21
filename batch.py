import argparse
import os
import signal
import sys
import multiprocessing as mp
from functools import reduce

from tqdm import tqdm

from downloader import Downloader
from util import *


def run_batch(args):
    # Get queries from file.
    with open(args.queries, "r") as f:
        queries = [q.strip() for q in f.readlines() if q.strip()]

    if queries is None:
        raise Exception("Wrong call of run_batch: provide queries")
        sys.exit(1)
    if len(queries) == 0:
        raise Exception("Empty queries")
    print("Total {} # of queries are detected".format(len(queries)))
    print("")

    # Downloader setup.
    papers_total = []
    for conference in args.conference:
        # Create save folder for papers.
        savedir = os.path.join(args.root, conference)
        if not os.path.isdir(savedir):
            os.makedirs(savedir)

        # Prepare a progress bar.
        tq = tqdm(total=len(queries), ncols=80, leave=True)
        def update_tq(*args):
            tq.set_description(str(args[0])[:6])
            tq.update()

        # Prefetch the list of papers published.
        downloader = Downloader(
            root=savedir,
            conference=conference,
            timeout=args.timeout,
            download_supp=args.download_supp,
            verbose=args.verbose,
            tqdm_module=tq,
        )
        tq.write("Total {:d} papers are detected from the conference {:s}".format(
            len(downloader.papers),
            conference
        ))

        tq.write("Download papers from online ...")

        # Download with multiprocessing for efficient download.
        results = []
        with mp.Pool() as pool:
            # Signal handler setup.
            default_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            def sigint_handler(signal, frame):
                print("\nThe crawler has inturrupted by keyboard!")
                pool.terminate()
                remove_empty_files(savedir)
            signal.signal(signal.SIGINT, sigint_handler)

            # Run the downloader.
            for q in queries:
                result = pool.apply_async(
                    downloader.client,
                    (q, True,),
                    callback=update_tq,
                )
                results.append(result)
            pool.close()
            pool.join()
        papers = [r.get() for r in results]
        papers = reduce((lambda x, y: x + y), papers)
        papers_total.extend(papers)
        tq.close()

        print("")
        print("Download is now complete")
        print("Removing empty files")
        remove_empty_files(savedir)
        print("Directory is now cleared")
        print("")

    papers_total = set(papers_total)

    # Create line format to print pretty.
    len_id = len(str(len(papers_total)))
    len_title = 0
    for paper in papers_total:
        len_title_new = len(paper["title"])
        if len_title < len_title_new:
            len_title = len_title_new
    len_title = min(len_title, 60)
    line_format = "{:" + str(len_id + 2) + "s}  " \
        + "{:" + str(len_title) + "s}  " \
        + "{:s}"
    
    # Print the queries.
    # TODO add column of successful download
    print(line_format.format("ID", "TITLE", "1st AUTHOR"))
    for pid, paper in enumerate(papers_total):
        print(line_format.format(str(pid), paper["title"][:len_title], paper["authors"][0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper search with downloader")
    parser.add_argument("--root", "-r", type=str, default="default", help="save directory")
    parser.add_argument("--conference", "-c", type=str, nargs="+", default="ICCV2019", help="name of the CV converence [CVPR, ICCV, ECCV][yyyy]")
    parser.add_argument("--download-supp", action="store_true", help="download suppplementary materials along with the main manuscripts")
    parser.add_argument("--queries", "-q", type=str, default="q.txt", help="search keywords in the paper title")
    parser.add_argument("--timeout", type=float, default=60.0, help="timeout of each request for file in seconds")
    parser.add_argument("--url-list-only", action="store_true", help="produce a list of urls for external downloader")
    parser.add_argument("--verbose", "-v", action="store_true", help="print detailed messages")
    args = parser.parse_args()
    run_batch(args)

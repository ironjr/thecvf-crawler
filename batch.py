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
    # Get queries from file
    with open(args.queries, "r") as f:
        queries = [q.strip() for q in f.readlines() if q.strip()]

    if queries is None:
        raise Exception("Wrong call of run_batch: provide queries")
        sys.exit(1)
    if len(queries) == 0:
        raise Exception("Empty queries")
    print("Total {} # of queries are detected".format(len(queries)))
    print("")

    # Create save folder for papers
    savedir = os.path.join(args.root, args.conference)
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    print("Download papers from online ...")
    pbar = tqdm(total=len(queries), ncols=80)
    def update_pbar(*args):
        pbar.update()

    # Downloader setup
    downloader = Downloader(
        root=savedir,
        conference=args.conference,
        timeout=args.timeout,
        verbose=args.verbose,
        use_tqdm=True,
    )

    # Download with multiprocessing for efficient download
    results = []
    with mp.Pool() as pool:
        # Signal handler setup
        default_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        def sigint_handler(signal, frame):
            print("\nThe crawler has inturrupted by keyboard!")
            pool.terminate()
            remove_empty_files(savedir)
        signal.signal(signal.SIGINT, sigint_handler)

        # Run downloader
        for q in queries:
            result = pool.apply_async(
                downloader.client,
                (q,),
                callback=update_pbar,
            )
            results.append(result)
        pool.close()
        pool.join()
    papers = [r.get() for r in results]
    papers = reduce((lambda x, y: x + y), papers)

    print("")
    print("Download is now complete")
    print("Removing empty files")
    remove_empty_files(savedir)
    print("Directory is now cleared")
    print("")

    # Create line format to print pretty
    len_id = len(str(len(papers)))
    len_title = 0
    for paper in papers:
        len_title_new = len(paper["title"])
        if len_title < len_title_new:
            len_title = len_title_new
    if len_title > 60:
        len_title = 60
    line_format = "{:" + str(len_id + 2) + "s}  " + \
            "{:" + str(len_title) + "s}  " + \
            "{:s}"
    
    # Print the queries
    # TODO add column of successful download
    print(line_format.format("ID", "TITLE", "1st AUTHOR"))
    for pid, paper in enumerate(papers):
        print(line_format.format(str(pid), paper["title"][:len_title], paper["authors"][0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper search with downloader")
    parser.add_argument("--root", "-r", type=str, default="default",
            help="save directory")
    parser.add_argument("--conference", "-c", type=str, default="ICCV2019", help="name of the CV converence [CVPR, ICCV, ECCV][yyyy]")
    parser.add_argument("--queries", "-q", type=str, default="sample.txt",
            help="search keywords in the paper title")
    parser.add_argument("--timeout", type=float, default=5.0,
            help="timeout of each request for file in seconds")
    parser.add_argument("--verbose", "-v", action="store_true",
            help="print detailed messages")
    args = parser.parse_args()
    run_batch(args)

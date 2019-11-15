import argparse
import os
import signal
import multiprocessing as mp

from tqdm import tqdm

from crawler import Crawler
from parser import CVPRParser
from util import *


def main(args):
    # TODO Perhaps add support for multiple keywords?
    keywords = [args.keyword,]

    # Get queries from file
    for 
    queries = 
    print("Total {} # of papers detected".format(len(papers)))

    # Search for the keywords
    print("")
    for keyword in keywords:
        result = [paper for paper in papers if keyword.lower() in paper["title"].lower()]
        print("CVPR papers with keyword: {}".format(keyword))
        print("Total {} # of papers found".format(len(result)))

        if not os.path.isdir(keyword):
            os.mkdir(keyword)
        if not os.path.isdir(os.path.join(keyword, "arxiv")):
            os.mkdir(os.path.join(keyword, "arxiv"))
        if not os.path.isdir(os.path.join(keyword, "openaccess")):
            os.mkdir(os.path.join(keyword, "openaccess"))

        # Search website for more information
        print("Download papers from online ...")
        crawler = Crawler(keyword, timeout=args.timeout, verbose=args.verbose)
        pbar = tqdm(total=len(result))
        def update_pbar(*args):
            pbar.update()

        default_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = mp.Pool(mp.cpu_count())

        def sigint_handler(signal, frame):
            print("\nThe crawler has inturrupted by keyboard!")
            pool.terminate()
            for keyword in keywords:
                remove_empty_files(keyword)

        signal.signal(signal.SIGINT, sigint_handler)
        for i in range(len(result)):
            pool.apply_async(crawler.client, args=(result[i],), callback=update_pbar)
        pool.close()
        pool.join()

        print("")
        print("Download is now complete")
        print("Removing empty files")
        remove_empty_files(keyword)
        print("Directory is now cleared")
        print("")

        # Create line format to print pretty
        len_id = 0; len_title = 0
        for paper in result:
            len_id_new = len(str(paper["id"]))
            if len_id < len_id_new:
                len_id = len_id_new
            len_title_new = len(paper["title"])
            if len_title < len_title_new:
                len_title = len_title_new
        line_format = "{:" + str(len_id + 2) + "s}  " + \
                "{:" + str(len_title) + "s}  " + \
                "{:s}"
        
        # Print the results
        # TODO add column of successful download
        print(line_format.format("ID", "TITLE", "1st AUTHOR"))
        for paper in result:
            print(line_format.format(str(paper["id"]), paper["title"], paper["authors"][0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper search with downloader")
    parser.add_argument("--keyword", type=str, default="detection",
            help="search keywords in the paper title")
    parser.add_argument("--timeout", type=float, default=5.0,
            help="timeout of each request for file in seconds")
    parser.add_argument("--verbose", "-v", action="store_true",
            help="print detailed messages")
    args = parser.parse_args()

    main(args)

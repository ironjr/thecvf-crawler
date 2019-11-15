import json
import os
import re
import requests
import sys
import urllib

from unidecode import unidecode

from parser import CVFMainParser


class Downloader(object):
    def __init__(self, root, conference, timeout=5.0, get_abstract=False, verbose=False, tqdm_module=None):
        self.root = root
        self.conference = conference
        self.timeout = timeout
        self.urlroot = "http://openaccess.thecvf.com"
        self.urlmain = urllib.parse.urljoin(
            self.urlroot,
            "{}.py".format(conference),
        )
        self.urlsearch = urllib.parse.urljoin(
            self.urlroot,
            "{}_search.py".format(conference),
        )
        self.search_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate",
            "content-type": "application/x-www-form-urlencoded",
            "content-length": "24",
            "origin": "http://openaccess.thecvf.com",
            "connection": "keep-alive",
            "referer": "http://openaccess.thecvf.com/{}_search.py".format(conference),
            "upgrade-insecure-requests": "1",
        }

        # TODO
        self.get_abstract = get_abstract

        self.verbose = verbose
        self.use_tqdm = tqdm_module is not None
        if self.use_tqdm:
            self.print_function = tqdm_module.write
        else:
            self.print_function = print

        # Fetch the whole list of papers provided in the main page
        self.papers = []
        self.database_ready = False
        self.crawl_database()

    def crawl_database(self):
        if self.database_ready:
            # TODO perhaps reload?
            return

        r = requests.get(
            self.urlmain,
            timeout=self.timeout,
        )
        if not r.ok:
            # Connection failed
            self._print_failure(
                self.urlmain,
                "Cannot reach thecvf server",
                r.status_code,
            )
            return

        # Successful connection
        parser_main = CVFMainParser()
        parser_main.feed(str(r.content))
        self.papers = parser_main.papers
        if len(self.papers) == 0:
            self._print_failure(
                self.urlmain,
                "No papers found in the main page",
                r.status_code,
            )
            return

        self.titles = [p["title"].lower() for p in self.papers]
        self.database_ready = True

    def client_search(self, query):
        data = { "query": query }
        r = requests.post(
            self.urlsearch,
            headers=self.search_headers,
            data=data,
            timeout=self.timeout,
        )
        if not r.ok:
            # Connection failed
            self._print_failure(
                query,
                "Cannot reach thecvf server",
                r.status_code,
            )
            return []

        # Successful connection
        parser_main = CVFMainParser()
        parser_main.feed(str(r.content))
        papers = parser_main.papers
        if len(papers) == 0:
            self._print_failure(
                query,
                "No papers found in the main page",
                r.status_code,
            )
            return []

    def client(self, query):
        if not self.database_ready:
            # Try once more
            self.crawl_database()
            if not self.database_ready:
                # Connection failed
                self._print_failure(
                    query,
                    "Cannot reach thecvf server",
                    r.status_code,
                )
            return []
        
        # Database is ready
        papers = [self.papers[i] for i, t in enumerate(self.titles) if query in t]
        self.download(papers)
        return papers

    def download(self, papers):
        successes = 0
        for p in papers:
            self.print_function("Downloading: {:10s}".format(p["title"]))

            # TODO Get abstract of the paper
            #  if html in p:

            # Download paper pdf
            if p["pdf"]:
                url = urllib.parse.urljoin(self.urlroot, p["pdf"])
                r = requests.get(url, stream=True, timeout=self.timeout)
                if r.ok:
                    # Successful connection
                    path = os.path.join(
                        self.root,
                        p["pdf"].split("/")[2],
                    )
                    with open(path, "wb") as f:
                        f.write(r.content)
                    successes += 1
                else:
                    self._print_failure(
                        p["title"],
                        "Cannot download PDF from the link",
                        r.status_code,
                    )
            else:
                self._print_failure(
                    p["title"],
                    "No URL of PDF",
                    r.status_code,
                )

            # Download supplementary pdf if it exists
            if p["supp"]:
                url = urllib.parse.urljoin(self.urlroot, p["supp"])
                r = requests.get(url, stream=True, timeout=self.timeout)
                if r.ok:
                    # Successful connection
                    path = os.path.join(
                        self.root,
                        p["supp"].split("/")[2],
                    )
                    with open(path, "wb") as f:
                        f.write(r.content)
                else:
                    self._print_failure(
                        p["title"],
                        "Cannot download supplementary PDF from the link",
                        r.status_code,
                    )
        return successes

    def _print_failure(self, title, msg, status_code):
        self.print_function("{:30s}: {}: {:d}" \
            .format(title, msg, status_code))


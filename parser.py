from html.parser import HTMLParser


class CVFMainParser(HTMLParser):
    def __init__(self):
        """parser of the main search page
        """
        super(CVFMainParser, self).__init__()
        self.flag_authors = False
        self.flag_in_content = False
        self.flag_in_dt = False
        self.flag_in_a = False
        self.counter_dd = 0
        self.counter_a = 0
        self.papers = []
        self.paper = {
            "title": "",
            "authors": [],
            "html": "",
            "pdf": "",
            "supp": "",
        }

    def handle_starttag(self, tag, attrs):
        if self.flag_in_content:
            if tag == "dt": # paper title
                self.flag_in_dt = True
            if tag == "dd": # link contents
                self.counter_dd += 1
                self.counter_a = 0
            if tag == "a":
                self.flag_in_a = True
                if self.flag_in_dt:
                    for name, value in attrs:
                        if name == "href":
                            self.paper["html"] = value
                elif self.counter_dd == 1: # authors
                    self.flag_authors = True
                elif self.counter_dd == 2: # links
                    self.counter_a += 1
                    if self.counter_a == 1: # paper
                        for name, value in attrs:
                            if name == "href":
                                self.paper["pdf"] = value
                    elif self.counter_a == 2: # supplementary
                        for name, value in attrs:
                            if name == "href":
                                self.paper["supp"] = value
        else:
            if tag == "div":
                for name, value in attrs:
                    if name == "id" and value == "content":
                        self.flag_in_content = True

    def handle_endtag(self, tag):
        if tag == "div" and self.counter_dd == 0:
            self.flag_in_content = False
        if tag == "dt":
            self.flag_in_dt = False
        if tag == "dd":
            self.flag_authors = False
            if self.flag_in_content and self.counter_dd == 2:
                self.papers.append(self.paper)
                self.counter_dd = 0
                self.paper = {
                    "title": "",
                    "authors": [],
                    "html": "",
                    "pdf": "",
                    "supp": "",
                }
        if tag == "a":
            self.flag_in_a = False

    def handle_data(self, data):
        if self.flag_in_dt and self.flag_in_a:
            self.paper["title"] = data
        if self.flag_authors and self.flag_in_a:
            self.paper["authors"].append(data)


#  class CVFPaperParser(HTMLParser):
#      def __init__(self):
#          """parser of single paper description page
#          """
#          super(CVFPaperParser, self).__init__()
#          self.flag_in_content = False
#          slef.flag_in_dt = False
#          self.counter_dd = 0
#          self.counter_a = 0
#          self.papers = []
#
#      def handle_starttag(self, tag, attrs):
#          if self.flag_in_content:
#              if tag == "dl": # single result
#                  self.counter_dd = 0
#              if tag == "dt":
#                  self.flag_in_dt = True
#              if tag == "dd":
#                  self.counter_dd += 1
#                  self.counter_a = 0
#
#              if tag == "a"
#                  if self.flag_dt:
#
#                  elif self.counter_dd == 2:
#                      self.counter_a += 1
#                      if self.counter_a == 1: # paper
#                          attrs["href"]
#
#          else:
#              if tag = "div":
#                  for name, value in attrs:
#                      if name == "id" and value == "content":
#                          self.flag_in_content = True
#
#      def handle_endtag(self, tag):
#          if tag == "div" and self.flag_in_content:
#              self.flag_in_content = False
#
#          if tag == "tr":
#              self.flag_intr = False
#              # At least title should be provided
#              if "title" in self.cvpr_paper and "id" in self.cvpr_paper:
#                  # Remove the duplicates
#                  if self.cvpr_paper["id"] not in self.paper_ids:
#                      self.paper_ids.append(self.cvpr_paper["id"])
#                      self.cvpr_papers.append(self.cvpr_paper)
#          elif tag == "td":
#              self.flag_intd = False
#
#      def handle_data(self, data):
#          if self.flag_intr and self.flag_intd:
#              if self.counter_td == 4:
#                  # Title of the paper
#                  self.cvpr_paper["title"] = data.strip()
#              elif self.counter_td == 5:
#                  # Authors of the paper
#                  self.cvpr_paper["authors"] = [name.strip() for name in data.split(";")]
#              elif self.counter_td == 6:
#                  # ID of the paper
#                  self.cvpr_paper["id"] = int(data)
#              else:
#                  pass

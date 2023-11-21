import os
import re
from datetime import datetime

class FileContent():
    def __init__(self, path):
        self.path = path
        with open(self.path, 'r', encoding='utf-8') as file:
            self.text = file.read()
            searchObj = re.search(r"title: (.*)\ndate: (.*)\ntags: (.*)\n---(.*)", self.text)
            self.title = searchObj[1]
            self.date = datetime.strptime(searchObj[2], "%Y-%m-%d %H:%M:%S")
            self.tags = searchObj[3]
            self.content = searchObj[4]



if __name__ == "__main__":
    # ./_exercise/路径下所有文件名的列表
    path = os.path.join(os.path.dirname(__file__), "_exercise")
    file_list = os.listdir(path)
    a = FileContent(os.path.join(path, file_list[0]))
    # print(a.text)
    # print("title: ", a.title)
    # print("date: ", a.date)
    # print("tags: ", a.tags)
    print("content: ", a.content)
    # print(a.content)
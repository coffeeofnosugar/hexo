import os
import re
import logging
from datetime import datetime


class FileContent():
    def __init__(self, path):
        self.path = path
        self.fileName = os.path.basename(path)
        self.fileNameDate = datetime.strptime(self.fileName.split("_")[0], "%Y-%m-%d")
        with open(self.path, 'r', encoding='utf-8') as file:
            self.text = file.read()
            searchObj = re.search(r"title: (.*)\ndate: (.*)\ntags: (.*)\n---\n(.*)", self.text, re.S)
            self.title = searchObj[1]
            self.date = datetime.strptime(searchObj[2].strip(), "%Y-%m-%d %H:%M:%S")
            self.tags = searchObj[3]
            self.content = searchObj[4]
            self.content = re.sub(r"<!-- more -->\n", "", self.content)
            self.content = re.sub(r"""<link rel="stylesheet" href="/../css/(.*).css">\n""", "", self.content)
        if self.fileNameDate.day != self.date.day:
            logging.warning("文件名日期和文件内容日期不一致")
        # else:
        #     logging.info("文件名日期和文件内容日期一致")
    

if __name__ == "__main__":
    # ./_exercise/路径下所有文件名的列表
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    path = os.path.dirname(__file__)
    path_exercise = os.path.join(path, "_exercise")
    file_list = os.listdir(path_exercise)
    classList = []
    for fileName in file_list:
        classList.append(FileContent(os.path.join(path_exercise, fileName)))

    monthToDate = {}

    for monthFile in os.listdir(path):
        if re.match(r"^\d{4}年\d{2}月_exercise.md$", monthFile):
            with open(os.path.join(path, monthFile), 'r', encoding='utf-8') as file:
                findallObj = re.findall(r"\n### (.*)\n", file.read())
                monthToDate[monthFile] = findallObj


    for item in classList:
        monthDate = item.fileNameDate.strftime("%Y年%m月")
        monthFile = monthDate + "_exercise.md"
        if monthFile not in os.listdir(path):
            with open(os.path.join(path, monthFile), 'w', encoding='utf-8') as file:
                content = f"""---\ntitle: {monthDate} 运动\ndate: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\ntags: \n  - 运动\n  - 日常\n---\n\n<link rel="stylesheet" href="/../css/base.css">\n<link rel="stylesheet" href="/../css/center.css">\n<link rel="stylesheet" href="/../css/images.css">\n"""
                file.write(content + f"\n--- \n\n### {item.title}\n" + item.content)
                monthToDate[monthFile] = [item.title]
                logging.info(f"创建月文件{monthFile}并写入{item.title}")
        else:
            if item.title not in monthToDate[monthFile]:
                with open(os.path.join(path, monthFile), 'a', encoding='utf-8') as file:
                    file.write("\n" + f"\n--- \n\n### {item.title}\n" + item.content)
                    monthToDate[monthFile].append(item.title)
                    logging.info(f"写入{item.title}")
            else:
                logging.debug(f"{item.title}已存在于{monthFile}")
    logging.debug(monthToDate)



        


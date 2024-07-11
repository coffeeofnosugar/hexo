import os
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
path = os.path.dirname(__file__)


class Image():
    def __init__(self, name) -> None:
        self.name = name
        l1 = name.split(".")
        l2 = l1[0].split("_")
        self.date = datetime.strptime(l2[0], "%Y-%m-%d")
        self.exerciseType = l2[1] if len(l2) > 1 else "跑步"

class ImageFiles():
    def __init__(self) -> None:
        imagePath = os.path.join(path, r"../images/exercise")
        images = os.listdir(imagePath)
        self.dateList = []
        self.monthList = []
        self.dateDict = {}
        for name in images:
            image = Image(name)
            self.dateList.append(image.date)
            self.monthList.append(image.date.strftime("%Y-%m"))
            if image.date in self.dateDict:
                self.dateDict[image.date].append(image)
            else:
                self.dateDict[image.date] = [image]
        self.dateSet = set(self.dateList)
        self.monthList = set(self.monthList)


class Md():
    def __init__(self, name) -> None:
        mdPath = os.path.join(path, "_exercise")
        self.name = name
        self.date = datetime.strptime(self.name.split("_")[0], "%Y-%m-%d")

        with open(os.path.join(mdPath, self.name), "r", encoding = "UTF-8") as file:
            self.text = file.read()
            searchObj = re.search(r"title: (.*)\ndate: (.*)\ntags: (.*)\n---\n(.*)", self.text, re.S)
            self.title = searchObj[1]
            self.tags = searchObj[3]
            self.content = searchObj[4]
            self.content = re.sub(r"<!-- more -->\n", "", self.content)
            self.content = re.sub(r"""<link rel="stylesheet" href="/../css/(.*).css">\n""", "", self.content)
        
class MdFiles():
    def __init__(self) -> None:
        mdPath = os.path.join(path, "_exercise")
        self.nameList = os.listdir(mdPath)
        self.dateList = []
        self.dateDict = {}
        for name in self.nameList:
            md = Md(name)
            self.dateList.append(md.date)
            self.dateDict[md.date] = md
        self.dateSet = set(self.dateList)


if __name__ == "__main__":
    imageFiles = ImageFiles()
    mdFiles = MdFiles()
    allExercise = imageFiles.dateSet | mdFiles.dateSet
    # 图片文件和md文件的所有日期集合
    allExercise = sorted(allExercise)
    

    # exit()
    # 字典 [跟目录下的运动文件] : [这个文件下所包含的日期]
    monthToDate = {}
    for monthFile in os.listdir(path):
        if re.match(r"^\d{4}-\d{2}_exercise.md$", monthFile):
            with open(os.path.join(path, monthFile), 'r', encoding='utf-8') as file:
                findallObj = re.findall(r"\n### (\d{4}-\d{2}-\d{2})", file.read())
                monthToDate[monthFile] = findallObj

    for date in allExercise:
        logging.debug(date.strftime("%Y-%m-%d"))
        day = date.strftime("%Y-%m-%d")
        # 先判断是否是md文件
        if date in mdFiles.dateSet:
            # 是md文件
            md = mdFiles.dateDict[date]
            dayType = day + " 运动"
            littleTitle = f"\n--- \n\n### {dayType}\n"
            monthDate = date.strftime("%Y-%m")
            fileName = monthDate + "_exercise.md"

            title = f"""---\ntitle: {date.strftime("%Y年%m月")} 运动\ndate: {date.strftime("%Y-%m-%d %H:%M:%S")}\ntags: \n  - 运动\n  - 日常\n---\n\n<link rel="stylesheet" href="/../css/base.css">\n<link rel="stylesheet" href="/../css/center.css">\n<link rel="stylesheet" href="/../css/images.css">\n"""
            content = littleTitle + md.content

            if fileName not in os.listdir(path):
                # 需要全新创建一个md文件
                with open(os.path.join(path, fileName), "w", encoding="utf-8") as file:
                    file.write(title + content)
                    monthToDate[fileName] = [day]
                    logging.info(f"创建文件 {fileName}")
            else:
                # 需要添加到md文件中
                if day not in monthToDate[fileName]:
                    with open(os.path.join(path, fileName), "a", encoding="utf-8") as file:
                        file.write("\n" + littleTitle + md.content)
                        monthToDate[fileName].append(day)
                        logging.info(f"在文件 {fileName} 中添加 {day}")
                else:
                    logging.debug(f"{md.name} 已存在于 {fileName}")
        else:
            # 是图片文件
            images = imageFiles.dateDict[date]
            
            day = ""
            dayType = ""
            body = ""

            for image in images:
                s1 = image.name.split(".")[0]
                s2 = s1.split("_")
                day = s2[0]
                if len(s2) == 1:
                    dayType += " 跑步"
                else:
                    dayType += " " + " ".join(s2[1:])
                body += f"""\n\n<img class="half" src="/../images/exercise/{image.name}"></img>\n\n"""

            littleTitle = f"\n--- \n\n### {day}{dayType}\n"
            monthDate = date.strftime("%Y-%m")
            fileName = monthDate + "_exercise.md"
            title = f"""---\ntitle: {date.strftime("%Y年%m月")} 运动\ndate: {date.strftime("%Y-%m-%d %H:%M:%S")}\ntags: \n  - 运动\n  - 日常\n---\n\n<link rel="stylesheet" href="/../css/base.css">\n<link rel="stylesheet" href="/../css/center.css">\n<link rel="stylesheet" href="/../css/images.css">\n"""
            content = littleTitle + body
            
            if fileName not in os.listdir(path):
                # 需要全新创建一个md文件
                with open(os.path.join(path, fileName), "w", encoding="utf-8") as file:
                    file.write(title + content)
                    monthToDate[fileName] = [day]
                    logging.info(f"创建文件 {fileName}")
            else:
                # 需要添加到md文件中
                if day not in monthToDate[fileName]:
                    with open(os.path.join(path, fileName), "a", encoding="utf-8") as file:
                        file.write("\n" + content)
                        monthToDate[fileName].append(day)
                        logging.info(f"在文件 {fileName} 中添加 {image.name}")
                else:
                    logging.debug(f"{image.name} 已存在于 {fileName}")

    # 根目录md文件中标题日期列表
    a = []
    for key in monthToDate:
        a.extend(monthToDate[key])
    # 去重a后排序
    s = sorted(list(set(a)))

    # 检查
    if len(a) != len(s):
        logging.warning(f"拥有重复的标题，请仔细检查md文件")
    if len(a) != len(allExercise):
        logging.warning(f"漏掉了文件，请仔细检查_exercise和image文件夹")
    else:
        logging.info(f"载入完成")


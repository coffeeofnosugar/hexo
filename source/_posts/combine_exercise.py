import os
import json
from datetime import datetime


def write_file():
    filename_list = read_json()
    if filename_list:
        last_date = datetime.strptime(filename_list[-1].split('_')[0], '%Y-%m-%d')
    else:
        last_date = datetime(1998, 9, 20)
    
    # ./_exercise/路径下所有文件名的列表
    file_list = os.listdir("./_exercise/")

    if not any(item in filename_list for item in file_list):
        return 0

    for item in file_list:
        if item not in filename_list:
            with open("./exercise.md", 'a', encoding="utf-8") as file:
                with open(f"./_exercise/{item}", 'r', encoding="utf-8") as file_item:
                    date = datetime.strptime(item.split('_')[0], '%Y-%m-%d')
                    if date.month != last_date.month:
                        file.write("\n\n---\n\n### ")
                        file.write(datetime.strftime(date.date(), "%Y年%m月"))
                        file.write("\n")
                    last_date = date
                    
                    contents = file_item.readlines()
                    for content in contents:
                        if content == '---\n' or content.startswith(("date", "tags", "<link ")):
                            continue
                        elif (content.startswith("title")):
                            file.write("\n\n---\n\n")
                            content = content.replace("title: ", "")
                            content = content.replace(" 运动", "")
                            file.write("#### " + content)
                        else:
                            pass
                            file.write(content)
            add_exercise_filename(item)
            print(f"写入{item}")

def add_exercise_filename(filename_):
    """
    写入拼接的文件名
    """
    filename_list = read_json()
    filename_list.append(filename_)
    with open("./_exercise_filename.json", 'w', encoding="utf-8") as file:
        file.write(json.dumps(filename_list, indent=4))

def read_json() -> list:
    """
    读取已经拼接的文件名
    """
    with open("./_exercise_filename.json", 'r', encoding="utf-8") as file:
        filename_list = json.loads(file.read())
        return filename_list

if __name__ == "__main__":
    if not write_file():
        print("无新增文件")
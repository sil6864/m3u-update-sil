import requests
import datetime
import os

# 原始M3U文件的URL
SOURCE_M3U_URL = "https://raw.githubusercontent.com/mursor1985/LIVE/refs/heads/main/douyuyqk.m3u"
# 目标输出文件名
OUTPUT_M3U_FILE = "douyuyqk_modified.m3u"
# 包含要插入内容的文件的名称
INSERT_CONTENT_FILE = "updata.txt"

# 插入点标记（在这行之后插入）
INSERTION_MARKER = "https://cdn.jsdelivr.net/gh/feiyang666999/testvideo/hlg4kvideo/playlist.m3u8"

def fetch_and_modify_m3u():
    print(f"[{datetime.datetime.now()}] Starting M3U update process.")

    # 1. 读取要插入的内容
    content_to_insert = ""
    if os.path.exists(INSERT_CONTENT_FILE):
        with open(INSERT_CONTENT_FILE, "r", encoding="utf-8") as f:
            content_to_insert = f.read().strip()
        print(f"Content to insert loaded from {INSERT_CONTENT_FILE}.")
    else:
        print(f"Error: {INSERT_CONTENT_FILE} not found. Cannot insert content.")
        return

    if not content_to_insert:
        print(f"Warning: {INSERT_CONTENT_FILE} is empty. No content will be inserted.")

    # 2. 获取原始M3U内容
    print(f"Fetching M3U from: {SOURCE_M3U_URL}")
    try:
        response = requests.get(SOURCE_M3U_URL)
        response.raise_for_status()  # 检查HTTP请求是否成功
        original_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching M3U content: {e}")
        return

    lines = original_content.splitlines()
    modified_lines = []
    inserted = False

    # 3. 遍历并插入内容
    for line in lines:
        modified_lines.append(line)
        if line.strip() == INSERTION_MARKER.strip() and not inserted:
            if content_to_insert: # 只有当有内容时才插入
                modified_lines.append(content_to_insert)
                inserted = True
                print("Content inserted successfully after marker.")
            else:
                print("No content to insert from updata.txt.")


    # 如果原始文件不包含插入点，则在文件末尾添加（可选，根据需求决定）
    if not inserted and content_to_insert:
        print(f"Warning: Insertion marker '{INSERTION_MARKER}' not found. Appending content to end.")
        modified_lines.append(content_to_insert)
        inserted = True # 标记为已插入，即使在末尾

    new_m3u_content = "\n".join(modified_lines)

    # 4. 保存到文件
    with open(OUTPUT_M3U_FILE, "w", encoding="utf-8") as f:
        f.write(new_m3u_content)
    print(f"Modified M3U saved to {OUTPUT_M3U_FILE}")

if __name__ == "__main__":
    fetch_and_modify_m3u()

import requests
import datetime
import os
import re # 导入正则表达式模块

# --- 常量定义 ---
SOURCE_M3U_URL_DOUYU = "https://raw.githubusercontent.com/mursor1985/LIVE/refs/heads/main/douyuyqk.m3u"
SOURCE_M3U_URL_HUYA = "https://raw.githubusercontent.com/mursor1985/LIVE/refs/heads/main/huyayqk.m3u"
OUTPUT_M3U_FILE = "lunbo.m3u" # 新的输出文件名
INSERT_CONTENT_FILE = "updata.txt"

# 虎牙M3U中需要删除的头部结束标记
# 从 #EXTM3U 到此行（包含此行）的内容将被删除
HUYA_HEADER_END_MARKER = "https://cdn.jsdelivr.net/gh/feiyang666999/testvideo/hlg4kvideo/playlist.m3u8"

# --- 辅助函数：获取并处理M3U内容 ---
def fetch_and_process_m3u_content(url, target_group_title):
    """
    从指定URL获取M3U内容，并将其中的group-title值替换为target_group_title。
    """
    print(f"[{datetime.datetime.now()}] Fetching and processing M3U from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP请求是否成功
        original_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching M3U content from {url}: {e}")
        return None

    processed_lines = []
    for line in original_content.splitlines():
        # 替换 group-title 值
        if line.startswith("#EXTINF:"):
            # 使用正则表达式匹配 group-title="任意内容" 并替换
            line = re.sub(r'group-title="[^"]*"', f'group-title="{target_group_title}"', line)
        processed_lines.append(line)
    return processed_lines

# --- 主更新流程函数 ---
def main_update_process():
    print(f"[{datetime.datetime.now()}] Starting M3U update process.")

    # 1. 读取要添加到尾部的内容 (来自 updata.txt)
    content_to_append = ""
    if os.path.exists(INSERT_CONTENT_FILE):
        with open(INSERT_CONTENT_FILE, "r", encoding="utf-8") as f:
            content_to_append = f.read().strip()
        print(f"Content to append loaded from {INSERT_CONTENT_FILE}.")
    else:
        print(f"Error: {INSERT_CONTENT_FILE} not found. Cannot append content.")
        # 即使文件不存在，也允许继续处理其他M3U内容
        # return # 如果希望文件不存在就停止，则取消注释此行

    if not content_to_append:
        print(f"Warning: {INSERT_CONTENT_FILE} is empty. No custom content will be appended.")

    # 2. 处理斗鱼M3U内容
    douyu_processed_lines = fetch_and_process_m3u_content(SOURCE_M3U_URL_DOUYU, "douyu")
    if douyu_processed_lines is None:
        print("Failed to process Douyu M3U. Exiting.")
        return

    # 3. 处理虎牙M3U内容并删除其头部
    huya_raw_processed_lines = fetch_and_process_m3u_content(SOURCE_M3U_URL_HUYA, "huya")
    if huya_raw_processed_lines is None:
        print("Failed to process Huya M3U. Exiting.")
        return

    huya_lines_without_header = []
    skip_header = True
    for line in huya_raw_processed_lines:
        if skip_header:
            # 找到头部结束标记后，停止跳过
            if line.strip() == HUYA_HEADER_END_MARKER.strip():
                skip_header = False
                continue # 这一行是头部结束标记，也跳过不添加到结果中
            continue # 继续跳过当前行
        huya_lines_without_header.append(line)
    print("Huya M3U header removed successfully.")

    # 4. 合并所有内容
    final_m3u_lines = []
    
    # 确保最终文件以 #EXTM3U 开头，只保留一个
    if douyu_processed_lines and douyu_processed_lines[0].strip() == "#EXTM3U":
        final_m3u_lines.append(douyu_processed_lines[0]) # 取斗鱼的 #EXTM3U
        douyu_processed_lines = douyu_processed_lines[1:] # 移除斗鱼列表中的第一个 #EXTM3U
    else:
        final_m3u_lines.append("#EXTM3U") # 如果斗鱼列表没有，则手动添加

    # 添加处理后的斗鱼内容
    final_m3u_lines.extend(douyu_processed_lines)
    print("Processed Douyu content added.")

    # 添加处理后的虎牙内容（不含头部）
    final_m3u_lines.extend(huya_lines_without_header)
    print("Processed Huya content appended.")

    # 5. 将 updata.txt 内容添加到最终文件的尾部
    if content_to_append:
        # 确保在添加前有一个换行符，避免与前一行内容粘连
        if final_m3u_lines and not final_m3u_lines[-1].endswith('\n'):
             final_m3u_lines.append("") # 添加一个空行作为分隔
        final_m3u_lines.append(content_to_append)
        print("Custom content from updata.txt appended to the very end.")
    else:
        print("No custom content to append from updata.txt (file was empty).")

    # 6. 保存到新的输出文件
    new_m3u_content = "\n".join(final_m3u_lines)
    with open(OUTPUT_M3U_FILE, "w", encoding="utf-8") as f:
        f.write(new_m3u_content)
    print(f"Final combined M3U saved to {OUTPUT_M3U_FILE}")

if __name__ == "__main__":
    main_update_process()

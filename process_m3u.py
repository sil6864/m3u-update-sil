# process_m3u.py

import requests
import os

def fetch_and_process_m3u(url, replacements):
    """
    从指定URL获取M3U内容，并根据replacements字典进行字符串替换。
    返回处理后的行列表和原始M3U的第一个非空行（通常是#EXTM3U）。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果请求失败，抛出HTTPError
        content_lines = response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], ""

    processed_lines = []
    first_line = ""
    for line in content_lines:
        if not first_line and line.strip():
            first_line = line.strip() # 记录第一个非空行，通常是#EXTM3U
        
        modified_line = line
        for old_str, new_str in replacements.items():
            modified_line = modified_line.replace(old_str, new_str)
        processed_lines.append(modified_line)
    
    return processed_lines, first_line

def main():
    huya_url = "http://10.0.1.1:35455/huyayqk.m3u"
    douyu_url = "http://10.0.1.1:35455/douyuyqk.m3u"
    output_filename = "iptv.m3u"

    # 定义虎牙内容的替换规则
    huya_replacements = {
        "一起看": "huya",
        "原创": "huya"
    }

    # 定义斗鱼内容的替换规则
    douyu_replacements = {
        "一起看": "douyu",
        "原创IP": "douyu"
    }

    print(f"Fetching and processing Huya M3U from {huya_url}...")
    huya_processed_lines, huya_first_line = fetch_and_process_m3u(huya_url, huya_replacements)
    
    print(f"Fetching and processing Douyu M3U from {douyu_url}...")
    douyu_processed_lines, douyu_first_line = fetch_and_process_m3u(douyu_url, douyu_replacements)

    if not huya_processed_lines and not douyu_processed_lines:
        print("No content fetched from either URL. Exiting.")
        return

    # 合并内容
    merged_content = []
    
    # 保留第一个M3U文件的头部（例如 #EXTM3U）
    if huya_first_line:
        merged_content.append(huya_first_line)
    elif douyu_first_line:
        merged_content.append(douyu_first_line)

    # 添加虎牙处理后的内容，跳过其头部（如果已添加）
    for line in huya_processed_lines:
        if line.strip() and line.strip() != huya_first_line:
            merged_content.append(line)

    # 添加斗鱼处理后的内容，跳过其头部（如果已添加）
    for line in douyu_processed_lines:
        if line.strip() and line.strip() != douyu_first_line:
            merged_content.append(line)

    # 确保输出目录存在
    output_dir = os.getenv('OUTPUT_DIR', '.') # 允许通过环境变量指定输出目录
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    # 将合并后的内容写入文件
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for line in merged_content:
                f.write(line + "\n")
        print(f"Successfully merged and saved to {output_path}")
    except IOError as e:
        print(f"Error writing to file {output_path}: {e}")

if __name__ == "__main__":
    main()

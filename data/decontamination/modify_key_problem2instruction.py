"""原来生成的文件中problem字段不符合条件，改成instruction字段，还有一个字段也改了"""

from pathlib import Path
import json

def read_jsonl(file_path: str) -> list[dict]:
    """读取 JSONL 文件并返回数据列表"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path} - {e}")
        return []
    return data

def write_jsonl(file_path: str, data: list[dict]):
    """将数据写入 JSONL 文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    except IOError as e:
        print(f"Error: Failed to write to {file_path} - {e}")

def process_file(input_file: str):
    """处理单个文件，将 problem 改为 instruction，solution 改为 response，并写入新文件"""
    # 读取数据
    data = read_jsonl(input_file)
    if not data:
        return  # 如果读取失败，直接返回

    # 修改字段名
    for item in data:
        if 'problem' in item:
            item['instruction'] = item.pop('problem')
        if 'solution' in item:
            item['response'] = item.pop('solution')

    # 确定新文件的路径（在原文件名后加上 _modified）
    input_path = Path(input_file)
    output_file = input_path.with_stem(input_path.stem + "_modified")

    # 写回新文件
    write_jsonl(output_file, data)
    print(f"Processed: {input_file} -> {output_file}")

def main():
    # 定义两个文件路径
    file1 = "/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_merged_data_clean_up_decontamination.jsonl"
    file2 = "/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_processed_batch_inference_data_clean_up_decontamination.jsonl"
    
    # 处理两个文件
    process_file(file1)
    process_file(file2)

if __name__ == "__main__":
    main()
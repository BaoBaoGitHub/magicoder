import json

def check_duplicate_custom_ids(file_path):
    seen_ids = set()
    duplicates = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    custom_id = data.get('custom_id')
                    if custom_id in seen_ids:
                        duplicates.add(custom_id)
                    else:
                        seen_ids.add(custom_id)
                except json.JSONDecodeError:
                    print(f"警告: 跳过无效的 JSON 行: {line}")
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return

    if duplicates:
        print("发现重复的 custom_id:")
        for dup in duplicates:
            print(dup)
    else:
        print("没有发现重复的 custom_id")

if __name__ == "__main__":
    file_path = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/transformed_data_unique.jsonl'
    check_duplicate_custom_ids(file_path)
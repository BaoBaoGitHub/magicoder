import json

def filter_matching_entries(file1_path, file2_path, output_path):
    # 第一步：读取文件1中的所有 custom_id
    custom_ids = set()
    with open(file1_path, 'r', encoding='utf-8') as f1:
        for line in f1:
            try:
                data = json.loads(line.strip())
                custom_id = data.get('custom_id')
                if custom_id:
                    custom_ids.add(custom_id)
            except json.JSONDecodeError:
                print(f"警告: 跳过文件1中的无效行")

    # 第二步：在文件2中查找 raw_index 与 custom_id 匹配的行
    matching_entries = []
    with open(file2_path, 'r', encoding='utf-8') as f2:
        for line in f2:
            try:
                data = json.loads(line.strip())
                raw_index = data.get('raw_index')
                if raw_index in custom_ids:
                    matching_entries.append(data)
            except json.JSONDecodeError:
                print(f"警告: 跳过文件2中的无效行")

    # 第三步：将匹配的行写入新文件
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for entry in matching_entries:
            outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"筛选完成，匹配的行已保存到: {output_path}")

# 设置文件路径
file1_path = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/seed_custom_for_evol_instruct.jsonl'
file2_path = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/merged_api_and_batch.jsonl'
output_path = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/seed_data_for_evol_instruct.jsonl'

# 执行筛选任务
filter_matching_entries(file1_path, file2_path, output_path)
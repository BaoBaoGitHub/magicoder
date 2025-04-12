import json

# 定义函数来读取jsonl文件并提取instruction和response字段
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                json_obj = json.loads(line)
                # 检查是否存在instruction和response字段
                if 'instruction' in json_obj and 'response' in json_obj:
                    data.append({
                        'instruction': json_obj['instruction'],
                        'response': json_obj['response']
                    })
                else:
                    print(f"缺少字段 in {file_path}: {line.strip()}")
            except json.JSONDecodeError:
                print(f"无效的JSON in {file_path}: {line.strip()}")
    return data

# 输入文件路径
file1 = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/merged_api_and_batch.jsonl'
file2 = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/extracted_questions_and_answers_compatible.jsonl'

# 读取两个文件的数据
data1 = read_jsonl(file1)
data2 = read_jsonl(file2)

# 合并数据
merged_data = data1 + data2

# 输出文件路径
output_file = '/home/baoxuanlin/graduation/new_merged.jsonl'

# 将合并后的数据写入新文件
with open(output_file, 'w', encoding='utf-8') as file:
    for item in merged_data:
        file.write(json.dumps(item) + '\n')

print(f"合并完成，结果已保存到 {output_file}")
import json

def filter_and_count_entries(file_path, output_file_path):
    count = 0
    # 同时打开输入文件和输出文件
    with open(file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                # 解析每行的 JSON 数据
                data = json.loads(line.strip())
                # 提取 content 字段
                content = data['response']['body']['choices'][0]['message']['content']
                # 检查是否包含“低质量”或“中质量”
                if "低质量" not in content and "中质量" not in content:
                    count += 1
                    # 将符合条件的条目写入新文件
                    outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"警告: 跳过无效的行 - {e}")
    return count

# 指定文件路径
file_path = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/data_judgement_result_from_deepseekr1.jsonl'
output_file_path = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/data_judgement_result_from_deepseekr1_filter_low.jsonl'

# 执行统计并输出结果
result = filter_and_count_entries(file_path, output_file_path)
print(f"没有出现'低质量'或'中质量'的条目数量: {result}")
print(f"符合条件的条目已保存到: {output_file_path}")
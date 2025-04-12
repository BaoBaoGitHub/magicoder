import json

def filter_high_quality_entries(input_file, output_file):
    # 打开输入文件和输出文件
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                # 解析 JSON 行
                data = json.loads(line.strip())
                # 提取 content 字段
                content = data['response']['body']['choices'][0]['message']['content']
                # 统计“高质量”出现次数
                count = content.count("高质量")
                # 如果出现 2 次及以上，写入新文件
                if count >= 2:
                    outfile.write(line)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                # 跳过无效行并打印警告
                print(f"警告: 跳过无效的行 - {e}")
                continue

# 文件路径
input_file = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/data_judgement_result_from_deepseekr1_filter_low.jsonl'
output_file = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/seed_data_for_evol_instruct.jsonl'

# 执行筛选并保存结果
filter_high_quality_entries(input_file, output_file)
print(f"筛选完成，种子数据已保存到: {output_file}")
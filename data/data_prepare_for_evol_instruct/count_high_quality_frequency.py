import json
from collections import Counter

def analyze_high_quality_occurrences(file_path):
    # 存储每行“高质量”出现次数的列表
    occurrence_counts = []
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # 解析 JSON 行
                data = json.loads(line.strip())
                # 提取 content 字段
                content = data['response']['body']['choices'][0]['message']['content']
                # 统计“高质量”出现次数
                count = content.count("高质量")
                occurrence_counts.append(count)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"警告: 跳过无效的行 - {e}")
                continue
    
    # 统计不同出现次数的分布
    count_distribution = Counter(occurrence_counts)
    
    # 输出分布结果
    print("“高质量”出现次数的分布:")
    for count, num_entries in sorted(count_distribution.items()):
        print(f"出现 {count} 次的条目数量: {num_entries}")
    
    # 计算并输出总次数
    total_high_quality = sum(occurrence_counts)
    print(f"\n“高质量”出现的总次数: {total_high_quality}")

# 文件路径
file_path = '/home/baoxuanlin/graduation/magicoder/data/data_for_evol_instruct/data_judgement_result_from_deepseekr1_filter_low.jsonl'

# 执行分析
analyze_high_quality_occurrences(file_path)
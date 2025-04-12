"""
之前有很多数据都是拿代码跑的，现在合并一下"""

import jsonlines
import os

# 设置输入文件夹路径和输出文件路径
input_dir = '/home/baoxuanlin/graduation/magicoder/data/generate_data/oss_instruct/'
output_path = '/home/baoxuanlin/graduation/magicoder/data/merged_data.jsonl'

# 存储合并后的数据
merged_data = []

# 当前行号，从 0 开始
current_index = 0

# 遍历目录中的所有文件
for filename in os.listdir(input_dir):
    if filename.endswith('.jsonl'):
        # 只处理以 .jsonl 结尾的文件
        file_path = os.path.join(input_dir, filename)
        
        # 提取文件中的 datanum 和 rawindex
        try:
            parts = filename.split('-')
            datanum = parts[1]  # 假设 datanum 是第二个部分
            rawindex = parts[2].split('.')[0]  # 假设 rawindex 是第三个部分并去掉扩展名
        except IndexError:
            print(f"Skipping invalid filename format: {filename}")
            continue
        
        # 读取每个文件的内容
        with jsonlines.open(file_path) as reader:
            for line in reader:
                # 修改 raw_index 为 datanum_rawindex
                line['raw_index'] = f"{datanum}_{rawindex}"
                
                # 添加当前行号作为 index
                line['index'] = current_index
                
                # 增加到合并后的数据中
                merged_data.append(line)
                
                # 行号加 1
                current_index += 1

# 将合并后的数据写入新文件
with jsonlines.open(output_path, mode='w') as writer:
    writer.write_all(merged_data)

print(f"Finished merging files. Output saved to {output_path}.")

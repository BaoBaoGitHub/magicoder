import json
import random

def generate_unique_custom_id(existing_ids):
    """
    生成一个唯一的 custom_id，格式为 datanum_虚拟数字。
    虚拟数字是 100000 到 999999 之间的随机数。
    """
    while True:
        virtual_number = random.randint(100000, 999999)
        new_custom_id = f"datanum_{virtual_number}"
        if new_custom_id not in existing_ids:
            return new_custom_id

def process_file(input_file, output_file):
    """
    处理 JSONL 文件，修改重复的 custom_id。
    """
    # 用于存储所有 custom_id（包括原始和修改后的）
    all_custom_ids = set()
    # 存储处理后的数据
    processed_data = []

    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                # 解析每一行 JSON 数据
                entry = json.loads(line.strip())
                custom_id = entry.get('custom_id', 'unknown')
                
                # 如果 custom_id 已存在，生成新的 custom_id
                if custom_id in all_custom_ids:
                    new_custom_id = generate_unique_custom_id(all_custom_ids)
                    entry['custom_id'] = new_custom_id
                    all_custom_ids.add(new_custom_id)
                else:
                    all_custom_ids.add(custom_id)
                
                # 添加到处理后的数据列表
                processed_data.append(entry)
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
            except Exception as e:
                print(f"处理数据时出错: {e}")

    # 将处理后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for entry in processed_data:
            outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"处理完成，原始数据量: {len(processed_data)}, 其中重复条目已修改 custom_id")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    # 输入和输出文件路径（根据实际路径修改）
    input_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/transformed_data.jsonl'
    output_file = 'transformed_data_unique.jsonl'
    
    # 执行文件处理
    process_file(input_file, output_file)
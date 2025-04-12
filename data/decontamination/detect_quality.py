import json

def transform_data(entry):
    # 从原始数据中提取需要的字段，默认值处理空字段
    custom_id = entry.get('raw_index', 'unknown')  # 使用 raw_index 作为 custom_id
    instruction = entry.get('instruction', '')     # 提取 instruction，默认空字符串
    response = entry.get('response', '')           # 提取 response，默认空字符串
    
    # 定义 content 的字符串模板
    content_template = (
        "该问题和答案对的质量属于哪个水平？是高质量、中质量还是低质量？从这三个选项中选择一个。"
        "问题：\n\n{instruction}\n\n答案：\n\n{response}"
    )
    
    # 使用模板拼接 instruction 和 response
    content = content_template.format(instruction=instruction, response=response)
    
    # 构建新的 JSON 对象
    new_entry = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "deepseek-r1",
            "messages": [{
                "role": "user",
                "content": content
            }]
        }
    }
    return new_entry

def process_file(input_file, output_file):
    # 打开输入文件和输出文件
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                # 解析每一行的 JSON 数据
                entry = json.loads(line.strip())
                # 转换数据格式
                new_entry = transform_data(entry)
                # 将转换后的 JSON 对象写入新文件，每行一个 JSON
                outfile.write(json.dumps(new_entry, ensure_ascii=False) + '\n')
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
            except Exception as e:
                print(f"处理数据时出错: {e}")

if __name__ == "__main__":
    # 定义输入和输出文件路径
    input_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_merged_final.jsonl'
    output_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/transformed_data.jsonl'
    
    # 执行文件处理
    process_file(input_file, output_file)
    print(f"数据转换完成，已生成文件: {output_file}")
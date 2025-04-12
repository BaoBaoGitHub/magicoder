#!/usr/bin/env python3
import json

input_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/merged_api_and_batch_fixed.jsonl'
output_file = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/merged_api_and_batch_fixed_instruction_response.jsonl'

with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
    for line in fin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"解析JSON出错: {e}")
            continue
        
        # 提取 instruction 和 response 字段
        new_data = {
            "instruction": data.get("instruction"),
            "response": data.get("response")
        }
        
        fout.write(json.dumps(new_data, ensure_ascii=False) + "\n")

print(f"处理完成，结果保存在: {output_file}")

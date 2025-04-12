"""批量调用生成的数据中，没有seed_code部分，所以在这里补齐一下"""

import jsonlines
import os

# 设置路径
batch_inference_path = '/home/baoxuanlin/graduation/magicoder/data/batch_inference_result/batch_inference_gengerate_data.jsonl'
jsonl_output_dir = '/home/baoxuanlin/code/codematcher-demo/jsonl_output'

# 存储更新后的数据
updated_data = []

# 读取 batch_inference_gengerate_data.jsonl 文件
with jsonlines.open(batch_inference_path) as reader:
    for line in reader:
        # 获取 custom_id，格式为 "datanum1_num2"
        custom_id = line.get('custom_id')
        if custom_id:
            datanum1, num2 = custom_id.split('_')
            num2 = int(num2)  # 转换为整数

            # 根据 datanum1 构建对应的 jsonl 文件路径
            data_jsonl_path = os.path.join(jsonl_output_dir, f"{datanum1}.jsonl")
            
            # 确保文件存在
            if os.path.exists(data_jsonl_path):
                with jsonlines.open(data_jsonl_path) as data_reader:
                    # 读取指定的 num2 行
                    for idx, data_line in enumerate(data_reader):
                        if idx == num2:
                            content = data_line.get('content')
                            if content:
                                # 更新 batch_inference_gengerate_data 中的 seed_code 属性
                                line['seed_code'] = content
                            break
            else:
                print(f"Warning: File {data_jsonl_path} does not exist.")
        
        # 将更新后的行添加到列表
        updated_data.append(line)

# 将更新后的数据写回到新的文件
output_path = '/home/baoxuanlin/graduation/magicoder/data/batch_inference_result/updated_batch_inference_gengerate_data.jsonl'
with jsonlines.open(output_path, mode='w') as writer:
    writer.write_all(updated_data)

print(f"Finished updating the batch_inference_gengerate_data file. Output saved to {output_path}.")

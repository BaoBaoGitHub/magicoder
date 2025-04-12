import jsonlines
import os

# 设置路径
batch_inference_path = '/home/baoxuanlin/graduation/magicoder/data/batch_inference_result/batch_inference_gengerate_data.jsonl'
jsonl_output_dir = '/home/baoxuanlin/code/codematcher-demo/jsonl_output'

# 存储更新后的数据
updated_data = []

# 缓存文件内容
file_cache = None
cached_file = None

# 读取 batch_inference_gengerate_data.jsonl 文件
with jsonlines.open(batch_inference_path) as reader:
    for line in reader:
        # 获取 custom_id，格式为 "datanum1_num2"
        custom_id = line.get('custom_id')
        print(custom_id)
        if custom_id:
            datanum1, num2 = custom_id.split('_')
            num2 = int(num2)  # 转换为整数

            # 如果当前处理的文件与上次缓存的文件不同，读取新文件
            if datanum1 != cached_file:
                cached_file = datanum1
                file_cache = []  # 清空缓存
                
                # 根据 datanum1 构建对应的 jsonl 文件路径
                data_jsonl_path = os.path.join(jsonl_output_dir, f"{datanum1}.jsonl")
                
                # 如果文件存在，缓存文件内容
                if os.path.exists(data_jsonl_path):
                    with jsonlines.open(data_jsonl_path) as data_reader:
                        for data_line in data_reader:
                            file_cache.append(data_line)
                else:
                    print(f"Warning: File {data_jsonl_path} does not exist.")

            # 获取缓存中的内容
            if 0 <= num2 < len(file_cache):
                content = file_cache[num2].get('content')
                if content:
                    # 更新 batch_inference_gengerate_data 中的 seed_code 属性
                    line['seed_code'] = content

        # 将更新后的行添加到列表
        updated_data.append(line)

# 将更新后的数据写回到新的文件
output_path = '/home/baoxuanlin/graduation/magicoder/data/batch_inference_result/updated_batch_inference_gengerate_data.jsonl'
with jsonlines.open(output_path, mode='w') as writer:
    writer.write_all(updated_data)

print(f"Finished updating the batch_inference_gengerate_data file. Output saved to {output_path}.")

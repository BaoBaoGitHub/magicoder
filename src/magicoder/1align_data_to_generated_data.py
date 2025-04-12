import jsonlines
import random
import os

# 设置路径
input_path = '/home/baoxuanlin/graduation/magicoder/data/batch_inference_result/updated_batch_inference_gengerate_data.jsonl'
output_path = '/home/baoxuanlin/graduation/magicoder/data/processed_batch_inference_data.jsonl'

def parse_problem_solution(response_text: str) -> tuple[str, str] | None:
    """
    解析问题及其解决方案。
    
    Args:
        response_text (str): 包含问题和解决方案的文本。
    
    Returns:
        tuple[str, str] | None: 返回一个包含问题和解决方案的元组，
                                如果无法解析，则返回 None。
    
    """
    lines = response_text.splitlines(keepends=True)
    problem_start_index: int | None = None
    solution_start_index: int | None = None
    for idx, line in enumerate(lines):
        if "[problem description]" in line.lower() and problem_start_index is None:
            problem_start_index = idx
        if "[solution]" in line.lower() and solution_start_index is None:
            solution_start_index = idx
    if problem_start_index is None or solution_start_index is None:
        return None
    if problem_start_index >= solution_start_index:
        return None
    problem = "".join(lines[problem_start_index + 1 : solution_start_index]).strip()
    solution = "".join(lines[solution_start_index + 1 :]).strip()
    return problem, solution


# 存储更新后的数据
processed_data = []

# 读取 updated_batch_inference_gengerate_data.jsonl 文件
with jsonlines.open(input_path) as reader:
    for index, line in enumerate(reader):
        custom_id = line.get('custom_id')
        seed_code = line.get('seed_code')
        response = line.get('response', {})
        
        # 提取 reasoning_content
        reasoning_content = response.get('body', {}).get('choices', [{}])[0].get('message', {}).get('reasoning_content', '')
        
        # 提取 content 并解析
        content = response.get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
        
        parsed = parse_problem_solution(content)
        
        if parsed:
            problem, solution = parsed
            # 生成 openai_fingerprint
            openai_fingerprint = random.randint(100000000, 999999999)
            
            # 准备新的一行
            processed_line = {
                "raw_index": custom_id,
                "index": index,
                "seed": seed_code,
                "openai_fingerprint": openai_fingerprint,
                "problem": problem,
                "solution": solution,
                "reasoning_content": reasoning_content
            }
            
            # 添加到 processed_data 列表
            processed_data.append(processed_line)

# 将更新后的数据写入新的 jsonl 文件
with jsonlines.open(output_path, mode='w') as writer:
    writer.write_all(processed_data)

print(f"Finished processing the data. Output saved to {output_path}.")

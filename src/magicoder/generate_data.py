import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from datasets import Dataset, load_dataset
from tqdm.auto import tqdm
from transformers import HfArgumentParser

import magicoder

# DO NOT CHANGE THE FOLLOWING
SYSTEM = "You are exceptionally skilled at crafting high-quality programming problems and offering precise solutions."
ERROR_MARGIN = 10


@dataclass(frozen=True)
class Args:
    seed_code_start_index: int
    # `seed_code_start_index` + `max_new_data` is the last-to-end seed code index
    max_new_data: int
    continue_from: str | None = field(default=None)

    # Keep the following arguments unchanged for reproducibility
    # seed: int = field(default=976)
    seed: int = field(default=random.randint(1, pow(2, 31) - 1))

    temperature: float = field(default=0.0)
    # todo model: str = field(default="gpt-3.5-turbo-1106")
    model: str = field(default="deepseek-r1")
    model_max_tokens: int = field(default=8192)
    # max_new_tokens: int = field(default=2500)
    max_new_tokens: int = field(default=4096)

    min_lines: int = field(default=1)
    max_lines: int = field(default=15)
    chunk_size: int = field(default=1000)

    dataset_name: str = field(default="bigcode/starcoderdata")
    # data_dir: str | None = field(default="python")
    data_dir: str | None = field(default=None)
    # max_considered_data: int | None = field(default=150000)
    max_considered_data: int | None = field(default=100000)

    stream: bool = field(default=True)

    tag: str = field(
        default="",
        metadata={
            "help": "Custom tag as part of the output filename, not affecting the fingerprint"
        },
    )

    def fingerprint(self, prompt_template: str) -> str:
        """
        计算基于给定 prompt_template 的指纹值。
        
        Args:
            prompt_template (str): 模板字符串，用于生成指纹值。
        
        Returns:
            str: 计算出的指纹值。
        
        """
        # The combination of arguments can uniquely determine the generation process
        args = (
            self.seed,
            self.temperature,
            self.model,
            self.model_max_tokens,
            self.min_lines,
            self.max_lines,
            self.chunk_size,
            self.dataset_name,
            self.data_dir,
            self.max_considered_data,
            prompt_template,
            SYSTEM,
            ERROR_MARGIN,
        )
        return magicoder.utils.compute_fingerprint(*args, hash_length=5)


def map_dataset(examples: dict, indices: list[int], args: Args) -> dict:
    """
    对给定的数据集进行映射。
    
    Args:
        examples (dict): 包含多个数据项的字典，每个数据项包含"content"键，对应的数据值为字符串。
        indices (list[int]): 一个整数列表，表示需要映射的数据项的索引。
        args (Args): 一个包含各种参数的Args对象，其中包括seed（随机种子）。
    
    Returns:
        dict: 一个包含映射后数据的字典，包含两个键："seed"和"raw_index"。
            - "seed"：一个列表，包含从examples中根据indices映射出的seed代码段。
            - "raw_index"：一个列表，包含原始indices。
    
    """
    random.seed(args.seed + indices[0])
    seed_snippets = [
        extract_seed_code(args, content) for content in examples["content"]
    ]
    return {
        "seed": seed_snippets,
        "raw_index": indices,
    }


def extract_seed_code(args: Args, document: str) -> str:
    """
    从文档中提取种子代码。
    
    Args:
        args (Args): 参数对象，包含最小行数（min_lines）和最大行数（max_lines）等参数。
        document (str): 原始文档字符串。
    
    Returns:
        str: 从文档中随机提取的一段代码字符串。
    
    """
    lines = document.splitlines(keepends=True)
    start_index = random.choice(range(len(lines)))
    n_lines_to_consider = random.randint(args.min_lines, args.max_lines)
    code = "".join(lines[start_index : start_index + n_lines_to_consider])
    return code


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


def main():
    # 解析命令行参数
    args, *_ = cast(
        tuple[Args, ...], HfArgumentParser(Args).parse_args_into_dataclasses()
    )

    # 根据参数设置数据集的拆分方式
    # split = (
    #     f"train[:{args.max_considered_data}]"
    #     if args.max_considered_data is not None
    #     else "train"
    # )
    split = "train" # 不搞乱七八糟的，直接就是train

    # 断言OpenAI客户端不为空
    assert magicoder.utils.OPENAI_CLIENT is not None

    # 加载数据集
    # dataset: Dataset = load_dataset(
    #     args.dataset_name,
    #     data_dir=args.data_dir,
    #     split=split,
    #     num_proc=magicoder.utils.N_CORES,
    # )

    # 加载本地数据集
    dataset: Dataset = load_dataset(
        "json",
        data_files=args.dataset_name,
        split=split,
        num_proc=magicoder.utils.N_CORES,
    )

    # 设置随机种子
    random.seed(args.seed)
    # 把args.seed输出到args.dataset_name相同文件夹下的data0_seed.jsonl文件中，其实这行代码也可以处理json
    seed_save_file = args.dataset_name.replace(".json", "_seed.json")
    with open(seed_save_file, "w") as f:
        json.dump({"seed": args.seed}, f)
    

    # 对数据集进行映射处理
    # map_fn = get_map_dataset(args)
    dataset = dataset.map(
        function=map_dataset,
        fn_kwargs=dict(args=args),
        with_indices=True,
        batched=True,
        batch_size=args.chunk_size,
    )

    # 打乱数据集
    dataset = dataset.shuffle(seed=args.seed)

    # 为每个数据项添加索引
    dataset = dataset.map(lambda _, index: {"index": index}, with_indices=True)

    # 确保每次运行都生成相同的数据，除非默认参数发生变化
    start_index = args.seed_code_start_index
    end_index = min(start_index + args.max_new_data, len(dataset))
    # TODO 其实一个文件比如data0执行了好多次，所以seed文件的值被覆盖好多次了，那么数据不再正确
    # 1️⃣ 读取原始 JSON 文件
    with open(seed_save_file, "r") as f:
        data = json.load(f)  # 加载为字典

    # 2️⃣ 检查是否已有相同字段，若有则覆盖
    data["start_index"] = start_index
    data["end_index"] = end_index

    # 3️⃣ 重新写入文件（覆盖写入）
    with open(seed_save_file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # 因为这里的dataset已经是打乱了，所以这里虽然选择了一些数据，但是其实本质上是随机的
    dataset = dataset.select(range(start_index, end_index))

    # 读取提示模板
    prompt_template = Path("data/prompt.txt").read_text()

    # 获取时间戳
    timestamp = magicoder.utils.timestamp()

    # 生成数据指纹
    data_fingerprint = args.fingerprint(prompt_template)

    # 检查是否从旧数据继续
    if args.continue_from is not None:
        assert data_fingerprint in args.continue_from, "Fingerprint mismatch"
        assert f"{start_index}_{end_index}" in args.continue_from, "Index mismatch"
        old_path = Path(args.continue_from)
        assert old_path.exists()
        old_data = magicoder.utils.read_jsonl(old_path)
        assert len(old_data) > 0
        last_index = old_data[-1]["index"]
        n_skipped = last_index - start_index + 1
        print("Continuing from", old_path)
        f_out = old_path.open("a")
    else:
        # 生成新的输出路径
        tag = "" if args.tag == "" else f"-{args.tag}"
        path = Path(
            f"data{tag}-{data_fingerprint}-{start_index}_{end_index}-{timestamp}.jsonl"
        )
        assert not path.exists()
        f_out = path.open("w")
        print("Saving to", path)
        n_skipped = 0

    # 遍历数据集，处理每个数据项
    for index, example in enumerate(tqdm(dataset)):
        if index < n_skipped:
            continue
        assert index + start_index == example["index"]
        
        time.sleep(random.randint(10, 30)) # 每次调用前建议等一下，不然怕被查

        # 生成提示
        prompt = prompt_template.format(code=example["seed"])

        # 确保生成的内容在模型的上下文大小范围内
        max_new_tokens = min(
            args.max_new_tokens,
            args.model_max_tokens
            # TODO 偷懒不计算输入prompt的token
            # - magicoder.utils.num_tokens_from_string(prompt, args.model)
            # 误差裕量（例如，由于对话标记）
            - ERROR_MARGIN,
        )
        if max_new_tokens <= 0:
            continue

        # 构造与OpenAI交互的消息
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ]

        openai_seed = args.seed + example["index"]

        """ error_cnt = 0
        # 生成响应
        while error_cnt < args.max_retries:
            response = magicoder.utils.chat_completions_with_backoff(
                model=args.model,
                messages=messages,
                max_tokens=max_new_tokens,
                n=1,
                temperature=args.temperature,
                # seed=openai_seed,  个人认为这里不需要seed，反而影响效果
                # 提问经常超时，用stream解决
                stream=args.stream,    
            )

            # 推理过程
            reasoning_content = ""
            is_answering = False   # 判断是否结束思考过程并开始回复

            if args.stream:
                print("[Streaming]")
                # 聚合流式响应的内容
                complete_response = ""
                for chunk in response:
                    # 假设每个chunk中，chunk.choices[0].delta.content包含新生成的文本
                    delta = chunk.choices[0].delta

                    # 检查是否有reasoning_content属性
                    if not hasattr(delta, 'reasoning_content'):
                        continue

                    # 处理空内容情况
                    if not getattr(delta, 'reasoning_content', None) and not getattr(delta, 'content', None):
                        continue

                    # 处理开始回答的情况
                    if not getattr(delta, 'reasoning_content', None) and not is_answering:
                        # print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                        is_answering = True

                    # 处理思考过程
                    if getattr(delta, 'reasoning_content', None):
                        # print(delta.reasoning_content, end='', flush=True)
                        reasoning_content += delta.reasoning_content
                    # 处理回复内容
                    elif getattr(delta, 'content', None):
                        # print(delta.content, end='', flush=True)
                        complete_response += delta.content

                # 如果没有生成内容，则跳过该样本
                if not complete_response:
                    print("[Warning] No content received in streamed response.")
                    continue

                # 开启流式下，解析问题和解决方案
                parsing_result = parse_problem_solution(complete_response)
                if parsing_result is None:
                    print("[Warning] Failed to parse response:", complete_response)
                    continue

            else:
                # 检查响应是否完成
                choice = response.choices[0]
                if choice.finish_reason != "stop":
                    print("[Warning] Response incomplete:", choice.finish_reason)
                    continue

                # 解析问题和解决方案
                parsing_result = parse_problem_solution(choice.message.content)
            
                if parsing_result is None:
                    print("[Warning] Failed to parse response:", choice.message.content)
                    continue """
        
        success = False
        parsing_result = None
        complete_response = ""
        reasoning_content = ""
        
        try:
            response = magicoder.utils.chat_completions_with_backoff(
                model=args.model,
                messages=messages,
                max_tokens=max_new_tokens,
                n=1,
                temperature=args.temperature,
                stream=args.stream,    
            )
        
            if args.stream:
                # print("[Streaming]")
                # complete_response = ""
                # reasoning_content = ""
                is_answering = False   # 判断是否开始回答
                last_finish_reason = None
                # 遍历流式返回的每个 chunk
                for chunk in response:    
                    # 如果当前 chunk 包含 finish_reason，就记录下来（通常只有最后一个 chunk 会有）
                    if getattr(chunk.choices[0], "finish_reason",None):
                        last_finish_reason = chunk.choices[0].finish_reason
                    
                    delta = chunk.choices[0].delta
                    # 处理推理过程文本
                    if getattr(delta, 'reasoning_content',None):
                        reasoning_content += delta.reasoning_content
                    # 处理回复内容
                    else:
                        if getattr(delta, 'content',None):
                            if is_answering == False:
                                is_answering = True
                            complete_response += delta.content
                
                # 判断生成是否是自然结束（"stop"）还是因为截断或其他原因
                if last_finish_reason != "stop":
                    raise Exception(f"Streaming ended with finish_reason: {last_finish_reason} (not natural stop)")
                parsing_result = parse_problem_solution(complete_response)

            else:
                choice = response.choices[0]
                if choice.finish_reason != "stop":
                    raise Exception("Response incomplete: " + str(choice.finish_reason))
                parsing_result = parse_problem_solution(choice.message.content)
            
            if parsing_result is None:
                    raise Exception("Failed to parse streamed response.")
            problem, solution = parsing_result
            if len(problem) == 0 or len(solution) == 0:
                print("[Warning] Empty problem or solution:", last_response_content)
                continue
            
            # 如果执行到这里，说明API调用和解析都成功
            success = True
        except Exception as e:
            print(f"[error] API call failed: {e}")
            # 已经在每一次调用的时候随机等待一段时间了
            continue

        

        if not success:
            continue  # 跳过当前样本
        
        # 获取大模型响应指纹
        # fingerprint = response.system_fingerprint
        # 用阿里云调用deepseek r1的response没有指纹，所以这里生成一个随机数就可以
        fingerprint = "counterfeit " + str(random.randint(0, pow(2,31)-1))
        assert fingerprint is not None

        # 构造输出数据
        # 在这个字典中，seed指的是“种子代码片段”
        data = dict(
            raw_index=example["raw_index"],
            index=example["index"],
            seed=example["seed"],
            openai_fingerprint=fingerprint,
            problem=problem,
            solution=solution,
            reasoning_content=reasoning_content, # r1模型的推理过程
        )

        # print(reasoning_content)

        # 打印问题和解决方案
        # print("[Problem Description]", problem, sep="\n", end="\n\n")
        # print("[Solution]", solution, sep="\n")

        # 将数据写入文件
        f_out.write(json.dumps(data) + "\n")
        # 直接刷新进硬盘
        f_out.flush()


if __name__ == "__main__":
    main()

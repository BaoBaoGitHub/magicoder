import functools
import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TypeVar

import openai
import tiktoken

N_CORES = 1 if (count := os.cpu_count()) is None or count == 0 else count // 2


def read_jsonl(path: str | Path) -> list[Any]:
    """Read lines of JSON from a file (including '\n')."""
    with Path(path).open("r") as f:
        return [json.loads(line) for line in f]


def write_jsonl(path: str | Path, data: Sequence[Mapping]):
    # cannot use `dict` here as it is invariant
    with Path(path).open("w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


# def reformat_python(code: str) -> str | None:
#     """Reformat Python code using Black."""

#     try:
#         return black.format_str(code, mode=black.Mode())
#     except Exception:
#         return None


_T = TypeVar("_T")


def chunked(seq: Sequence[_T], n: int) -> Iterable[Sequence[_T]]:
    """Yield successive n-sized chunks from seq."""
    return (seq[i : i + n] for i in range(0, len(seq), n))


# OpenAI API access
# Use environment variables!
# openai.organization = "org-pQ4H2mEb8OUHqSkIkP8b50k6"
# openai.api_key = os.getenv("OPENAI_API_KEY")


def retry_with_exponential_backoff(
    errors: tuple,
    initial_delay: float = 30,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 1, #重试一次就行了，不然重试太多了
):
    """
    重试函数，使用指数退避策略。
    
    Args:
        errors (tuple): 需要重试的错误类型元组。
        initial_delay (float, optional): 初始延迟时间，以秒为单位。默认为30秒。
        exponential_base (float, optional): 指数退避的底数。默认为2。
        jitter (bool, optional): 是否在退避时间中添加抖动。默认为True。
        max_retries (int, optional): 最大重试次数。默认为5次。
    
    Returns:
        function: 返回一个装饰器，该装饰器会重试被装饰的函数。
    
    """
    """Retry a function with exponential backoff."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 初始化变量
            num_retries = 0
            delay = initial_delay

            # 循环直到成功响应或达到最大重试次数或引发异常
            while True:
                try:
                    return func(*args, **kwargs)
                # 对特定错误进行重试
                except errors as e:
                    print(f"Error: {e}. Retrying in {delay} seconds...")
                    # 增加重试次数
                    num_retries += 1
                    # 检查是否已达到最大重试次数
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )
                    # 增加延迟
                    delay *= exponential_base * (1 + jitter * random.random())
                    # 休眠指定的延迟时间
                    time.sleep(delay)
                    # time.sleep(60)
                # 对未指定的任何错误引发异常
                except Exception as e:
                    raise e

        return wrapper

    return decorator


ERRORS = (
    openai.RateLimitError,
    openai.APIError,
    openai.APIConnectionError,
    openai.InternalServerError,
)

try:
    OPENAI_CLIENT: openai.OpenAI | None = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), 
        base_url=os.getenv(key="OPENAI_BASE_URL"),
    )
except openai.OpenAIError:
    OPENAI_CLIENT = None


@retry_with_exponential_backoff(ERRORS)
def chat_completions_with_backoff(*args, **kwargs):
    """
    使用回退机制进行聊天补全请求。
    
    Args:
        *args: 可变参数列表，用于传递给 OPENAI_CLIENT.chat.completions.create 的位置参数。
        **kwargs: 关键字参数，用于传递给 OPENAI_CLIENT.chat.completions.create 的关键字参数。
    
    Returns:
        返回 OPENAI_CLIENT.chat.completions.create 的结果。
    
    Raises:
        AssertionError: 如果 OPENAI_CLIENT 未被初始化。
    
    """
    assert OPENAI_CLIENT is not None
    return OPENAI_CLIENT.chat.completions.create(*args, **kwargs)


@retry_with_exponential_backoff(ERRORS)
def completions_with_backoff(*args, **kwargs):
    assert OPENAI_CLIENT is not None
    return OPENAI_CLIENT.completions.create(*args, **kwargs)


# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = None
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Warning: Model {model} not found in tiktoken registry. Using 'cl100k_base' as fallback.")
        encoding = tiktoken.get_encoding("cl100k_base")  # 手动指定编码器
    # encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def compute_fingerprint(*args: Any, hash_length: int | None = None) -> str:
    combined = "".join(map(str, args))
    content = hashlib.sha256(combined.encode()).hexdigest()
    if hash_length is not None:
        content = content[:hash_length]
    return content

import json
import random
import re
from typing import List, Dict, Tuple, Pattern
import logging
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 预编译正则表达式
GENERIC_TYPE_PATTERN: Pattern = re.compile(r'\<[A-Z][a-zA-Z0-9]*\>')
ANNOTATION_PATTERN: Pattern = re.compile(r'@[A-Za-z]+')

# 优化后的主题和关键词
TOPICS: Dict[str, List[Tuple[str | Pattern, bool]]] = {
    'OOP': [
        ('class', False), ('object', False), ('inheritance', False), ('extends', False),
        ('implements', False), ('abstract', False), ('interface', False), ('encapsulation', False),
        ('polymorphism', False), ('override', False)
    ],
    'Exceptions': [
        ('try', False), ('catch', False), ('throw', False), ('exception', False),
        ('error', False), ('finally', False), ('throws', False)
    ],
    'Collections': [
        ('list', False), ('set', False), ('map', False), ('ArrayList', False),
        ('HashMap', False), ('iterator', False), ('Collections', False)
    ],
    'I/O': [
        ('File', False), ('InputStream', False), ('OutputStream', False),
        ('BufferedReader', False), ('FileInputStream', False)
    ],
    'Concurrency': [
        ('Thread', False), ('Runnable', False), ('synchronized', False),
        ('Lock', False), ('ExecutorService', False), ('Future', False)
    ],
    'Generics': [
        ('generic', False), (GENERIC_TYPE_PATTERN, True), ('wildcard', False),
        ('extends', False), ('super', False)
    ],
    'Lambdas and Streams': [
        ('lambda', False), ('stream', False), ('Function', False),
        ('Predicate', False), ('map', False), ('filter', False)
    ],
    'Annotations': [
        ('annotation', False), (ANNOTATION_PATTERN, True), ('Override', False),
        ('Deprecated', False), ('SuppressWarnings', False)
    ],
    'JDBC': [
        ('Connection', False), ('PreparedStatement', False), ('ResultSet', False),
        ('DriverManager', False), ('sql', False)
    ],
    'Basics': [
        ('int', False), ('static', False), ('final', False), ('enum', False),
        ('package', False), ('if', False), ('else', False), ('for', False),
        ('while', False), ('switch', False)
    ]
}

# 复杂性主题集合
HIGH_COMPLEXITY_TOPICS = set(['Concurrency', 'Generics', 'Lambdas and Streams', 'Annotations', 'JDBC'])
MEDIUM_COMPLEXITY_TOPICS = set(['OOP', 'Exceptions', 'Collections', 'I/O'])
LOW_COMPLEXITY_TOPICS = set(['Basics'])

def has_any_keyword(text: str, keyword_list: List[Tuple[str | Pattern, bool]]) -> bool:
    """
    检查文本是否包含关键词列表中的任何关键词，支持正则和精确匹配。

    Args:
        text (str): 要检查的文本。
        keyword_list (List[Tuple[str | Pattern, bool]]): 关键词列表，每个元素为(keyword, is_regex)。

    Returns:
        bool: 如果文本包含任一关键词返回True，否则返回False。
    """
    for keyword, is_regex in keyword_list:
        if is_regex and isinstance(keyword, Pattern):
            if keyword.search(text):
                return True
        else:
            if re.search(r'\b' + re.escape(str(keyword)) + r'\b', text):
                return True
    return False

def assign_topics(entry: Dict) -> List[str]:
    """
    根据指令和种子文本分配主题。

    Args:
        entry (Dict): 数据条目，包含'instruction_lower'和'seed_lower'字段。

    Returns:
        List[str]: 分配的主题列表。
    """
    text = entry['instruction_lower'] + ' ' + entry['seed_lower']
    return [topic for topic, keywords in TOPICS.items() if has_any_keyword(text, keywords)]

def determine_complexity(entry: Dict) -> str:
    """
    根据主题和代码特征确定复杂性等级。

    Args:
        entry (Dict): 数据条目，包含'topics'字段，可能包含'response'字段。

    Returns:
        str: 复杂性等级，可能是'high'、'medium'、'low'或'unknown'。
    """
    topics = entry['topics']
    code = entry.get('response', '')
    # 特征提取
    code_lines = len(code.split('\n'))
    nested_loops = code.count('for') > 1 or code.count('while') > 1
    method_calls = code.count('(')  # 简化的方法调用检测

    # 复杂性判断逻辑
    if any(topic in HIGH_COMPLEXITY_TOPICS for topic in topics) or (code_lines > 20 and nested_loops):
        return 'high'
    elif any(topic in MEDIUM_COMPLEXITY_TOPICS for topic in topics) or (code_lines > 10 and method_calls > 3):
        return 'medium'
    elif any(topic in LOW_COMPLEXITY_TOPICS for topic in topics):
        return 'low'
    return 'unknown'

def is_clear_and_complete(entry: Dict) -> bool:
    """
    检查条目是否清晰且完整。

    Args:
        entry (Dict): 数据条目，包含'instruction'和'response'字段。

    Returns:
        bool: 如果条目清晰且完整返回True，否则返回False。
    """
    instruction = entry.get('instruction', '')
    response = entry.get('response', '')
    if len(instruction) < 50:
        return False
    if not response or not any(keyword in response.lower() for keyword in ['public', 'private', 'protected', 'class', 'interface', 'method', 'void', 'int', 'double', 'string']):
        return False
    return True

def process_entry(line: str) -> Dict | None:
    """
    处理单行数据，返回过滤后的条目或None。

    Args:
        line (str): 数据集中的一行JSON字符串。

    Returns:
        Dict | None: 过滤后的条目，如果不符合条件返回None。
    """
    try:
        entry = json.loads(line)
        if entry.get('lang') != 'java':
            return None
        
        # 预处理文本
        entry['instruction_lower'] = entry.get('instruction', '').lower()
        entry['seed_lower'] = entry.get('seed', '').lower()
        
        if not is_clear_and_complete(entry):
            return None
        
        entry['topics'] = assign_topics(entry)
        entry['complexity'] = determine_complexity(entry)
        if entry['complexity'] not in ['medium', 'high']:
            return None
        
        return entry
    except json.JSONDecodeError as e:
        logger.warning(f"跳过无效的JSON行: {e}")
        return None

def load_and_filter_dataset(filename: str, max_workers: int = 4) -> List[Dict]:
    """
    流式加载并并行过滤数据集。

    Args:
        filename (str): 数据集文件名。
        max_workers (int): 并行处理的工作线程数，默认为4。

    Returns:
        List[Dict]: 过滤后的数据集。
    """
    filtered_data = []
    seen_instructions = set()
    
    with open(filename, 'r') as f:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(process_entry, f)
            for entry in results:
                if entry and entry['instruction_lower'] not in seen_instructions:
                    seen_instructions.add(entry['instruction_lower'])
                    filtered_data.append(entry)
    
    logger.info(f"过滤后数据量: {len(filtered_data)}")
    return filtered_data

def select_seed_dataset(filtered_data: List[Dict], size: int = 2500, seed: int = 42) -> List[Dict]:
    """
    从过滤后的数据中选择种子数据集。

    Args:
        filtered_data (List[Dict]): 过滤后的数据集。
        size (int): 种子数据集的目标大小，默认为2500。
        seed (int): 随机种子，默认为42。

    Returns:
        List[Dict]: 种子数据集。
    """
    random.seed(seed)
    if len(filtered_data) <= size:
        logger.info(f"数据量不足 {size}，返回全部数据: {len(filtered_data)}")
        return filtered_data
    return random.sample(filtered_data, size)

def main():
    """
    主函数，执行数据处理并保存结果。
    """
    filename = '/home/baoxuanlin/graduation/magicoder/data/decontamination/data/backup_merged_final.jsonl'
    try:
        filtered_data = load_and_filter_dataset(filename, max_workers=4)
        # seed_dataset = select_seed_dataset(filtered_data, size=2500, seed=42)
        
        # 保存种子数据集
        with open('seed_dataset.jsonl', 'w') as f:
            for entry in filtered_data:
                f.write(json.dumps(entry) + '\n')
        # logger.info(f"种子数据集已保存，数量: {len(seed_dataset)}")
    except FileNotFoundError:
        logger.error(f"文件未找到: {filename}")
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    main()
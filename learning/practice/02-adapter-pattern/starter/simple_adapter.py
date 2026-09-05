from typing import List, Dict, Callable
import json

class AdapterError(Exception):
    """适配器错误"""
    pass

class SimpleAdapter:
    """简化的模型适配器（用于学习）"""

    def __init__(self, api_key: str, *, model: str = "gpt-4o-mini", opener: Callable = None):
        # TODO: 验证 api_key 非空
        # TODO: 保存参数
        # TODO: 如果 opener 为 None，使用 urlopen
        pass

    def __call__(self, messages: List[Dict]) -> str:
        """
        发送消息到模型 API，返回文本响应

        步骤：
        1. 构造 JSON 请求体 {"model": ..., "messages": ...}
        2. 创建 HTTP POST 请求，添加 Authorization 头
        3. 调用 opener 发送请求
        4. 解析 JSON 响应
        5. 提取 choices[0].message.content
        6. 错误时抛出 AdapterError
        """
        # TODO: 实现适配器逻辑
        pass

from typing import List, Dict, Callable
import json
from urllib.request import Request, urlopen

class AdapterError(Exception):
    """适配器错误"""
    pass

class SimpleAdapter:
    """简化的模型适配器（参考实现）"""

    def __init__(self, api_key: str, *, model: str = "gpt-4o-mini", opener: Callable = None):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.model = model
        self._opener = opener if opener is not None else urlopen

    def __call__(self, messages: List[Dict]) -> str:
        # 1. 构造请求体
        payload = json.dumps({
            "model": self.model,
            "messages": messages
        }, ensure_ascii=False).encode("utf-8")

        # 2. 创建 HTTP 请求
        request = Request(
            url="https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        # 3. 发送请求并处理响应
        try:
            response = self._opener(request, timeout=30)
            raw_data = response.read()
            data = json.loads(raw_data.decode("utf-8"))

            # 4. 提取文本
            content = data["choices"][0]["message"]["content"]

            if not isinstance(content, str):
                raise AdapterError("response content is not a string")

            return content

        except KeyError as e:
            raise AdapterError(f"invalid response format: missing {e}") from e
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise AdapterError("failed to parse response") from e
        except Exception as e:
            raise AdapterError(f"request failed: {e}") from e

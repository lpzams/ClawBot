import unittest

def echo_model(messages):
    """返回最后一条消息的内容"""
    if not messages:
        return ""
    return messages[-1]["content"]

def uppercase_model(messages):
    """返回最后一条消息的内容（大写）"""
    if not messages:
        return ""
    return messages[-1]["content"].upper()

class TestFakeModels(unittest.TestCase):
    def test_echo_model_returns_last_message(self):
        """测试 EchoModel 返回最后一条消息"""
        messages = [{"role": "user", "content": "hello"}]
        result = echo_model(messages)
        self.assertEqual(result, "hello")

    def test_uppercase_model_converts_to_upper(self):
        """测试 UppercaseModel 转换为大写"""
        messages = [{"role": "user", "content": "hello world"}]
        result = uppercase_model(messages)
        self.assertEqual(result, "HELLO WORLD")

    def test_handles_multiple_messages(self):
        """测试处理多条消息（system + user）"""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "greetings"}
        ]
        result = echo_model(messages)
        self.assertEqual(result, "greetings")

    def test_echo_model_with_empty_content(self):
        """测试空内容的消息"""
        messages = [{"role": "user", "content": ""}]
        result = echo_model(messages)
        self.assertEqual(result, "")

    def test_uppercase_preserves_numbers_and_symbols(self):
        """测试大写转换保留数字和符号"""
        messages = [{"role": "user", "content": "test123!@#"}]
        result = uppercase_model(messages)
        self.assertEqual(result, "TEST123!@#")

if __name__ == "__main__":
    unittest.main()

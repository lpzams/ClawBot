import unittest

def echo_model(messages):
    """返回最后一条消息的内容"""
    # TODO: 实现这个函数
    pass

def uppercase_model(messages):
    """返回最后一条消息的内容（大写）"""
    # TODO: 实现这个函数
    pass

class TestFakeModels(unittest.TestCase):
    def test_echo_model_returns_last_message(self):
        """测试 EchoModel 返回最后一条消息"""
        # TODO: 编写测试
        # 提示：创建一个消息列表，调用 echo_model，断言结果
        pass

    def test_uppercase_model_converts_to_upper(self):
        """测试 UppercaseModel 转换为大写"""
        # TODO: 编写测试
        pass

    def test_handles_multiple_messages(self):
        """测试处理多条消息（system + user）"""
        # TODO: 编写测试
        # 提示：创建包含 system 和 user 消息的列表
        # 应该返回 user 的内容（最后一条）
        pass

    def test_echo_model_with_empty_content(self):
        """测试空内容的消息"""
        # TODO: 编写测试
        pass

if __name__ == "__main__":
    unittest.main()

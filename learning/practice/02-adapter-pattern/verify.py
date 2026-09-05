"""验证练习 2 的完成度"""
import sys
import os

# 添加 starter 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "starter"))

def verify():
    print("🔍 验证练习 2：适配器模式\n")

    checks_passed = 0
    total_checks = 5

    try:
        from simple_adapter import SimpleAdapter, AdapterError
    except ImportError as e:
        print(f"❌ 无法导入模块：{e}")
        return False

    # 检查 1：可以实例化
    print("✓ 检查 1：适配器实例化")
    try:
        adapter = SimpleAdapter("test-key", model="gpt-4")
        print("  ✅ 实例化成功\n")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ 实例化失败：{e}\n")
        return False

    # 检查 2：验证 API key
    print("✓ 检查 2：API key 验证")
    try:
        SimpleAdapter("")
        print("  ❌ 应该拒绝空 API key\n")
    except (ValueError, TypeError):
        print("  ✅ 正确验证 API key\n")
        checks_passed += 1

    # 检查 3：Fake Opener 测试
    print("✓ 检查 3：Fake Opener 集成")

    class MockResponse:
        def read(self):
            return b'{"choices":[{"message":{"content":"test response"}}]}'

    def fake_opener(request, timeout=None):
        return MockResponse()

    try:
        adapter = SimpleAdapter("key", opener=fake_opener)
        result = adapter([{"role": "user", "content": "hello"}])

        if result == "test response":
            print("  ✅ 正确使用 opener 并解析响应\n")
            checks_passed += 1
        else:
            print(f"  ❌ 响应内容错误：期望 'test response'，得到 '{result}'\n")
    except Exception as e:
        print(f"  ❌ 调用失败：{e}\n")

    # 检查 4：请求格式
    print("✓ 检查 4：请求格式验证")

    captured_request = {}

    def spy_opener(request, timeout=None):
        captured_request["headers"] = dict(request.headers)
        captured_request["data"] = request.data
        return MockResponse()

    try:
        adapter = SimpleAdapter("secret-key", opener=spy_opener)
        adapter([{"role": "user", "content": "hi"}])

        # 验证 Authorization 头
        auth_header = captured_request.get("headers", {}).get("Authorization", "")
        if "Bearer secret-key" in auth_header:
            print("  ✅ Authorization 头正确")
            checks_passed += 1
        else:
            print(f"  ❌ Authorization 头错误：{auth_header}")

        # 验证请求体
        import json
        body = json.loads(captured_request.get("data", b"{}"))
        if "model" in body and "messages" in body:
            print("  ✅ 请求体包含必需字段\n")
        else:
            print(f"  ❌ 请求体缺少字段：{body}\n")

    except Exception as e:
        print(f"  ❌ 请求构造失败：{e}\n")

    # 检查 5：错误处理
    print("✓ 检查 5：错误处理")

    def error_opener(request, timeout=None):
        raise Exception("Network error")

    try:
        adapter = SimpleAdapter("key", opener=error_opener)
        adapter([{"role": "user", "content": "test"}])
        print("  ❌ 应该抛出 AdapterError\n")
    except AdapterError:
        print("  ✅ 正确抛出 AdapterError\n")
        checks_passed += 1
    except Exception as e:
        print(f"  ❌ 抛出了错误的异常类型：{type(e).__name__}\n")

    # 总结
    print("=" * 50)
    print(f"\n验证结果：{checks_passed}/{total_checks} 项通过\n")

    if checks_passed == total_checks:
        print("🎉 练习完成！")
        print("\n下一步：")
        print("1. 查看 solution/ 对比你的实现")
        print("2. 阅读 ClawBot 的 clawbot/models.py")
        print("3. 在 phase2-workbook.md 中记录学习心得")
        print("4. 思考：为什么要统一异常？opener 注入的好处是什么？")
        return True
    else:
        print("⚠️  还有检查项未通过，继续加油！")
        print("\n提示：")
        print("- 查看 README.md 了解练习要求")
        print("- 使用提示部分获取代码示例")
        print("- 参考 clawbot/models.py 的实现")
        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)

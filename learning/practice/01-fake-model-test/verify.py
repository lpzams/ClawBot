"""验证练习 1 的完成度"""
import subprocess
import sys
import os

def verify():
    print("🔍 验证练习 1：Fake Model 测试\n")

    checks_passed = 0
    total_checks = 3

    # 检查 1：测试文件存在
    print("✓ 检查 1：测试文件存在")
    if not os.path.exists("starter/test_fake.py"):
        print("  ❌ 未找到 starter/test_fake.py")
        return False
    print("  ✅ 文件存在\n")
    checks_passed += 1

    # 检查 2：测试可以运行
    print("✓ 检查 2：运行测试")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "starter.test_fake"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("  ❌ 测试失败")
        print(f"\n输出：\n{result.stdout}")
        print(f"\n错误：\n{result.stderr}")
        return False
    print("  ✅ 所有测试通过\n")
    checks_passed += 1

    # 检查 3：代码质量（简单检查）
    print("✓ 检查 3：代码实现")
    with open("starter/test_fake.py", "r", encoding="utf-8") as f:
        content = f.read()

    if "pass" in content and content.count("pass") > 2:
        print("  ⚠️  警告：还有 TODO 未完成（函数中有 pass）")
        print("  提示：确保所有函数都有实际实现")
    else:
        print("  ✅ 代码已实现\n")
        checks_passed += 1

    # 总结
    print("=" * 50)
    print(f"\n验证结果：{checks_passed}/{total_checks} 项通过\n")

    if checks_passed == total_checks:
        print("🎉 练习完成！")
        print("\n下一步：")
        print("1. 查看 solution/ 对比你的实现")
        print("2. 在 phase1-workbook.md 中记录学习心得")
        print("3. 尝试扩展挑战（README 中）")
        return True
    else:
        print("⚠️  还有检查项未通过，继续加油！")
        print("\n提示：")
        print("- 查看 README.md 了解练习要求")
        print("- 使用提示部分获取帮助")
        print("- 测试应该是确定性的（每次运行结果相同）")
        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)

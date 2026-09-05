---
name: practice
description: 动手练习模式，通过编写和验证代码巩固学习，自动检查答案
---

# 练习 Skill

提供结构化的编程练习，帮助你通过实战巩固 ClawBot 的核心概念。

## 工作流程

### 1. 选择练习

根据 `learning/state.json` 中的 `current_phase`，推荐对应的练习：
- Phase 1 → `01-fake-model-test`
- Phase 2 → `02-adapter-pattern`
- Phase 3 → `03-tool-safety`

### 2. 提供练习说明

每个练习包含：
- **目标**：这个练习要实现什么
- **起始代码**：`starter/` 目录中的模板
- **验收标准**：如何判断完成
- **提示**：卡住时的方向提示
- **参考答案**：完成后可以对比

### 3. 编写代码

学习者在 `learning/practice/{练习目录}/` 中编写代码

### 4. 自动验证

运行 `verify.py` 脚本，检查：
- 代码能否运行
- 测试是否通过
- 是否满足验收标准

### 5. 反馈和改进

- ✅ 通过：解释做得好的地方，指出可优化的点
- ❌ 失败：指出问题，给出改进方向（不直接给答案）

### 6. 更新 Workbook

练习结果记录到对应的 workbook：
- 完成时间
- 遇到的困难
- 学到的经验
- 可以在面试中讲的点

## 练习结构

```
learning/practice/01-fake-model-test/
├── 练习说明.md           # 练习说明
├── starter/            # 起始代码
│   └── test_fake.py   # 待完成的测试
├── solution/           # 参考答案（完成后查看）
│   └── test_fake.py
└── verify.py           # 自动验证脚本
```

## 使用方法

**开始练习：**
```
/practice 开始
```

**验证答案：**
```
/practice 验证
```

**查看提示：**
```
/practice 提示
```

**查看参考答案：**
```
/practice 答案
```

## 验证脚本示例

每个练习的 `verify.py` 检查：

```python
def verify():
    """自动验证练习完成度"""
    checks = []
    
    # 检查 1：文件存在
    if not os.path.exists("test_fake.py"):
        return {"passed": False, "message": "未找到 test_fake.py"}
    
    # 检查 2：测试可以运行
    result = subprocess.run(["python", "-m", "unittest", "test_fake.py"])
    if result.returncode != 0:
        return {"passed": False, "message": "测试未通过"}
    
    # 检查 3：代码质量
    # ... 更多检查
    
    return {"passed": True, "message": "练习完成！"}
```

## AI 模型切换支持

任何模型执行此 Skill 时：
1. 读取 `learning/state.json` 确定当前阶段
2. 读取对应 workbook 了解已完成的练习
3. 推荐下一个合适的练习
4. 验证时给出一致的评价标准

## 练习与面试的关联

每个练习完成后，在 workbook 中记录：

**面试中可以讲：**
- "我在练习中实现了 Fake Model 测试，确保 Harness 在无网络时也能验证"
- "这个设计让我理解了测试替身（Test Double）的实际应用"
- "类似 [企业案例] 的做法"

## 注意事项

1. **渐进式难度**：先简单后复杂，每个练习基于前一个
2. **真实场景**：练习来自 ClawBot 实际代码，不是凭空设计
3. **可验证**：自动化验证，减少主观判断
4. **面试导向**：每个练习都对应一个可以在面试中讲的技术点


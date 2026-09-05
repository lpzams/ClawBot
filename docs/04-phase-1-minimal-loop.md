---
layout: page
title: "Phase 1：可测试的最小执行链"
---

## 1. 本课目标

不接真实模型，先回答一个更基础的问题：Harness 能否把正确的消息交给一个模型，并把模型回复返回给调用者？

本课完成的数据流只有：

```text
命令行 prompt -> run_agent -> fake_model -> 文本回复
```

## 2. 为什么先用 Fake Model

真实模型具有网络、密钥、费用、限流和输出波动。若第一步就接 API，测试失败时很难快速判断是 Harness、配置还是网络出了问题。

Fake Model 是一个普通函数：收到消息，返回固定字符串。它让我们只验证自己的编排代码，而且运行快速、免费、结果稳定。

## 3. 测试先描述行为

测试构造一个局部 `fake_model`，把收到的消息保存到 `seen_messages`：

```python
seen_messages = []

def fake_model(messages):
    seen_messages.extend(messages)
    return "fixed reply"
```

然后验证两件事：

1. `run_agent` 返回模型的回复。
2. 模型收到 `[{"role": "user", "content": "hello"}]`。

这个测试没有检查内部用了多少函数或类，只检查可观察行为，所以将来可以安全重构实现。

## 4. 最小实现怎样工作

核心函数只有一个分支和一次调用：

```python
def run_agent(prompt, model):
    if not prompt.strip():
        raise ValueError("prompt cannot be blank")

    return model([{"role": "user", "content": prompt}])
```

这里的 `model` 是函数参数，这是一种最小依赖注入：生产环境可以传真实模型函数，测试可以传 Fake Model。Phase 1 当时没有必要创建抽象基类、工厂或依赖注入框架；Phase 2 只增加了一个具体的 `Harness` 外壳，仍然没有引入这些重量级结构。

## 5. CLI 只负责输入输出

`clawbot/__main__.py` 用标准库 `argparse`：

- 读取一个必填的 `prompt`。
- 调用 `run_agent`。
- 打印结果。
- 把空白输入转换成友好的命令行错误。

CLI 不负责组织模型消息。这种边界让核心逻辑无需启动子进程就能被测试。

## 6. 亲自运行

请在功能 worktree 中执行：

```powershell
Set-Location P:\github\Harness\.worktrees\minimal-loop
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
python -m clawbot "   "
```

再用 Git 查看本分支到底改了什么：

```powershell
git status --short
git diff
```

## 7. 你应该能回答的面试问题

### 为什么不直接在测试里调用真实模型？

核心单元测试必须确定、快速且不依赖外部服务。真实 API 应由少量集成测试和手工演示覆盖。

### 这已经算 Agent 吗？

还不算完整 Agent。目前只有一次模型调用，没有工具选择和循环。它是后续 Agent loop 的第一个可验证切片。

### 为什么消息用字典，不用类？

当前只有 `role` 和 `content`，字典与 API JSON 直接对应。等工具调用带来更复杂的合法状态时，再引入结构化类型会更有价值。

### 现在最大的设计上限是什么？

模型只能返回字符串，因此无法表达“调用哪个工具以及参数是什么”。Phase 3 会在真实需求出现时把回复升级为结构化结果。

## 8. 小练习

不要马上增加新功能，先确认自己理解现有行为：

1. 在纸上写出 `python -m clawbot "hi"` 从 CLI 到返回值经过的函数。
2. 把测试中的期望消息改错，观察失败信息，然后恢复。
3. 解释为什么 `run_agent("   ", model)` 不应该调用模型。
4. 执行 `git diff -- tests/test_agent.py clawbot`，逐行说明每个改动解决哪个验收条件。

完成这些练习后，继续阅读[可复用框架接入指南]({{ '/06-reusable-framework.html' | relative_url }})，看同一个模型函数边界如何被其他项目复用，再进入真实模型 adapter。

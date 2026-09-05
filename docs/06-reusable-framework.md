---
layout: page
title: 把 ClawBot 当作可复用框架
---

## 1. 这一次要解决什么问题

前面的版本证明了“输入能传给模型”。但如果每个项目都复制一份 `__main__.py`、模型请求代码和输入校验，最后得到的只是一个示例，而不是框架。

这一阶段把边界固定下来：

```text
业务项目（命令行、Web、定时任务）
                │
                ▼
        Harness.run(prompt)
                │
                ▼
       Model：messages -> text
                │
                ▼
      Fake 或真实模型适配器
```

`Harness` 不知道项目是客服、代码审查还是数据分析；它只负责所有项目都需要的最小编排。项目自己的业务规则留在项目里，供应商的 HTTP/SDK 细节留在 adapter 里。

## 2. 三层边界

| 层 | 负责什么 | 不负责什么 |
| --- | --- | --- |
| `clawbot.agent.Harness` | 校验输入、组装消息、调用模型 | API Key、HTTP、CLI 参数、业务规则 |
| `clawbot.models.OpenAICompatibleModel` | 把消息发送到兼容接口、解析文本 | 决定业务流程、执行本地工具 |
| 你的项目入口 | 收集输入、选择配置、展示结果 | 重新实现消息编排 |

这不是为了把代码拆成很多层，而是为了让每一层只有一个变化原因：

- 换模型供应商时，不改 Harness。
- 换 CLI 为 Web 时，不改 Harness。
- 换业务提示词时，不改 adapter。
- 测试时，用 Fake Model 替换网络 adapter。

## 3. 最小公共 API

框架的入口只有一个类：

```python
from clawbot import Harness


def fake_model(messages):
    return "收到：" + messages[-1]["content"]


harness = Harness(
    fake_model,
    system_prompt="你是一个简洁的项目助手。",
)
answer = harness.run("总结今天的工作")
print(answer)
```

调用 `run` 时，Harness 做四件事：

1. 拒绝空字符串，避免无意义的模型请求。
2. 把可选的 system 指令和 user 输入按固定顺序组装成消息列表。
3. 调用传入的模型函数。
4. 确认模型返回文本，再把文本交给上层。

模型只需要满足这个约定：

```python
messages: list[dict[str, str]] -> str
```

因此，普通函数、一个 SDK client 的包装类、远程 RPC 客户端都可以作为模型传入。这里没有创建抽象基类、工厂或容器；一个可调用对象已经是最小且够用的依赖注入。

旧代码仍然可以使用函数入口：

```python
from clawbot import run_agent

answer = run_agent("hello", fake_model)
```

`run_agent` 只是兼容包装，内部与 `Harness` 走同一条路径，不会产生两套行为。

## 4. 为什么模型 adapter 不放进 Harness

真实模型请求通常包含以下变化：

- 不同供应商的 URL 和认证头。
- 不同的模型名称和响应 JSON。
- 超时、限流、网络断开。
- SDK 版本和重试策略。

如果把这些细节写进 Harness，任何项目都会被绑定到某一家供应商；测试也会被迫启动网络。现在 `OpenAICompatibleModel` 是一个可选 adapter，核心包本身仍然只依赖 Python 标准库。

它支持所有遵循常见 Chat Completions 请求形状的服务。配置通过环境变量读取：

```powershell
$env:OPENAI_API_KEY = "你的密钥"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "gpt-4o-mini"
python -m clawbot --provider openai "解释这个项目"
```

也可以在 Python 项目中直接创建：

```python
from clawbot import Harness, OpenAICompatibleModel

model = OpenAICompatibleModel.from_env()
harness = Harness(model, system_prompt="只回答和项目有关的问题")
print(harness.run("README 讲了什么？"))
```

密钥只进入请求头，不会拼到异常消息中。没有 `OPENAI_API_KEY` 时，adapter 会在发出网络请求前失败，这样错误位置是明确的。

## 5. 在另一个项目中接入

假设另一个项目叫 `reviewer`，它想让模型审查一段代码。接入步骤只有三步。

### 第一步：安装或引用包

在 ClawBot 仓库根目录执行：

```powershell
python -m pip install -e .
```

`pyproject.toml` 没有声明运行时第三方依赖。也可以把 `clawbot/` 作为内部包放进现有仓库，公共 API 不变。

### 第二步：在业务入口选择模型

```python
# reviewer/main.py
from clawbot import Harness, OpenAICompatibleModel


def review(code: str) -> str:
    model = OpenAICompatibleModel.from_env()
    harness = Harness(
        model,
        system_prompt="你是严格但实用的代码审查员，指出问题并给出最小修复建议。",
    )
    return harness.run("请审查下面的代码：\n\n" + code)
```

### 第三步：让业务层决定输入输出

```python
print(review(open("example.py", encoding="utf-8").read()))
```

`review` 是业务代码；Harness 不需要知道“代码审查”这个概念。下一个项目可以把同一个 Harness 用在客服、报告摘要或内部知识问答中，只替换 system prompt、输入和模型 adapter。

## 6. 测试为什么仍然不联网

业务项目的单元测试应传入 Fake Model：

```python
from clawbot import Harness


def test_review_sends_the_expected_prompt():
    seen = []

    def fake_model(messages):
        seen.extend(messages)
        return "通过"

    result = Harness(fake_model).run("审查：x = 1")

    assert result == "通过"
    assert seen[-1] == {"role": "user", "content": "审查：x = 1"}
```

这个测试只证明自己的编排行为，不证明供应商服务可用。网络 adapter 另外用一个假的 `opener` 检查 URL、请求头、JSON 和响应解析。两类问题分开后，失败更容易定位：

```text
业务/Harness 测试失败 -> 检查本地编排
adapter 测试失败     -> 检查供应商协议转换
手工集成测试失败     -> 检查密钥、网络和账户配置
```

## 7. 一次调用的完整数据流

以 `Harness(model).run("hello")` 为例：

```text
调用方传入 prompt
        │
        ▼
Harness.run 校验非空
        │
        ▼
[{"role": "user", "content": "hello"}]
        │
        ▼
model(messages)
        │
        ├── Fake Model：直接返回固定文本
        └── OpenAICompatibleModel：HTTP 请求 -> JSON -> 文本
        │
        ▼
Harness 校验返回值类型
        │
        ▼
调用方得到最终字符串
```

这里的“单次调用”是一个有意的边界。它已经足以复用模型接入和测试方式，但还没有假装自己支持工具、记忆或自主循环。

## 8. 当前框架的上限与下一步

当前公共协议返回字符串，所以它不能表达“调用哪个工具、参数是什么”。当第一个真实项目确实需要工具时，再把返回值升级为结构化 `ModelResponse`，并在 Harness 中加入：

1. 工具白名单和参数校验。
2. 最大循环步数。
3. 工具结果消息。
4. 可脱敏的事件记录。

这些能力会扩展同一个边界，而不是让每个业务项目各写一套 Agent loop。没有真实工具需求之前，不提前加入这些类型和注册表，避免框架为了假想场景变重。

## 9. 复用检查清单

把框架带到新项目时，确认以下事项：

- 业务入口只负责输入、配置和输出。
- Harness 只负责消息编排和边界校验。
- 模型供应商细节都在 adapter 中。
- 单元测试使用 Fake Model，不访问网络。
- 密钥来自环境变量，不写进源码或日志。
- 需要工具前，不创建工具系统；需要循环前，不创建状态机。

满足这六点，ClawBot 就是一个可以套用的最小骨架，而不只是当前仓库的演示命令。

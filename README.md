# ClawBot

ClawBot 是一个用于认真学习并复用 **AI Harness（AI 智能体运行框架）** 的最小项目。

在线学习站：<https://lpzams.github.io/ClawBot/>

我们不会先套用大型 Agent 框架，而是从一条可测试的执行链开始，逐步实现目标链路：

```text
用户输入 -> 模型请求 -> 工具调用 -> 工具结果 -> 模型回答 -> 事件记录
```

这样既能理解模型 API，也能在面试中讲清楚 Harness 为什么需要状态、循环、安全边界、可观测性和评测。

## 当前状态

项目处于 **Phase 2：可复用核心与模型适配器**，并开始学习 Jenkins CI/CD。

- [x] 初始化本地 Git 仓库，默认分支为 `main`
- [x] 定义最小产品范围和学习路线
- [x] 编写 GitHub 与 worktree 实操手册
- [x] 创建第一个功能 worktree
- [x] 实现不依赖真实模型的最小 Harness 执行链
- [x] 把核心执行器封装为可复用 `Harness`
- [x] 增加无第三方运行时依赖的 OpenAI-compatible adapter
- [x] 增加 Jenkins Pipeline：测试、冒烟检查、打包和交付归档
- [ ] 用真实 API 做一次手工集成验证

## 文档

1. [先读：ClawBot 到底是什么](docs/00-what-is-clawbot.md)
2. [学习与开发路线](docs/00-learning-roadmap.md)
3. [Git、GitHub 与 worktree](docs/01-git-github-worktree.md)
4. [ClawBot 最小产品定义](docs/02-mvp-definition.md)
5. [开发日志](docs/03-development-log.md)
6. [Phase 1：最小执行链](docs/04-phase-1-minimal-loop.md)
7. [可复用框架接入指南](docs/06-reusable-framework.md)
8. [发布到 GitHub Pages](docs/05-publishing-github-pages.md)
9. [Jenkins CI/CD 实操](docs/07-jenkins-ci-cd.md)

## 技术选择

- Python 3.9+（推荐 3.11+）
- CLI 优先
- 标准库优先
- 先用 Fake Model 写测试，再接真实模型 API
- 暂不引入 LangChain、数据库、Web UI 或多 Agent

这些延后项不是永远不做，而是等核心执行链跑通、并且有明确需求时再加入。

## 作为框架使用

安装当前仓库后，其他 Python 项目即可复用同一个包：

```powershell
python -m pip install -e .
```

业务项目只需要提供一个 `messages -> string` 的模型函数：

```python
from clawbot import Harness

harness = Harness(my_model, system_prompt="回答要简洁、可执行")
answer = harness.run("分析这份报告")
```

CLI、Web 接口和定时任务都可以调用同一个 `Harness`；供应商 SDK 或 HTTP 只放在模型 adapter 中。完整的跨项目接入示例见[可复用框架接入指南](docs/06-reusable-framework.md)。

## 当前演示

```powershell
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
python -m clawbot --help
```

需要真实模型时，先设置 `OPENAI_API_KEY`（以及可选的 `OPENAI_BASE_URL`、`OPENAI_MODEL`），再运行：

```powershell
python -m clawbot --provider openai "hello harness"
```

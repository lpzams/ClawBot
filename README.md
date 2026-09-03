# ClawBot

ClawBot 是一个用于认真学习 **AI Harness（AI 智能体运行框架）** 的最小项目。

在线学习站：<https://lpzams.github.io/ClawBot/>

我们不会先套用大型 Agent 框架，而是从一条可测试的执行链开始，亲手实现：

```text
用户输入 -> 模型请求 -> 工具调用 -> 工具结果 -> 模型回答 -> 事件记录
```

这样既能理解模型 API，也能在面试中讲清楚 Harness 为什么需要状态、循环、安全边界、可观测性和评测。

## 当前状态

项目处于 **Phase 1：可测试的最小执行链**。

- [x] 初始化本地 Git 仓库，默认分支为 `main`
- [x] 定义最小产品范围和学习路线
- [x] 编写 GitHub 与 worktree 实操手册
- [x] 创建第一个功能 worktree
- [x] 实现不依赖真实模型的最小 Harness 循环
- [ ] 接入真实模型 API

## 文档

1. [学习与开发路线](docs/00-learning-roadmap.md)
2. [Git、GitHub 与 worktree](docs/01-git-github-worktree.md)
3. [ClawBot 最小产品定义](docs/02-mvp-definition.md)
4. [开发日志](docs/03-development-log.md)
5. [Phase 1：最小执行链](docs/04-phase-1-minimal-loop.md)
6. [发布到 GitHub Pages](docs/05-publishing-github-pages.md)

## 技术选择

- Python 3.11+
- CLI 优先
- 标准库优先
- 先用 Fake Model 写测试，再接真实模型 API
- 暂不引入 LangChain、数据库、Web UI 或多 Agent

这些延后项不是永远不做，而是等核心执行链跑通、并且有明确需求时再加入。

## 当前演示

```powershell
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
```

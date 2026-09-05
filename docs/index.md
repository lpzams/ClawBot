---
layout: home
title: ClawBot 学习站
---

ClawBot 是一个边开发、边测试、边记录的可复用 AI Agent Harness 学习项目。

这里不仅展示最终代码，也保留需求定义、技术取舍、Git worktree、测试、Issue 和 Pull Request 的完整开发过程。

## 从这里开始

1. [先读：ClawBot 到底是什么]({{ '/00-what-is-clawbot.html' | relative_url }})：先用普通语言理解模型、Harness 和 Agent 的区别。
2. [学习与开发路线]({{ '/00-learning-roadmap.html' | relative_url }})：了解项目怎样分阶段完成。
3. [Git、GitHub 与 worktree]({{ '/01-git-github-worktree.html' | relative_url }})：跟着真实命令学习仓库管理。
4. [ClawBot MVP 定义]({{ '/02-mvp-definition.html' | relative_url }})：学习怎样控制项目边界和验收标准。
5. [开发日志]({{ '/03-development-log.html' | relative_url }})：查看每次开发的目标、失败、验证和决定。
6. [Phase 1 最小执行链]({{ '/04-phase-1-minimal-loop.html' | relative_url }})：学习第一个红灯到绿灯的实现。
7. [可复用框架接入指南]({{ '/06-reusable-framework.html' | relative_url }})：把核心代码接到其他项目。
8. [发布到 GitHub Pages]({{ '/05-publishing-github-pages.html' | relative_url }})：理解本站是怎样发布的。
9. [Jenkins CI/CD 实操]({{ '/07-jenkins-ci-cd.html' | relative_url }})：用 Jenkins 自动测试并交付构建产物。

## 当前可运行功能

```powershell
git clone https://github.com/lpzams/ClawBot.git
cd ClawBot
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
```

默认使用 Fake Model，因此运行测试和演示都不需要 API Key；需要时可通过 `--provider openai` 切换兼容接口。

## 项目导航

- [GitHub 仓库](https://github.com/lpzams/ClawBot)
- [Issues](https://github.com/lpzams/ClawBot/issues)
- [Pull Requests](https://github.com/lpzams/ClawBot/pulls)
- [源代码](https://github.com/lpzams/ClawBot/tree/main/clawbot)
- [自动测试](https://github.com/lpzams/ClawBot/tree/main/tests)

## 当前边界

ClawBot 目前提供一次确定性的通用模型调用和一个真实模型 adapter。工具调用、安全审批、事件日志和评测会按学习路线逐步加入，而不是提前堆进项目。

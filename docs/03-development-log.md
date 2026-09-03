# ClawBot 开发日志

这个文件记录每次开发的目标、命令、关键判断、验证结果和下一步。它不是流水账；只保留以后复盘和面试讲解真正有用的信息。

## 2026-09-03｜Session 001｜建立项目基线

### 本次目标

从空目录建立一个可以持续学习和开发的仓库基线，并明确 ClawBot 的范围。

### 实际操作

```powershell
git init -b main
```

新增：

- `.gitignore`
- `README.md`
- 学习路线
- Git/GitHub/worktree 手册
- MVP 定义
- 开发日志

### 学到的内容

- Git 仓库可以先完全存在于本地，GitHub 是后续添加的远程协作平台。
- AI Harness 的核心不是聊天页面，而是模型、工具、状态、安全和事件之间的执行闭环。
- 先定义 MVP 和完成标准，可以避免项目被 RAG、多 Agent、UI 等功能带偏。

### 关键决定

- 使用 Python 3.11+ 和 CLI，降低非核心复杂度。
- Phase 1 先用 Fake Model，不让 API Key 和网络阻塞核心学习。
- 先实现单 Agent、单只读工具，再依据真实需求扩展。

### 验证

- `rg --files` 确认预期的 6 个项目文件均已创建。
- `git diff --cached --check` 通过，没有空白或冲突标记错误。
- 自动执行环境因目录所有者不同触发了 Git 的 `dubious ownership` 保护；本次只通过命令级 `-c safe.directory=P:/github/Harness` 放行，没有修改用户全局配置。
- 本次基线提交信息：`docs: define ClawBot learning roadmap`。

### 下一步

1. 建立基线 commit。
2. 创建 `feat/minimal-loop` worktree。
3. 在该 worktree 中实现第一个失败测试和最小执行链。

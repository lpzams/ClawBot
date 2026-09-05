---
layout: page
title: ClawBot 开发日志
---

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

## 2026-09-03｜Session 002｜最小执行链

### 本次目标

在独立 worktree 中完成一条不依赖网络和 API Key 的执行链：

```text
CLI 输入 -> run_agent -> Fake Model -> 固定回答
```

### Git 操作

基线提交：

```text
3b42887 docs: define ClawBot learning roadmap
```

创建本分支的命令：

```powershell
git worktree add .worktrees/minimal-loop -b feat/minimal-loop main
```

教学环境把 worktree 放在仓库内已忽略的 `.worktrees/` 中；日常开发更推荐手册中的同级目录布局。

### 红灯：先证明功能不存在

先创建 `tests/test_agent.py`，再运行：

```powershell
python -m unittest discover -s tests -v
```

第一次结果是 `ModuleNotFoundError: No module named 'clawbot'`。这说明测试确实在寻找尚未实现的产品入口，而不是一个无论如何都会通过的空测试。

### 绿灯：最少实现

新增：

- `clawbot/agent.py`：校验输入并把用户消息交给模型。
- `clawbot/__main__.py`：使用 `argparse` 提供 CLI 和离线 Fake Model。
- `clawbot/__init__.py`：标记 Python 包。

模型暂时只是一个传入 `run_agent` 的函数。函数参数已经能让测试替换真实模型，因此没有创建单实现接口、工厂或容器。

### 验证结果

```text
Ran 2 tests in 0.000s
OK
```

```powershell
python -m clawbot "hello harness"
# ClawBot received: hello harness

python -m clawbot "   "
# error: prompt cannot be blank
```

### 环境发现

当前机器只有 Python 3.9.13。Phase 1 的标准库代码可以运行，但 Python 3.9 已结束官方支持；接入真实模型前应建立 Python 3.12 虚拟环境，并把版本要求写入项目配置。本阶段为了方便复用，代码仍保持 3.9 语法兼容，实际部署推荐 3.11/3.12。

### 关键决定

- 用 `unittest` 而不是安装测试框架：当前两个行为不需要额外依赖。
- 用普通字典表示消息：它与模型 API 的 JSON 结构接近，当前足够。
- 用字符串表示模型回复：工具调用出现后再升级为结构化响应。
- 保留空输入校验：CLI 是输入边界，失败应明确且可预测。

### 下一步

1. 本分支以 `feat: add minimal agent loop` 建立功能提交。
2. 创建 GitHub 远程仓库并推送 `main` 与功能分支。
3. 用 PR 练习审查和合并。
4. 建立 Python 3.12 环境后开始真实模型 adapter。

## 2026-09-03｜Session 003｜公开仓库与学习网站

### 本次目标

把本地学习项目发布为公开 GitHub 仓库，并让 `docs/` 成为任何人都能访问的网站。

### GitHub 实操记录

1. 使用 GitHub 设备授权登录账号 `lpzams`。
2. 创建公开仓库：<https://github.com/lpzams/ClawBot>。
3. 创建 [Issue #1](https://github.com/lpzams/ClawBot/issues/1) 定义 Phase 1 验收条件。
4. 推送 `feat/minimal-loop` 并创建 [PR #2](https://github.com/lpzams/ClawBot/pull/2)。
5. 复查目标分支、文件列表、可合并状态，并再次运行测试。
6. 用 merge commit 合并 PR，自动关闭 Issue #1。
7. 同步本地 `main`，确认旧 worktree 干净后将其移除。
8. 从最新 `main` 创建 `docs/github-pages` worktree。
9. 创建 [Issue #3](https://github.com/lpzams/ClawBot/issues/3) 记录网站验收条件。

### 网站方案

直接使用 GitHub Pages 的 `main` 分支 `/docs` 目录：

```text
Markdown 文档 -> GitHub Pages/Jekyll -> 公共网页
```

只增加首页、Jekyll front matter 和 `_config.yml`。没有建立独立前端，也不提交生成后的 HTML。

### 关键决定

- 仓库设为公开，方便面试官和其他学习者查看历史、issue、PR 与代码。
- 保留 issue 和 merge commit，让开发过程本身也成为作品的一部分。
- 使用 GitHub 原生 Pages；当前内容站不需要前端框架和自建服务器。
- Pages 地址固定为 <https://lpzams.github.io/ClawBot/>。

### 下一步

1. 通过 PR 合并 Pages 配置。
2. 把 Pages 源设置为 `main` 的 `/docs`。
3. 等待 GitHub 构建，并验证公开地址。
4. 下一阶段建立 Python 3.12 环境并接入真实模型。

## 2026-09-03｜Session 004｜可复用核心与模型适配器

### 本次目标

让 ClawBot 不只是当前仓库的演示命令，而是可以被其他项目直接导入的最小框架，同时保持离线测试。

### 实际操作

新增：

- `clawbot.agent.Harness`：项目无关的一次模型调用边界。
- `clawbot.models.OpenAICompatibleModel`：只使用标准库的真实模型 adapter。
- `pyproject.toml`：允许以 editable package 方式接入其他项目。
- `docs/06-reusable-framework.md`：解释层次、数据流、接入步骤和当前上限。

保留：

- `run_agent` 作为旧代码的兼容函数。
- Fake Model 作为默认 CLI provider。
- 所有自动测试不访问网络。

### 关键决定

- Harness 只接受 `messages -> string` 的可调用对象，不绑定供应商 SDK。
- OpenAI-compatible adapter 放在独立模块，便于替换为其他 provider。
- 不提前加入工具注册表、状态机或事件系统；这些属于后续阶段，当前字符串协议无法证明它们有真实需求。
- 使用 `urllib` 而不是新增 HTTP 依赖，降低其他项目的接入成本。

### 验证

```text
Ran 7 tests in 0.001s
OK
```

测试覆盖：消息编排、system prompt、空输入、返回值边界、请求构造、环境变量校验和异常响应解析。

### 下一步

1. 建立 Python 3.11/3.12 虚拟环境并运行 `pip install -e .`。
2. 使用真实 API 做一次手工 smoke test，不把它放进默认自动测试。
3. 若一个实际项目需要工具，再开始 Phase 3 的结构化响应和受限工具循环。

## 2026-09-04｜Session 005｜接入 Jenkins CI/CD 学习链路

### 本次目标

让学习项目具备一条不依赖真实模型 API 的 Jenkins CI/CD 流水线，并能在本地复现同样的检查。

### 实际操作

新增：

- 根目录 `Jenkinsfile`：`Checkout -> Test -> Smoke -> Build -> Deliver`。
- `docs/07-jenkins-ci-cd.md`：Jenkins 启动、任务配置、失败演练和凭据边界。

同步更新 README、学习路线和站点首页导航。

### 关键决定

- 使用 Jenkins Pipeline as Code，避免把构建步骤散落在 Jenkins 网页配置中。
- CI 只运行离线 `unittest` 和 Fake Model CLI 冒烟检查，不在构建中消耗真实 API。
- CD 先做到持续交付：用 `git archive` 生成并归档通过检查的源码 ZIP；当前没有真实部署目标，因此不添加虚假的生产部署脚本。
- Jenkinsfile 兼容 Linux 和 Windows agent，只依赖 Python、Git 及 Jenkins 内置步骤。

### 验证

```powershell
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
```

下一次在 Jenkins 中选择 **Pipeline script from SCM**，指向仓库根目录的 `Jenkinsfile`，即可观察同一条链路。

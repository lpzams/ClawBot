# Git、GitHub 与 worktree 实操手册

## 1. 先分清三个概念

| 名称 | 它是什么 | 在本项目里的作用 |
| --- | --- | --- |
| Git | 本地版本控制工具 | 保存历史、分支、提交和合并 |
| GitHub | 托管 Git 仓库的协作平台 | issue、PR、代码审查、自动检查 |
| Git worktree | Git 自带的多工作目录功能 | 同时打开多个分支，不必反复切换或复制仓库 |

worktree 不是 GitHub 的功能。即使没有远程仓库，也能使用它。

## 2. 本项目已经执行的初始化

```powershell
git init -b main
```

它做了两件事：

1. 在当前目录创建 `.git` 元数据。
2. 把第一个分支命名为 `main`。

随时用下面三条命令观察仓库：

```powershell
git status
git log --oneline --decorate --graph --all
git remote -v
```

## 3. 建立第一个基线提交

先查看将要提交的内容，而不是直接提交：

```powershell
git status --short
git diff -- . ':(exclude).git'
```

确认后执行：

```powershell
git add .gitignore README.md docs
git diff --cached
git commit -m "docs: define ClawBot learning roadmap"
```

学习重点：

- 工作区是你正在编辑的文件。
- 暂存区是“下一次提交的候选内容”。
- commit 是一个可追踪、可比较、可回退的项目快照。
- `git add` 后一定可以先用 `git diff --cached` 自审。

## 4. 创建 GitHub 远程仓库

推荐先安装并登录 GitHub CLI：

```powershell
gh auth login
```

在第一次提交完成后，从当前目录创建私有仓库：

```powershell
gh repo create ClawBot --private --source . --remote origin --push
```

如果你已在 GitHub 网页创建了空仓库，则执行：

```powershell
git remote add origin https://github.com/<你的用户名>/ClawBot.git
git push -u origin main
```

不要在网页端勾选自动创建 README、License 或 `.gitignore`，否则远端和本地会各自拥有不同的第一次提交，需要额外合并。

验证连接：

```powershell
git remote -v
git branch -vv
```

`origin` 只是远程仓库的惯用别名；`-u` 会建立本地 `main` 和远端 `origin/main` 的跟踪关系。

## 5. 用 worktree 开发第一个功能

### 5.1 推荐的目录布局

```text
P:\github\Harness                 main 分支
P:\github\Harness-worktrees\
└── minimal-loop                  feat/minimal-loop 分支
```

功能目录放在主目录旁边，避免编辑器和搜索工具重复扫描同一仓库。

### 5.2 创建功能分支和工作目录

在主目录执行：

```powershell
Set-Location P:\github\Harness
git switch main
git pull --ff-only              # 尚未配置远端时跳过
git worktree add ..\Harness-worktrees\minimal-loop -b feat/minimal-loop main
```

这条 `git worktree add` 同时完成：

1. 从 `main` 创建 `feat/minimal-loop` 分支。
2. 在新目录检出这个分支。
3. 让两个目录共享同一套 Git 对象和提交历史。

查看所有 worktree：

```powershell
git worktree list
```

进入功能目录开发：

```powershell
Set-Location ..\Harness-worktrees\minimal-loop
git status
```

重要规则：同一个本地分支不能同时被两个 worktree 检出。这能阻止两个目录同时修改同一分支。

### 5.3 提交和推送功能

```powershell
git status --short
git diff
git add <本次相关文件>
git diff --cached
git commit -m "feat: add minimal agent loop"
git push -u origin feat/minimal-loop
```

在 GitHub 为 `feat/minimal-loop` 创建 PR，目标分支选择 `main`。PR 描述至少回答：

- 为什么需要这个改动？
- 它具体产生什么行为？
- 怎样验证？
- 这次明确没有做什么？

### 5.4 合并后清理

确认 PR 已合并且功能目录没有未提交内容：

```powershell
Set-Location P:\github\Harness
git switch main
git pull --ff-only
git worktree remove ..\Harness-worktrees\minimal-loop
git branch -d feat/minimal-loop
git worktree prune
```

`git worktree remove` 会删除那个工作目录，所以必须先用 `git status` 检查。不要直接手动删除目录；让 Git 同时清理登记信息。

## 6. 日常仓库管理流程

一个小功能对应一个 issue、一个分支、一个 worktree 和一个 PR：

```text
Issue -> feat/* branch -> worktree -> commit -> push -> PR -> merge -> cleanup
```

建议的分支名称：

- `feat/minimal-loop`
- `feat/tool-calling`
- `fix/max-step-stop`
- `docs/interview-guide`

建议的提交前缀：

- `feat:` 新行为
- `fix:` 修复错误
- `test:` 只改测试
- `docs:` 只改文档
- `refactor:` 行为不变的整理

提交应该小而完整。不要把多个无关主题塞进一个 commit，也不要为了“保持提交小”而提交不能运行的半成品。

## 7. GitHub 仓库的最小管理设置

个人学习项目先做好这些即可：

1. 把 `main` 设为默认分支。
2. 每项工作用 issue 记录目标和验收条件。
3. 功能通过 PR 合并，即使 PR 由自己审查。
4. Phase 1 有自动测试后，再给 `main` 添加必须通过测试的 ruleset。
5. API Key 只放在本地 `.env` 或 GitHub Actions Secrets，绝不提交。

暂时不需要复杂的多人审批、自动发布和项目看板；出现真实协作或发布需求时再添加。

## 8. 常见错误与恢复

### 忘记自己在哪个分支

```powershell
git status --short --branch
git worktree list
```

### 把文件加进暂存区但还没提交

```powershell
git restore --staged <文件>
```

这只移出暂存区，不删除工作区修改。

### worktree 无法删除

先进入该 worktree 执行 `git status`。提交或妥善保留修改后，再从其他目录执行 `git worktree remove <路径>`。

### 分支已在另一个 worktree 中

执行 `git worktree list` 找到它。切换到那个目录继续开发，或者完成并移除它；不要强制绕过 Git 的保护。

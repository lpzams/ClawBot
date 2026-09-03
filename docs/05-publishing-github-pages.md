---
layout: page
title: 发布公开仓库与 GitHub Pages
---

## 1. 本课结果

- 公开仓库：<https://github.com/lpzams/ClawBot>
- 学习网站：<https://lpzams.github.io/ClawBot/>
- Pages 来源：`main` 分支的 `/docs` 目录

## 2. 为什么选择 GitHub Pages

现有学习材料已经是 Markdown。GitHub Pages 可以直接把这些文件构建成静态网站，并自动提供 HTTPS 和公开地址。

当前没有搜索、登录或动态数据需求，因此不需要 React、文档框架、服务器或数据库。

## 3. 公开仓库流程

登录 GitHub CLI：

```powershell
gh auth login --hostname github.com --git-protocol https --web
```

创建公开仓库并连接本地 `origin`：

```powershell
gh repo create lpzams/ClawBot --public
git remote add origin https://github.com/lpzams/ClawBot.git
git push -u origin main
```

验证：

```powershell
git remote -v
gh repo view lpzams/ClawBot --web
```

## 4. 为什么先经过 Issue 和 PR

公开作品不仅要展示代码，还应展示你怎样定义需求和验证改动。本项目实际建立了：

- [Issue #1](https://github.com/lpzams/ClawBot/issues/1)：记录 Phase 1 的目标和验收条件。
- [PR #2](https://github.com/lpzams/ClawBot/pull/2)：把实现、测试和教学文档合并到 `main`。
- [Issue #3](https://github.com/lpzams/ClawBot/issues/3)：记录学习网站的发布目标和验收条件。

典型命令：

```powershell
git push -u origin feat/minimal-loop
gh pr create --base main --head feat/minimal-loop
gh pr view 2
gh pr merge 2 --merge --delete-branch
```

## 5. Pages 文件各自负责什么

```text
docs/
├── _config.yml   网站标题、主题和地址
├── index.md      网站首页
└── *.md          每一课的正文
```

每个要转换成网页的 Markdown 文件顶部都有 YAML front matter：

```yaml
---
layout: page
title: 页面标题
---
```

GitHub Pages 使用 Jekyll 读取这些信息，并生成 HTML。

## 6. 启用 Pages

在 GitHub 网页进入：

```text
Settings -> Pages -> Build and deployment
```

选择：

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

也可以用 GitHub API 完成相同配置。提交合并到 `main` 后，GitHub 会自动重新构建。

查看状态：

```powershell
gh api repos/lpzams/ClawBot/pages
```

首次部署通常需要几分钟。构建成功后访问：

```text
https://lpzams.github.io/ClawBot/
```

## 7. 日常更新网站

网站内容和代码采用同一套开发流程：

```text
更新 Markdown -> 本地检查 -> commit -> push -> PR -> merge -> Pages 自动发布
```

不直接编辑生成后的 HTML，因为下一次构建会覆盖它。

## 8. 公开仓库安全检查

公开前至少确认：

```powershell
git status
git log --all -- .env
git grep -n -i "api.key\|password\|secret"
```

注意：把秘密加入 `.gitignore` 只能阻止未来提交，不能清除已经进入 Git 历史的秘密。若发生泄露，应立即撤销密钥，再清理历史。

## 9. 你应该能回答的面试问题

### 为什么网站源码放在 `/docs`？

代码和学习文档可以在同一个 PR 中同步审查，GitHub Pages 又能直接从该目录发布，维护路径最短。

### 为什么不使用单独的 `gh-pages` 分支？

本站没有本地构建产物。直接发布 `main/docs` 更容易理解，也不会维护额外的生成分支。

### 什么时候才需要文档框架？

当页面数量、版本切换、全文搜索或组件化内容让原生 Jekyll 明显不足时，再评估 MkDocs、Docusaurus 等工具。

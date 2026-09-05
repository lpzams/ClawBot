---
layout: page
title: Jenkins CI/CD 实操
---

## 1. 本课目标

用 Jenkins 把 ClawBot 的最小交付链跑起来：

```text
Git 仓库 -> Jenkins Checkout -> 自动测试 -> CLI 冒烟检查 -> 打包 -> 归档交付物
```

这里的 `Jenkinsfile` 放在仓库根目录，流水线配置和代码一起版本控制。

## 2. CI 和 CD 在这里分别是什么

- **CI（持续集成）**：每次构建检出代码，运行 `unittest` 和 CLI 冒烟检查。
- **CD（持续交付）**：只有通过检查的构建才执行 `Build` 和 `Deliver`，由 Jenkins 保存可下载的源码 ZIP。

当前项目没有线上服务或部署目标，因此不伪造生产部署步骤。以后有明确目标时，再在交付物基础上增加部署阶段。

## 3. 启动 Jenkins

如果已经安装 Jenkins，确保 Jenkins agent 上有 Git 和 Python 3.9+。

本地学习也可以使用 Docker：

```powershell
docker run --name clawbot-jenkins `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  jenkins/jenkins:lts-jdk17
```

首次启动后，在 `http://localhost:8080` 完成初始化向导。容器方式读取初始密码：

```powershell
docker exec clawbot-jenkins `
  cat /var/jenkins_home/secrets/initialAdminPassword
```

上面的官方 Jenkins 镜像主要提供 Jenkins 和 Java，通常没有 Python。仅用于本地练习时，可以临时安装构建工具；长期使用应配置独立的 Python agent：

```powershell
docker exec -u 0 clawbot-jenkins bash -lc "apt-get update && apt-get install -y git python3"
```

安装向导的推荐插件即可；本流水线只使用 Jenkins 自带的 Pipeline、SCM 和 Artifact Archiver 能力。

## 4. 创建 Pipeline 任务

1. 选择 **New Item**，类型选 **Pipeline**。
2. 在 **Pipeline** 中选择 **Pipeline script from SCM**。
3. SCM 选 **Git**，仓库填写 `https://github.com/lpzams/ClawBot.git`。
4. 分支填写 `*/main`，Script Path 保持 `Jenkinsfile`。
5. 保存后点击 **Build Now**。

如果使用私有仓库，在 SCM 配置中选择 Jenkins Credentials；不要把 Token 写进 `Jenkinsfile`。

## 5. 观察构建结果

流水线包含五个阶段：

| 阶段 | 作用 |
| --- | --- |
| `Checkout` | 从任务配置的 Git 仓库检出当前版本 |
| `Test` | 运行全部离线单元测试 |
| `Smoke` | 执行 `python -m clawbot "hello harness"` |
| `Build` | 用 Git 自带的 `git archive` 生成 `dist/clawbot-harness.zip` |
| `Deliver` | 调用 Jenkins 的 `archiveArtifacts` 归档 ZIP，形成可下载的构建产物 |

构建成功后，在构建详情的 **Artifacts** 中可以下载交付物。故意改坏一个测试，再点 **Build Now**，观察流水线在 `Test` 阶段变红；修复后重新构建应恢复为绿色。

## 6. 本地先验证同一条命令

Jenkins 执行的核心命令在本地也能运行：

```powershell
python -m unittest discover -s tests -v
python -m clawbot "hello harness"
```

这样可以先排除代码问题，再排查 Jenkins agent、凭据或 SCM 配置问题。

## 7. 下一步练习

1. 创建一个功能分支并提交一个会失败的测试，观察 Jenkins 的红灯。
2. 配置 GitHub Webhook，让 push 自动触发构建（Jenkins 必须能被 GitHub 访问）。
3. 有真实部署目标后，再新增需要人工确认的 `Deploy` 阶段；真实模型 API Key 应放在 Jenkins Credentials 中，并通过 `withCredentials` 注入。

# Steam 价格监控 - 部署与使用指南

本项目可以通过 GitHub Actions 每天自动获取自定义事件，并在达到您的预定的事件时通过 ntfy 或 Bark 发送手机推送通知。本项目现已支持通过 **ClawCloud Run** 自建 ntfy 服务器来保障隐私和推送的稳定性。

## 目录
1. [前期准备](#1-前期准备)
2. [使用 ClawCloud Run 部署 ntfy 私有服务](#2-使用-clawcloud-run-部署-ntfy-私有服务)
3. [配置 GitHub Actions 自动监控](#3-配置-github-actions-自动监控)
4. [配置手机端接收通知](#4-配置手机端接收通知)

---

### 1. 前期准备

1. **获取此项目:**
   在 GitHub 上 Fork 此项目到你的个人仓库中。

2. **获取事件内容:**
   打开events.txt设置事件内容。

---

### 2. 使用 ClawCloud Run 部署 ntfy 私有服务

为了确保推送完全在自己的掌控之中，推荐使用 ClawCloud Run 服务来快速免费地部署专属 ntfy 服务器：

1. 登录并进入 **ClawCloud Run** 控制台 (如果支持 Docker 镜像一键部署功能，则非常方便)。
2. 创建一个新服务（Web Service 或类似选项）：
   - 如果可以通过 Docker Hub 部署，请填写镜像名称：`binwiederhier/ntfy`（或者根据 ClawCloud Run 的文档指南部署 Docker 容器）。
   - 暴露容器的 `80` 端口。
   - 配置启动命令参数（可选，如果在需要身份验证的情况下可以添加对应的 config 文件参数，仅做基础推送可保持默认无状态运行）。
3. 部署成功后，ClawCloud Run 会为你生成一个公共域名，例如 `https://ntfy.your-clawcloud-app.com`。
4. **测试服务:** 在浏览器打开上述域名，如果能看到 ntfy 的网页界面，说明部署成功。请记下这个**完整 URL**。

*提示：为了防止别人推送至您的自建服务，请自行设定一个较长、较复杂的 Topic 字符串（如 `my_secret_steam_topic_2024`）。*

---

### 3. 配置 GitHub Actions 自动监控

现在你已经有自己的 ntfy 服务器了，接下来需要配置项目的推送环境变量：

1. 进入你 Fork 到个人账号的 GitHub 仓库页面。
2. 点击上方的 **Settings** -> 左侧菜单栏的 **Secrets and variables** -> **Actions**。
3. 点击 **New repository secret**，依次添加以下内容（注意：复制名称时请确保没有多余的空格，否则会报错）：
   
   - **名称**: `NTFY_SERVER`
     **值**: 刚才部署好的 ClawCloud Run 域名，如 `https://ntfy.your-clawcloud-app.com`
     *(注意：如果不配置此项，脚本默认使用公共的 https://ntfy.sh)*

   - **名称**: `NTFY_TOPIC`
     **值**: 你自定义的一个频道名称，仅允许使用字母、数字、破折号及下划线，例如：`my_secret_steam_topic_2024`
   
   - *(可选)* **名称**: `BARK_KEY`
     **值**: 如果你是 iOS 用户，也可以不使用 ntfy 而是使用 Bark，在这里填入 Bark APP 提供的专属 ID。

4. 启用 Actions：
   点击仓库上方的 **Actions** 选项卡，同意开启 Workflow（如果有绿色的 "I understand my workflows, go ahead and enable them" 按钮请点击）。代码会在每天北京时间上午 10:00 自动运行。

---

### 4. 配置手机端接收通知

#### 安卓 / iOS 端 (使用 ntfy App)
1. 在应用商店中下载并安装 **ntfy** 应用。
2. 打开 App，点击右下角的 **`+` (订阅主题)**。
3. 在上方输入框填写你自建服务器所在的完整 URL 及对应的 Topic，例如：
   `https://ntfy.your-clawcloud-app.com/my_secret_steam_topic_2024`
   *(或者点击右上角的设置将 Default Server 改为你的自建域名，然后在输入框仅输入 Topic 名字)*
4. 点击订阅 (Subscribe)。你现已可以在手机端正常接收到此项目发来的 Steam 降价通知！

#### 手动运行测试
回到 GitHub 仓库 -> **Actions** 菜单 -> 左侧点击 **Steam 价格自动监控** -> 在右侧点击 **Run workflow** -> 绿色的 **Run workflow** 按钮。稍等片刻，你的手机即可收到降价测试推送！

<div align="center">

# Kyouka 镜华 点歌机器人

![GitHub last commit](https://img.shields.io/github/last-commit/shuyangzhang/Kyouka?logo=github)
[![Release](https://img.shields.io/github/v/release/shuyangzhang/Kyouka)](https://github.com/shuyangzhang/Kyouka/releases)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=4648697392687523&style=3)](https://kaihei.co/oHRMIL)
![github stars](https://img.shields.io/github/stars/shuyangzhang/Kyouka?style=social)

Kyouka is a simple and powerful music bot for [KOOK](https://www.kookapp.cn/), it is easy to use and develop.
</div>

## Multilingual README

[English](./README.md) | 中文

## Contents

- [声明](#声明)
- [特性](#特性)
- [依赖](#依赖)
- [安装与部署](#安装与部署)
  - [基于docker部署](#基于docker部署)
  - [基于源码部署](#基于源码部署)
- [使用指南](#使用指南)
  - [快速上手](#快速上手)
  - [操作指令](#操作指令)
- [开发](#开发)
  - [贡献源码](#贡献源码)
  - [许可协议](#许可协议)
- [社区](#社区)
- [致谢](#致谢)

## 声明

本项目仅供Python爱好者学习使用, 若您基于本项目进行商业行为, 您将承担所有的法律责任, 作者与其他贡献者将不承担任何责任.  
本项目的所有API均来源于公开网络, 本项目无任何破解、盗版等行为, 如果您需要付费歌曲, 请自行前往各音乐平台付费获取.  
最后, 如有侵权, 请联系我删除该项目.  

## 特性

+ 多平台/多架构支持
+ 全异步设计
+ 容器化服务

## 依赖

+ Docker, 无论你基于docker部署还是基于源码部署都需要
+ Python >= 3.9, 如果你基于源码部署

## 安装与部署

### 基于docker部署

我强烈建议你选择基于docker部署, 因为它的配置方法很简单

1. 如果你还没有安装docker, 请根据你的操作系统参照以下指引进行安装

- [如何在Windows上安装Docker Destktop](https://docs.docker.com/desktop/windows/install/)
- [如何在MacOS上安装Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- [如何在Linux上安装Docker Desktop](https://docs.docker.com/desktop/linux/install/)

2. 确认你的docker是否已经就绪

```bash
docker version
```

3. 拉取[Kyouka 镜华 点歌机器人 镜像](https://hub.docker.com/r/shuyangzhang/kyouka) 和 [khl-voice SDK 镜像](https://hub.docker.com/r/shuyangzhang/khl-voice).
> Kyouka 镜华 点歌机器人 镜像提供 `linux/amd64` 和 `linux/arm64`的多平台支持  
> khl-voice SDK 镜像仅支持 `linux/amd64` 架构  

> 如果你的设备的架构是 `Windows/x86_64`, `macos/amd64`, `macos/arm64`, 请不要担心, 你可以在Docker Desktop上跨平台/跨架构运行这些镜像的容器.
```bash
docker pull shuyangzhang/kyouka
docker pull shuyangzhang/khl-voice
```

4. 从此代码仓库复制文件: `.env.template` 或克隆此代码仓库, 然后把它重命名为 `.env`.
```bash
git clone https://github.com/shuyangzhang/Kyouka.git
cd Kyouka
mv .env.template .env
```

5. 配置 `.env` 文件.
> 警告: 不要在配置项所在的行末添加任何无用的字符(包括但不限于 空格, 注释), 否则会导致Json解析失败
```bash
# 你的机器人的 token
TOKEN=1/MECxOTk=/zCX2VjWr6p+AmD84jL9asQ==

# 默认绑定的语音频道ID
CHANNEL=2559449076697969

# khl-voice sdk 镜像所生成的容器名, 此名称必须与Kyouka 镜华 点歌机器人 镜像生成的容器名不同
CONTAINER_NAME=kyouka-runner

# 管理员ID
ADMIN_USERS=["693543263"]

# 是否将日志保存到文件
FILE_LOGGER=false
```

6. 创建Kyouka 镜华 点歌机器人 镜像的容器
```bash
docker run --name kyouka-manager --env-file .env -v /var/run/docker.sock:/var/run/docker.sock --restart always -d shuyangzhang/kyouka
```

7. 此时你的机器人已开始运行, 在你的频道中发送 `/ping` 命令, 如果 Kyouka 镜华回复你消息了, 那么代表你的部署已经完成! 请尽情享用
> 警告: 请提前确定你已经授予了你的机器人阅读和发送消息的权限

### 基于源码部署

> 如果你正在使用 `Win10`/`Win11`, 我强烈建议在 WSL2 中执行以下的操作指令

> [如何在 Windows 上安装 WSL](https://docs.microsoft.com/en-us/windows/wsl/install)

1. 与 `基于docker部署` 的第一步相同, 安装docker并确认它是否已就绪 
```bash
docker version
```
> 请确定你可以执行 `docker` 命令而无需使用 `sudo`. 参考 [使用非root用户管理docker](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

2. 拉取 [khl-voice SDK 镜像](https://hub.docker.com/r/shuyangzhang/khl-voice)

```bash
docker pull shuyangzhang/khl-voice
```

3. 确认你的系统已安装 Python , 并且它的版本大于等于3.9

> [为你的操作系统安装 Python](https://www.python.org/downloads/)

```bash
python -V
```

4. 克隆此代码仓库, 然后将文件 `.env.template` 重命名为 `.env`
```bash
git clone https://github.com/shuyangzhang/Kyouka.git
cd Kyouka
mv .env.template .env
```

5. 配置 `.env` 文件
> 警告: 不要在配置项所在的行末添加任何无用的字符(包括但不限于 空格, 注释), 否则会导致Json解析失败
```bash
# 你的机器人的 token
TOKEN=1/MECxOTk=/zCX2VjWr6p+AmD84jL9asQ==

# 默认绑定的语音频道ID
CHANNEL=2559449076697969

# khl-voice sdk 镜像所生成的容器名, 此名称必须与Kyouka 镜华 点歌机器人 镜像生成的容器名不同
CONTAINER_NAME=kyouka-runner

# 管理员ID
ADMIN_USERS=["693543263"]

# 是否将日志保存到文件
FILE_LOGGER=false
```

6. 安装 Python 的依赖

```bash
# 安装 virtualenv, 然后生成 venv 虚拟环境用于安装 Kyouka 镜华 点歌机器人 的依赖
pip install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
virtualenv venv

# 激活 venv 虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

7. 启动 Kyouka 镜华 点歌机器人
```bash
python startup.py
```

8. 此时你的机器人已开始运行, 在你的频道中发送 `/ping` 命令, 如果 Kyouka 镜华回复你消息了, 那么代表你的部署已经完成! 请尽情享用
> 警告: 请提前确定你已经授予了你的机器人阅读和发送消息的权限

## 使用指南

### 快速上手

在你的频道发送 `/help` 命令, Kyouka 镜华 会教你如何使用

### 操作指令

- `/ping`: 检测 Kyouka 镜华 的在线状态
- `/help`: 获取帮助文档
- `/debug`: (需要管理员权限) debug开关
- `/comehere`: 绑定你所在的语音频道
- `/channel {channel_id}`: 通过语音频道的ID进行绑定
- `/play {music_name}`: 点歌
- `/search {keyword}`: 搜索网易云音乐中的歌曲
- `/msearch {keyword}`: 搜索咪咕音乐中的歌曲
- `/qsearch {keyword}`: 搜索QQ音乐中的歌曲
- `/osearch {keyword}`: 搜索osu!中的歌曲
- `/select {search_list_id}`: 将搜索结果中的歌曲加入播放列表
- `/bilibili {bilibili_video_url}`: 点播B站视频
- `/list`: 查看播放列表
- `/cut`: 切歌
- `/playlist {playlist_url}`: 导入网易云音乐歌单(前10首歌曲)
- `/radio {radio_url}`: 导入网易云音乐电台
- `/album {album_url}`: 导入网易云音乐专辑
- `/remove {list_id}`: 删除播放列表中的歌曲
- `/top {list_id}`: 将播放列表中的歌曲置顶

## 开发
### 贡献源码
- 使用 issue 进行记录  
通过创建 issue 来提出新功能请求, 反馈 BUG 或提出问题, 这也是与此项目开发者以及其他对该问题感兴趣的人建立联系的一个好方法

- 更换代码工作区  
通俗地说，你应该 fork 这个仓库，在你自己 fork 的仓库中进行修改，然后提交一个PR, 并且所有的 commit message 应该满足 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/)

### 许可协议
本项目是根据 [MIT 许可协议](./LICENSE)的条款进行授权的

## 社区
如果你需要帮助, 有任何意见和建议, 或者想一起开发 Kyouka 镜华, 欢迎加入我们的官方社区: https://kaihei.co/oHRMIL

## 致谢
本项目是基于 [khl.py](https://github.com/TWT233/khl.py) 进行开发的

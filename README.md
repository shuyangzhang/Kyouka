<div align="center">

# Kyouka 镜华 点歌机器人

![GitHub last commit](https://img.shields.io/github/last-commit/shuyangzhang/Kyouka?logo=github)
[![Release](https://img.shields.io/github/v/release/shuyangzhang/Kyouka)](https://github.com/shuyangzhang/Kyouka/releases)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=4648697392687523&style=3)](https://kaihei.co/oHRMIL)

Kyouka is a simple and powerful music bot for [KaiHeiLa](https://www.kaiheila.cn/), it is easy to use and develop.
</div>

## Multilingual README

[English](./README.md) | [中文](./README_ZH_CN.md)

## Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Installation and Deployment](#installation-and-deployment)
  - [Deploy based on docker service](#deploy-based-on-docker-service)
  - [Deploy based on source code](#deploy-based-on-source-code)
- [Usage](#usage)
  - [Quick Stark](#quick-start)
  - [Commands](#commands)
- [Development](#development)
  - [Contributing](#contributing)
  - [License](#license)
- [Community](#community)
- [Credits](#credits)

## Features

+ Multi platform
+ All async
+ Container as a service

## Dependencies

+ Docker, whether you are deploying based on docker or binaries.
+ Python >= 3.6, if you wanna to deploy it based on source code.

## Installation and Deployment

### Deploy based on docker service

I highly recommend you to deploy based on docker because it is easy to configure.

1. if you havn't install docker, please follow these instructions.

- [Install Docker Desktop on Windows](https://docs.docker.com/desktop/windows/install/)
- [Install Docker Desktop on Mac](https://docs.docker.com/desktop/mac/install/)
- [Install Docker Desktop on Linux](https://docs.docker.com/desktop/linux/install/)

2. check if your docker is ready.

```bash
docker version
```

3. pull the [Kyouka bot image](https://hub.docker.com/r/shuyangzhang/kyouka) and [khl-voice image](https://hub.docker.com/r/shuyangzhang/khl-voice).
> Kyouka bot image provides multi-architecture support for `linux/amd64` and `linux/arm64`.  
> khl-voice image only support for `linux/amd64` arch.  

> If you are using `Windows/x86_64`, `macos/amd64`, `macos/arm64`, don't worry about that, you can also run images targeted for a different architecture on Docker Desktop.
```bash
docker pull shuyangzhang/kyouka
docker pull shuyangzhang/khl-voice
```

4. copy the `.env.template` file from this repository or clone this repository, then rename it to `.env`.
```bash
git clone git@github.com:shuyangzhang/Kyouka.git
cd Kyouka
mv .env.template .env
```

5. configure the `.env` file.
```bash
TOKEN=1/MECxOTk=/zCX2VjWr6p+AmD84jL9asQ==      # your bot token
CHANNEL=2559449076697969                       # default voice channel
CONTAINER_NAME=kyouka-runner                   # the name of khl-voice sdk container, it should be different with your manager(bot) container name
ADMIN_USERS=["693543263"]                      # the admin user id list
FILE_LOGGER=false                              # the file_logger switch
```

6. create container for Kyouka bot.
```bash
docker run --name kyouka-manager --env-file .env -v /var/run/docker.sock:/var/run/docker.sock --restart always -d shuyangzhang/kyouka
```

7. now the bot in running, send a `/ping` command in your channel, if Kyouka reply you, that means your deployment is completed, enjoy!
> WARN: make sure that you have granted your bot read & send permissions.

### Deploy based on source code

> if you are using `Win10`/`Win11`, I highly recommend you to run these scripts in WSL2.

> [How to Install Linux on Windows with WSL](https://docs.microsoft.com/en-us/windows/wsl/install)

1. same to step 1 of `deploy based on docker service`, install docker and check if it is ready. 
```bash
docker version
```
> make sure that you can run `docker` command without `sudo`. seeing [Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

2. pull the [khl-voice image](https://hub.docker.com/r/shuyangzhang/khl-voice)

```bash
docker pull shuyangzhang/khl-voice
```

3. make sure you have installed `Python`, and its version >= 3.6

> [Download Python for your os](https://www.python.org/downloads/)

```bash
python -V
```

4. clone this repository, then rename `.env.template` file to `.env`.
```bash
git clone git@github.com:shuyangzhang/Kyouka.git
cd Kyouka
mv .env.template .env
```

5. configure the `.env` file.
```bash
TOKEN=1/MECxOTk=/zCX2VjWr6p+AmD84jL9asQ==      # your bot token
CHANNEL=2559449076697969                       # default voice channel
CONTAINER_NAME=kyouka-runner                   # the name of khl-voice sdk container, it should be different with your manager(bot) container name
ADMIN_USERS=["693543263"]                      # the admin user id list
FILE_LOGGER=false                              # the file_logger switch
```

6. install python dependencies.

```bash
# install vritualenv and initialize a venv for your bot
pip install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
virtualenv venv

# activate venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

7. run the Kyouka bot.
```bash
python startup.py
```

8. now the bot in running, send a `/ping` command in your channel, if Kyouka reply you, that means your deployment is completed, enjoy!
> WARN: make sure that you have granted your bot read & send permissions.

## Usage

### Quick Start

send a `/help` command in you channel, Kyouka will teach you how to use.

### Commands

- `/ping`: check whether Kyouka is alive.
- `/help`: get usage from Kyouka.
- `/debug`: (only for admin) the debug switch.
- `/comehere`: bind the voice channel you are in.
- `/channel {channel_id}`: bind the voice channel with id.
- `/play {music_name}`: add a music to play list.
- `/search {keyword}`: search music by keyword.
- `/select {search_list_id}`: select a music from search result, then add it to play list.
- `/bilibili {bilibili_video_url}`: add a video from Bilibili to play list.
- `/list`: check the play list.
- `/cut`: play the next music in play list.
- `/import {playlist_url}`: import a netease cloud music play list to Kyouka.
- `/remove {list_id}`: remove a music from play list.
- `/top {list_id}`: place a music at the top of play list.

## Development
### Contributing
- using the issue tracker  
Use the issue tracker to suggest feature requests, report bugs, and ask questions. This is also a great way to connect with the developers of the project as well as others who are interested in this solution.

- changing the code base  
Generally speaking, you should fork this repository, make changes in your own fork, and then submit a pull request. All commit messages should satisfy [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/)

### License
This project is licensed under the terms of the MIT license.

## Community
If you need help, have any comments and suggestions, or want to develop Kyouka together, feel free to join our official community: https://kaihei.co/oHRMIL

## Credits
This project is all based on [khl.py](https://github.com/TWT233/khl.py)

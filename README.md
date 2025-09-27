# Personal AI Assistant v2.0

## 1. 项目愿景

本项目旨在开发一个基于多智能体协作的个人AI助理系统。通过模拟专业团队（如GitHub助手、邮件处理器等）的工作方式，系统能主动为用户完成信息整理、工作同步、健康管理和日程规划等任务，最终成为一个安全、智能、个性化的个人数字中枢。

## 2. 核心功能

- **多智能体架构**: 基于 `CrewAI` 框架，系统由一个核心的“个人管家”智能体协调多个专业的智能体协同工作。
- **GitHub 工作助手**: 自动监控指定代码仓库的提交（Commits）、拉取请求（Pull Requests）和问题（Issues），并能生成摘要报告。
- **邮件处理器**: 能够安全地连接到IMAP邮件服务器，自动获取新邮件，为未来的情感分析、摘要和自动回复建议打下基础。
- **任务自动调度**: 每个智能体都可以根据 `user_config.yaml` 文件中的 cron 表达式进行定时调度，实现无人值守的自主运行。
- **安全数据存储**: 内置加密模块，确保所有敏感信息（如API密钥、邮件内容）在存储前都经过加密。
- **Web 仪表板 (进行中)**: 提供一个简单直观的前端界面，用于展示由各个智能体收集和分析的信息。

## 3. 技术架构

- **后端框架**: `FastAPI`
- **多智能体框架**: `CrewAI`
- **任务调度**: `APScheduler`
- **数据存储**: `SQLAlchemy` (ORM), `SQLite` (加密数据库), `ChromaDB` (向量数据库)
- **安全与加密**: `Cryptography`, `Passlib`
- **前端 (MVP)**: `Jinja2` (模板引擎), 原生 HTML/CSS/JS

## 4. 如何开始

### 4.1. 环境准备

- Python 3.10+
- `pip` 包管理器

### 4.2. 安装依赖

克隆本项目后，在项目根目录下运行以下命令来安装所有必需的依赖项：

```bash
pip install -r requirements.txt
```

### 4.3. 配置应用

1.  **找到配置文件**: 项目的所用配置都在 `config/user_config.yaml` 文件中。
2.  **填写占位符**: 打开该文件，您需要填写所有标记为 `YOUR_..._HERE` 的占位符。
    - **GitHub 助手**: 在 `agents.github_assistant` 部分，填入您的GitHub个人访问令牌 (`github_token`) 和您想要监控的仓库列表。
    - **邮件处理器**: 在 `agents.email_processor.email_accounts` 部分，填入您的邮箱地址和**应用专用密码** (`password`)。**注意**：为了安全，请不要使用您的主登录密码，而应为您要连接的服务（如Gmail）生成一个“应用专用密码”。

### 4.4. 运行项目

完成配置后，在项目根目录下运行以下命令来启动Web服务：

```bash
uvicorn main:app --reload
```

- `--reload` 参数会使服务器在您修改代码后自动重启，非常适合开发环境。

服务器启动后，您可以在浏览器中访问 `http://localhost:8000/dashboard` 来查看Web界面。

## 5. 项目结构

```
.
├── agents/         # 存放所有具体的智能体实现
├── api/            # FastAPI的API路由
├── config/         # 配置文件
├── core/           # 核心框架组件 (协调器, 基类等)
├── data/           # 数据存储目录 (数据库, 日志等)
├── static/         # 存放CSS, JS等静态文件
├── templates/      # 存放HTML模板
├── tools/          # 可重用的工具 (如API客户端)
├── main.py         # FastAPI应用主入口
└── README.md       # 本文件
```
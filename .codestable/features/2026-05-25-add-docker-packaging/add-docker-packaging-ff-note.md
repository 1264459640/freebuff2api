---
doc_type: feature-ff-note
feature: add-docker-packaging
date: 2026-05-25
requirement: ""
tags: [docker, deployment, orchestration]
---

## 做了什么
为项目添加 Docker 打包和编排能力，支持一键构建镜像和启动服务。

## 改了哪些
- `Dockerfile` — 基于 `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` 的单阶段构建，使用 `uv sync --frozen` 安装依赖，入口为 `uv run freebuff2api`
- `docker-compose.yml` — 单服务编排，映射 8000 端口，加载 `.env` 环境变量，`restart: unless-stopped`
- `.dockerignore` — 排除 `__pycache__`、`.venv`、`.env`、`.git`、`.codestable/` 等构建无关文件

## 怎么验证的
- `docker build .` 验证镜像构建通过
- `docker compose up` 验证服务启动并响应 `/healthz`

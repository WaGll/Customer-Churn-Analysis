#!/usr/bin/env python3
"""
FastAPI 预测服务入口

启动方式:
    python run_api.py
    python run_api.py --port 8080
    python run_api.py --host 0.0.0.0 --port 8000
"""

import argparse
import sys
import os

# 确保 src 可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    parser = argparse.ArgumentParser(description="客户流失预测 API 服务")
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址 (默认 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="绑定端口 (默认 8000)")
    parser.add_argument("--reload", action="store_true", help="开发模式热重载")
    args = parser.parse_args()

    import uvicorn

    print(f"🚀 启动客户流失预测服务 http://{args.host}:{args.port}")
    print(f"📖 API 文档: http://{args.host}:{args.port}/docs")
    print(f"🔍 健康检查: http://{args.host}:{args.port}/health")

    uvicorn.run(
        "src.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()

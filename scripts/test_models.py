#!/usr/bin/env python3
"""
DeerFlow 模型路由测试脚本

用途：
  - 列出所有可用模型
  - 测试指定模型的可用性
  - 发送测试消息到特定模型
  - 验证模型能力（思维、视觉等）

使用：
  python scripts/test_models.py list
  python scripts/test_models.py test gpt-4
  python scripts/test_models.py send claude-3-5-sonnet "Hello, are you Claude?"
"""

import argparse
import sys
import json
import os
from typing import Optional

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:2026/api"
DEFAULT_TIMEOUT = 30

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{msg}{Colors.RESET}")

def list_models() -> bool:
    """列出所有可用模型"""
    try:
        print_header("📋 Available Models")
        
        response = requests.get(f"{BASE_URL}/models", timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('models', [])
        
        if not models:
            print_error("No models configured!")
            return False
        
        print_info(f"Total models: {len(models)}\n")
        
        for i, model in enumerate(models, 1):
            # 第一个模型是默认
            is_default = " [DEFAULT]" if i == 1 else ""
            print(f"{Colors.BOLD}{i}. {model['display_name']}{is_default}{Colors.RESET}")
            print(f"   Name: {model['name']}")
            
            if model.get('description'):
                print(f"   Description: {model['description']}")
            
            capabilities = []
            if model.get('supports_thinking'):
                capabilities.append("🧠 Thinking")
            if model.get('supports_vision'):
                capabilities.append("👁️ Vision")
            if model.get('supports_reasoning_effort'):
                capabilities.append("🔍 Reasoning")
            
            if capabilities:
                print(f"   Capabilities: {', '.join(capabilities)}")
            print()
        
        if data.get('token_usage', {}).get('enabled'):
            print_info("Token usage tracking is ENABLED")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Make sure DeerFlow is running: make dev")
        return False
    except Exception as e:
        print_error(f"Failed to list models: {e}")
        return False

def test_model(model_name: str) -> bool:
    """测试特定模型的可用性"""
    try:
        print_header(f"🧪 Testing Model: {model_name}")
        
        response = requests.get(f"{BASE_URL}/models/{model_name}", timeout=DEFAULT_TIMEOUT)
        
        if response.status_code == 404:
            print_error(f"Model '{model_name}' not found")
            list_models()
            return False
        
        response.raise_for_status()
        model = response.json()
        
        print_success(f"Model found: {model['display_name']}")
        
        print(f"\nModel Details:")
        print(f"  ID: {model['name']}")
        print(f"  Provider Model: {model['model']}")
        
        if model.get('description'):
            print(f"  Description: {model['description']}")
        
        print(f"\nCapabilities:")
        print(f"  Thinking Mode: {'✓' if model.get('supports_thinking') else '✗'}")
        print(f"  Vision Support: {'✓' if model.get('supports_vision') else '✗'}")
        print(f"  Reasoning Effort: {'✓' if model.get('supports_reasoning_effort') else '✗'}")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        return False
    except Exception as e:
        print_error(f"Failed to test model: {e}")
        return False

def send_message(model_name: str, message: str, thinking_enabled: bool = False) -> bool:
    """发送测试消息到指定模型"""
    try:
        print_header(f"💬 Sending Message to: {model_name}")
        print(f"Message: {message}")
        if thinking_enabled:
            print(f"Thinking Mode: {Colors.GREEN}Enabled{Colors.RESET}")
        
        # 首先创建一个线程
        print_info("Creating thread...")
        thread_response = requests.post(
            f"{BASE_URL}/langgraph/threads",
            json={"metadata": {}},
            timeout=DEFAULT_TIMEOUT
        )
        thread_response.raise_for_status()
        thread_id = thread_response.json()['thread_id']
        print_success(f"Thread created: {thread_id}")
        
        # 发送运行请求
        print_info("Sending message...")
        run_response = requests.post(
            f"{BASE_URL}/langgraph/threads/{thread_id}/runs",
            json={
                "input": {
                    "messages": [
                        {"role": "user", "content": message}
                    ]
                },
                "config": {
                    "recursion_limit": 100,
                    "configurable": {
                        "model_name": model_name,
                        "thinking_enabled": thinking_enabled
                    }
                },
                "stream_mode": ["values"]
            },
            timeout=DEFAULT_TIMEOUT
        )
        run_response.raise_for_status()
        
        print_success("Message sent successfully!")
        print(f"\nResponse Status: {run_response.status_code}")
        
        # 如果是流式响应，显示第一条消息
        if run_response.headers.get('content-type') == 'text/event-stream':
            print("\nStreaming response (first event):")
            for line in run_response.iter_lines():
                if line and line.startswith(b'data:'):
                    data = line[5:].strip()
                    if data:
                        try:
                            event_data = json.loads(data)
                            if 'messages' in event_data:
                                print(Colors.GREEN + "Response received!" + Colors.RESET)
                                break
                        except:
                            pass
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print_error(f"Model '{model_name}' not found")
        else:
            print_error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print_error(f"Failed to send message: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="DeerFlow Model Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_models.py list                        # 列出所有模型
  python scripts/test_models.py test gpt-4                  # 测试 GPT-4
  python scripts/test_models.py send claude-3-5-sonnet "你好"  # 发送消息
  python scripts/test_models.py send deepseek-r1 "复杂问题" --thinking  # 启用思维
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list 命令
    subparsers.add_parser('list', help='List all available models')
    
    # test 命令
    test_parser = subparsers.add_parser('test', help='Test a specific model')
    test_parser.add_argument('model_name', help='Model name to test')
    
    # send 命令
    send_parser = subparsers.add_parser('send', help='Send a message to a model')
    send_parser.add_argument('model_name', help='Model name to use')
    send_parser.add_argument('message', help='Message to send')
    send_parser.add_argument(
        '--thinking',
        action='store_true',
        help='Enable thinking mode (if supported)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    success = False
    if args.command == 'list':
        success = list_models()
    elif args.command == 'test':
        success = test_model(args.model_name)
    elif args.command == 'send':
        success = send_message(args.model_name, args.message, args.thinking)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())

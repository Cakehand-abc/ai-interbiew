#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API 调试工具
用于诊断代码与Dify API交互的问题
"""

import requests
import json
import time


class DifyDebugger:
    def __init__(
        self, base_url="http://localhost/v1", api_key="app-DkiRQ4jpXQARlOhJfA5t12lb"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.conversation_id = None

    def test_request(self, query, user_id="debug-user", include_conversation_id=False):
        """测试单个请求并详细记录信息"""

        print(f"\n{'='*60}")
        print(f"🔍 测试请求: {query}")
        print(f"{'='*60}")

        # 构建请求参数
        payload = {
            "query": query,
            "inputs": {},
            "response_mode": "blocking",
            "user": user_id,
        }

        if include_conversation_id and self.conversation_id:
            payload["conversation_id"] = self.conversation_id
            print(f"📋 使用会话ID: {self.conversation_id}")

        print(f"📤 请求参数:")
        for key, value in payload.items():
            if key == "conversation_id":
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {value}")

        print(f"\n🌐 请求URL: {self.base_url}/chat-messages")
        print(f"🔑 认证头: {self.headers['Authorization'][:20]}...")

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat-messages",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            end_time = time.time()

            print(f"\n⏱️  请求耗时: {end_time - start_time:.2f}秒")
            print(f"📊 状态码: {response.status_code}")
            print(f"📄 响应头: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 响应成功:")
                print(f"   响应键: {list(result.keys())}")

                if "conversation_id" in result:
                    self.conversation_id = result["conversation_id"]
                    print(f"   🆔 会话ID: {self.conversation_id}")

                if "answer" in result:
                    print(f"   💬 AI回复: {result['answer'][:200]}...")

                return result
            else:
                print(f"❌ 请求失败:")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data}")
                except:
                    print(f"   响应文本: {response.text[:500]}")
                return None

        except requests.exceptions.Timeout:
            print(f"⏰ 请求超时 (60秒)")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"🔗 连接错误: {str(e)}")
            return None
        except Exception as e:
            print(f"💥 其他错误: {str(e)}")
            return None

    def run_debug_sequence(self):
        """运行完整的调试序列"""
        print("🚀 开始Dify API调试序列")

        # 测试1: 简单问候
        result1 = self.test_request("你好")

        # 测试2: 面试请求（不带会话ID）
        result2 = self.test_request("我要面试Java开发工程师")

        # 测试3: 面试请求（带会话ID）
        if self.conversation_id:
            result3 = self.test_request("Java反射机制是什么？", include_conversation_id=True)
        else:
            print("\n⚠️  没有可用的会话ID，跳过带会话ID的测试")
            result3 = None

        # 测试4: 对比不同参数格式
        print(f"\n{'='*60}")
        print("🔍 测试不同参数格式")
        print(f"{'='*60}")

        # 测试最小参数格式
        minimal_payload = {"query": "Java开发工程师面试", "user": "test-user"}

        print(f"📤 最小参数格式测试:")
        try:
            response = requests.post(
                f"{self.base_url}/chat-messages",
                headers=self.headers,
                json=minimal_payload,
                timeout=30,
            )
            print(f"📊 状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功: {result.get('answer', '无回复')[:100]}...")
            else:
                print(f"❌ 失败: {response.text[:200]}")
        except Exception as e:
            print(f"💥 错误: {str(e)}")

        return result1, result2, result3


def main():
    """主函数"""
    print("🔧 Dify API 调试工具")
    print("=" * 60)

    # 创建调试器
    debugger = DifyDebugger()

    # 运行调试序列
    results = debugger.run_debug_sequence()

    print(f"\n{'='*60}")
    print("📊 调试总结")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r is not None)
    total_count = len([r for r in results if r is not None])

    print(f"✅ 成功请求: {success_count}/{total_count}")
    print(f"🆔 最终会话ID: {debugger.conversation_id}")

    if debugger.conversation_id:
        print("✅ 会话管理正常")
    else:
        print("⚠️  会话管理可能有问题")


if __name__ == "__main__":
    main()

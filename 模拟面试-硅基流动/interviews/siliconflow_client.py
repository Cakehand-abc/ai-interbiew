import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class SiliconFlowClient:
    """硅基流动 API 客户端"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1"
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        return session

    def get_chat_completion(self, messages, model="deepseek-ai/DeepSeek-V3.1-Terminus"):
        """获取聊天回复"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 检查是否包含要求输出 JSON 的提示
        response_format = None
        if messages and any("JSON" in msg.get("content", "") for msg in messages):
            response_format = {"type": "json_object"}
            
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,      
            "top_p": 0.5,           
            "top_k": 20,              
            "max_tokens": 4000,        
            "frequency_penalty": 0.6, 
            "stream": False,         
            "enable_thinking": False 
        }
        
        if response_format:
            data["response_format"] = response_format

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=120  
            )
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.Timeout:
            print("调用硅基流动 API 时发生超时")
            return {"error": "API 请求在 120 秒后超时。"}
        except requests.exceptions.RequestException as e:
            print(f"调用硅基流动 API 时出错: {e}")
            return {"error": str(e)}

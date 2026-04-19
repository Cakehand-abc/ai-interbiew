import os
import django
import sys
import json
import uuid

sys.path.append('e:\\模拟面试-硅基流动')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interview_backend.settings")
django.setup()

from django.test import RequestFactory
from interviews.views import chat

factory = RequestFactory()

def simulate_interview():
    print("\n--- 开始模拟面试 ---")
    session_id = ""
    job_name = "Python后端开发"
    
    # 1. 开场
    request = factory.post('/api/chat', data=json.dumps({"message": job_name}), content_type='application/json')
    response = chat(request)
    data = json.loads(response.content)
    session_id = data.get("session_id")
    print(f"【开场AI】: {data.get('message')}")
    print(f"Session ID: {session_id}\n")

    answers = [
        "你好，我是一名Python后端开发，熟练掌握Django和FastAPI，有高并发经验。",
        "我会使用连接池、索引优化、Redis缓存等方式优化数据库查询。",
        "我会使用全局异常处理中间件拦截异常，并返回标准化的JSON响应。",
        "我会使用Celery和RabbitMQ实现异步任务队列，削峰填谷。",
        "我会采用RESTful规范，使用复数名词，合理设计HTTP方法和状态码。",
        "最后补充一下，我会写单元测试。"
    ]

    for i, answer in enumerate(answers):
        print(f"【第 {i+1} 题 用户回答】: {answer}")
        request = factory.post('/api/chat', data=json.dumps({
            "message": answer,
            "session_id": session_id
        }), content_type='application/json')
        response = chat(request)
        data = json.loads(response.content)
        
        print(f"【AI回复】: {data.get('message')}")
        if data.get("interview_ended"):
            print(f"\n--- 面试在第 {i+1} 题正常结束！ ---")
            break
        print("-" * 50)

if __name__ == "__main__":
    simulate_interview()

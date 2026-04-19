import json
from typing import List, Dict, Any
import os


class FileUtils:
    @staticmethod
    def read_json(file_path: str) -> List[Dict[str, Any]]:
        """读取JSON文件（批量岗位数据）"""
        if not os.path.exists(file_path):
            print(f"⚠ 文件不存在：{file_path}")
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取JSON失败：{e}")
            return []

    @staticmethod
    def write_json(data: List[Dict[str, Any]], file_path: str):
        """写入JSON文件（导出数据）"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 写入JSON失败：{e}")

    @staticmethod
    def parse_document_to_json(document_content: str) -> List[Dict[str, Any]]:
        """解析原始文档内容为JSON格式（适配文档分隔符）"""
        jobs = []
        # 按企业名称拆分多条数据（文档中每条数据以"企业名称："开头）
        job_strings = [s.strip() for s in document_content.split("企业名称：") if s.strip()]
        for job_str in job_strings:
            job_dict = {}
            # 拆分字段（适配"key：value"格式）
            fields = job_str.split("，")
            for field in fields:
                if "：" in field:
                    key, value = field.split("：", 1)
                    job_dict[key.strip()] = value.strip()
            if job_dict:
                jobs.append(job_dict)
        return jobs

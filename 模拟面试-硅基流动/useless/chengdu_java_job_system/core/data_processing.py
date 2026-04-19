import pandas as pd
from typing import Dict, Any, List
from config.db_config import FIELD_MAP


class DataProcessor:
    @staticmethod
    def clean_job_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗单条岗位数据（格式标准化、异常值处理）"""
        cleaned_data = {}

        # 字段映射与空值填充
        for raw_key, target_key in FIELD_MAP.items():
            cleaned_data[target_key] = raw_data.get(raw_key, "")

        # 薪资处理（异常值转为0）
        cleaned_data["salary_low"] = DataProcessor._process_salary(raw_data.get("最低薪资"))
        cleaned_data["salary_high"] = DataProcessor._process_salary(
            raw_data.get("最高薪资")
        )

        # 发布时间格式化
        cleaned_data["release_time"] = DataProcessor._process_time(
            raw_data.get("岗位发布时间", "")
        )

        # 补充默认来源
        if not cleaned_data["source"]:
            cleaned_data["source"] = "成都岗位文档"

        return cleaned_data

    @staticmethod
    def _process_salary(salary: Any) -> int:
        """薪资处理（转换为整数，异常值返回0）"""
        try:
            return (
                int(salary) if salary and str(salary).strip() not in ["0", "无"] else 0
            )
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _process_time(time_str: str) -> str:
        """时间格式化（统一转为YYYY-MM-DD HH:MM:SS）"""
        if not time_str:
            return ""
        try:
            return pd.to_datetime(time_str).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ""

    @staticmethod
    def batch_clean_jobs(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量清洗岗位数据"""
        return [DataProcessor.clean_job_data(job) for job in raw_jobs]

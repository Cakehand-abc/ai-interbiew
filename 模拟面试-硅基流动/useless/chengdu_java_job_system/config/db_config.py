import sqlite3
from typing import Dict, Tuple

# 数据库连接配置
DB_NAME = "chengdu_java_jobs.db"
DB_TIMEOUT = 30.0

# 字段映射（文档字段→数据库字段）
FIELD_MAP: Dict[str, str] = {
    "企业名称": "company_name",
    "岗位名称": "job_name",
    "最低薪资": "salary_low",
    "最高薪资": "salary_high",
    "工作城市": "work_city",
    "工作区域": "work_district",
    "工作街道": "work_street",
    "工作类型": "work_type",
    "学历要求": "education_require",
    "工作年限要求": "work_experience",
    "岗位要求": "job_require",
    "岗位职责": "job_duty",
    "岗位发布时间": "release_time",
    "企业规模": "company_scale",
    "企业性质": "company_nature",
    "source": "source",
}

# 数据库表结构SQL
CREATE_TABLE_SQLS: Tuple[str, ...] = (
    # 岗位信息表
    """
    CREATE TABLE IF NOT EXISTS job_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        job_name TEXT,
        salary_low INTEGER DEFAULT 0,
        salary_high INTEGER DEFAULT 0,
        work_city TEXT,
        work_district TEXT,
        work_street TEXT,
        work_type TEXT,
        education_require TEXT,
        work_experience TEXT,
        job_require TEXT,
        job_duty TEXT,
        release_time TEXT,
        company_scale TEXT,
        company_nature TEXT,
        source TEXT DEFAULT '成都岗位文档',
        cid INTEGER NULL
    )
    """,
    # 企业信息表
    """
    CREATE TABLE IF NOT EXISTS company_info (
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE,
        company_scale TEXT,
        company_nature TEXT,
        source TEXT
    )
    """,
)


def get_db_connection():
    """获取数据库连接（带超时配置）"""
    conn = sqlite3.connect(DB_NAME, timeout=DB_TIMEOUT)
    # 启用字典游标，查询结果返回字典格式
    conn.row_factory = sqlite3.Row
    return conn

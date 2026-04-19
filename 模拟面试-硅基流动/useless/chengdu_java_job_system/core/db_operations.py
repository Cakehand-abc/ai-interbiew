from config.db_config import get_db_connection, CREATE_TABLE_SQLS
from typing import Dict, List, Optional, Any


class DBOperations:
    @staticmethod
    def init_tables():
        """初始化所有数据库表"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for sql in CREATE_TABLE_SQLS:
                cursor.execute(sql)
            conn.commit()
            print("✅ 数据库表初始化成功")
        except Exception as e:
            conn.rollback()
            print(f"❌ 表初始化失败：{e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def insert_job(data: Dict[str, any]) -> bool:
        """插入单条岗位数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 获取表结构信息
            cursor.execute("PRAGMA table_info(job_info)")
            table_columns = [row[1] for row in cursor.fetchall()]

            # 过滤无效字段，仅保留表中存在的字段
            valid_keys = [k for k in data.keys() if k in table_columns or k in ["cid"]]
            values = [data[k] for k in valid_keys]
            placeholders = ",".join(["?"] * len(valid_keys))

            sql = (
                f"INSERT INTO job_info ({','.join(valid_keys)}) VALUES ({placeholders})"
            )
            cursor.execute(sql, values)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ 岗位插入失败：{e} - 岗位：{data.get('job_name')}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def batch_insert_jobs(jobs: List[Dict[str, Any]]) -> int:
        """批量插入岗位数据"""
        conn = get_db_connection()
        cursor = conn.cursor()
        inserted_count = 0

        try:
            # 获取表结构信息
            cursor.execute("PRAGMA table_info(job_info)")
            table_columns = [row[1] for row in cursor.fetchall()]

            for job in jobs:
                # 过滤无效字段，仅保留表中存在的字段
                valid_keys = [
                    k for k in job.keys() if k in table_columns or k in ["cid"]
                ]
                values = [job[k] for k in valid_keys]
                placeholders = ",".join(["?"] * len(valid_keys))

                sql = f"INSERT INTO job_info ({','.join(valid_keys)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                inserted_count += 1

            conn.commit()
            return inserted_count

        except Exception as e:
            conn.rollback()
            print(f"❌ 批量插入失败：{e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def insert_company(data: Dict[str, any]) -> bool:
        """插入单条企业数据（忽略重复）"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """
            INSERT OR IGNORE INTO company_info (company_name, company_scale, company_nature, source)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(
                sql,
                [
                    data.get("company_name", ""),
                    data.get("company_scale", ""),
                    data.get("company_nature", ""),
                    data.get("source", "成都岗位文档"),
                ],
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ 企业插入失败：{e} - 企业：{data.get('company_name')}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_job_cid():
        """关联更新岗位表cid（通过企业名称匹配）"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """
            UPDATE job_info
            SET cid = (SELECT cid FROM company_info WHERE company_info.company_name = job_info.company_name)
            WHERE cid IS NULL
            """
            cursor.execute(sql)
            conn.commit()
            print(f"✅ 关联更新完成：{cursor.rowcount} 条岗位绑定企业cid")
        except Exception as e:
            conn.rollback()
            print(f"❌ cid更新失败：{e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def export_jobs(output_path: str):
        """导出岗位数据到JSON"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM job_info")
            jobs = [dict(row) for row in cursor.fetchall()]
            from utils.file_utils import FileUtils

            FileUtils.write_json(jobs, output_path)
            print(f"✅ 导出成功：{len(jobs)} 条数据保存到 {output_path}")
        except Exception as e:
            print(f"❌ 导出失败：{e}")
        finally:
            cursor.close()
            conn.close()

import json
import os
from typing import List, Dict, Any
from utils.file_utils import FileUtils


class TxtToJsonConverter:
    @staticmethod
    def parse_txt_line(line: str) -> Dict[str, Any]:
        """解析单行TXT数据为字典"""
        try:
            # 按逗号分割字段
            fields = line.strip().split(",")
            job_data = {}

            for field in fields:
                if "：" in field:
                    key, value = field.split("：", 1)
                    job_data[key.strip()] = value.strip()

            # 处理薪资字段
            if "最低薪资" in job_data:
                try:
                    job_data["最低薪资"] = int(job_data["最低薪资"])
                except:
                    job_data["最低薪资"] = 0

            if "最高薪资" in job_data:
                try:
                    job_data["最高薪资"] = int(job_data["最高薪资"])
                except:
                    job_data["最高薪资"] = 0

            # 添加默认来源
            if "source" not in job_data:
                job_data["source"] = "Boss直聘"

            return job_data
        except Exception as e:
            print(f"解析行失败: {line[:50]}... - 错误: {e}")
            return {}

    @staticmethod
    def convert_txt_file(txt_file_path: str, json_file_path: str) -> int:
        """将单个TXT文件转换为JSON文件"""
        try:
            with open(txt_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            jobs = []
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    job_data = TxtToJsonConverter.parse_txt_line(line)
                    if job_data:
                        jobs.append(job_data)

            # 保存为JSON
            FileUtils.write_json(jobs, json_file_path)
            print(f"✅ 转换成功: {txt_file_path} -> {json_file_path} ({len(jobs)} 条数据)")
            return len(jobs)

        except Exception as e:
            print(f"❌ 转换失败: {txt_file_path} - 错误: {e}")
            return 0

    @staticmethod
    def batch_convert_txt_folder(txt_folder: str, output_folder: str) -> int:
        """批量转换TXT文件夹中的所有文件"""
        total_jobs = 0

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for filename in os.listdir(txt_folder):
            if filename.endswith(".txt"):
                txt_path = os.path.join(txt_folder, filename)
                json_filename = filename.replace(".txt", ".json")
                json_path = os.path.join(output_folder, json_filename)

                count = TxtToJsonConverter.convert_txt_file(txt_path, json_path)
                total_jobs += count

        print(f"\n🎉 批量转换完成! 共转换 {total_jobs} 条岗位数据")
        return total_jobs


def main():
    """主函数 - 用于测试和手动转换"""
    # 转换单个文件测试
    # TxtToJsonConverter.convert_txt_file(
    #     "e:\\寒假项目\\jobs\\jobs_1.txt",
    #     "e:\\寒假项目\\chengdu_java_job_system\\jobs_1.json"
    # )

    # 批量转换所有文件
    TxtToJsonConverter.batch_convert_txt_folder(
        "e:\\寒假项目\\jobs", "e:\\寒假项目\\chengdu_java_job_system\\converted_jobs"
    )


if __name__ == "__main__":
    main()

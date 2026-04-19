#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT转CSV转换器
将jobs文件夹中的所有TXT文件分割为多个CSV文件，每个文件包含130条数据
"""

import os
import csv
import re
from typing import List, Dict, Set
from datetime import datetime


class TxtToCsvConverter:
    def __init__(
        self,
        txt_folder: str = "jobs",
        output_prefix: str = "jobs",
        batch_size: int = 130,
    ):
        self.txt_folder = txt_folder
        self.output_prefix = output_prefix
        self.batch_size = batch_size
        self.all_jobs = []
        self.field_names: Set[str] = set()

    def parse_txt_line(self, line: str) -> Dict[str, str]:
        """解析单行TXT数据为字典"""
        job_data = {}

        try:
            # 按逗号分割字段
            fields = line.strip().split(",")

            for field in fields:
                if "：" in field:
                    # 分割键值对
                    key_value = field.split("：", 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        job_data[key] = value

            # 处理薪资字段，确保是数字
            if "最低薪资" in job_data:
                job_data["最低薪资"] = re.sub(r"[^0-9]", "", job_data["最低薪资"]) or "0"

            if "最高薪资" in job_data:
                job_data["最高薪资"] = re.sub(r"[^0-9]", "", job_data["最高薪资"]) or "0"

            # 添加默认来源
            if "source" not in job_data:
                job_data["source"] = "Boss直聘"

            return job_data

        except Exception as e:
            print(f"❌ 解析行失败: {line[:50]}... - 错误: {e}")
            return {}

    def process_single_file(self, file_path: str) -> int:
        """处理单个TXT文件"""
        job_count = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                job_data = self.parse_txt_line(line)
                if job_data:
                    self.all_jobs.append(job_data)
                    self.field_names.update(job_data.keys())
                    job_count += 1

            print(f"✅ 处理完成: {os.path.basename(file_path)} - {job_count} 条数据")
            return job_count

        except Exception as e:
            print(f"❌ 处理文件失败: {file_path} - 错误: {e}")
            return 0

    def process_all_files(self) -> int:
        """处理所有TXT文件"""
        total_jobs = 0

        if not os.path.exists(self.txt_folder):
            print(f"❌ 文件夹不存在: {self.txt_folder}")
            return 0

        # 获取所有TXT文件并按数字排序
        txt_files = []
        for filename in os.listdir(self.txt_folder):
            if filename.endswith(".txt"):
                # 提取文件中的数字用于排序
                match = re.search(r"(\d+)", filename)
                if match:
                    num = int(match.group(1))
                    txt_files.append((num, filename))

        # 按数字排序
        txt_files.sort(key=lambda x: x[0])

        print(f"📁 开始处理文件夹: {self.txt_folder}")
        print(f"📋 找到 {len(txt_files)} 个TXT文件")

        for num, filename in txt_files:
            file_path = os.path.join(self.txt_folder, filename)
            job_count = self.process_single_file(file_path)
            total_jobs += job_count

        print(f"\n📊 总计处理: {total_jobs} 条岗位数据")
        return total_jobs

    def save_to_csv_batch(self) -> bool:
        """批量保存数据到多个CSV文件"""
        if not self.all_jobs:
            print("❌ 没有数据可保存")
            return False

        try:
            # 确定字段顺序（按常见字段排序）
            preferred_order = [
                "岗位名称",
                "企业名称",
                "最低薪资",
                "最高薪资",
                "工作城市",
                "工作区域",
                "工作街道",
                "学历要求",
                "工作年限要求",
                "企业规模",
                "企业性质",
                "工作类型",
                "岗位发布时间",
                "岗位要求",
                "source",
            ]

            # 确保所有字段都在field_names中
            field_names = list(self.field_names)

            # 按偏好顺序排序字段
            ordered_fields = []
            for field in preferred_order:
                if field in field_names:
                    ordered_fields.append(field)
                    field_names.remove(field)

            # 添加剩余的字段
            ordered_fields.extend(sorted(field_names))

            # 计算需要多少个文件
            total_jobs = len(self.all_jobs)
            num_files = (total_jobs + self.batch_size - 1) // self.batch_size

            print(f"📊 总数据量: {total_jobs} 条记录")
            print(f"📁 将分割为 {num_files} 个文件，每个文件最多 {self.batch_size} 条记录")

            # 创建输出文件夹
            output_folder = "split_csv_files"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            total_size = 0
            file_count = 0

            # 分批保存数据
            for i in range(num_files):
                start_idx = i * self.batch_size
                end_idx = min((i + 1) * self.batch_size, total_jobs)
                batch_jobs = self.all_jobs[start_idx:end_idx]

                # 生成文件名
                file_number = i + 1
                output_file = f"{self.output_prefix}_{file_number:02d}.csv"
                output_path = os.path.join(output_folder, output_file)

                with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=ordered_fields)
                    writer.writeheader()

                    for job in batch_jobs:
                        # 确保每行数据包含所有字段
                        row = {field: job.get(field, "") for field in ordered_fields}
                        writer.writerow(row)

                file_size = os.path.getsize(output_path) / 1024  # KB
                total_size += file_size
                file_count += 1

                print(
                    f"✅ 文件 {file_number:2d}: {output_file} - {len(batch_jobs)} 条记录 ({file_size:.1f} KB)"
                )

            print(f"\n📊 分割完成!")
            print(f"📁 输出文件夹: {output_folder}")
            print(f"📋 文件数量: {file_count} 个")
            print(f"📊 总文件大小: {total_size:.1f} KB")
            print(f"📋 字段数量: {len(ordered_fields)} 个")

            # 显示字段列表
            print("\n📋 字段列表:")
            for i, field in enumerate(ordered_fields, 1):
                print(f"  {i:2d}. {field}")

            return True

        except Exception as e:
            print(f"❌ 保存CSV文件失败: {e}")
            return False

    def show_sample_data(self, count: int = 5):
        """显示样本数据"""
        if not self.all_jobs:
            print("❌ 没有数据可显示")
            return

        print(f"\n📋 前 {count} 条样本数据:")
        print("-" * 80)

        for i, job in enumerate(self.all_jobs[:count], 1):
            print(f"第 {i} 条记录:")
            for key, value in job.items():
                # 限制长文本显示
                if key == "岗位要求" and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {key}: {value}")
            print("-" * 80)

    def convert(self) -> bool:
        """执行完整的转换流程"""
        print("🚀 开始TXT转CSV转换...")
        print("=" * 50)

        # 处理所有文件
        total_jobs = self.process_all_files()

        if total_jobs == 0:
            print("❌ 没有找到有效数据")
            return False

        # 显示样本数据
        self.show_sample_data(3)

        # 批量保存为多个CSV文件
        success = self.save_to_csv_batch()

        if success:
            print("\n🎉 转换完成!")
            print("=" * 50)

        return success


def main():
    """主函数"""
    converter = TxtToCsvConverter(
        txt_folder="jobs", output_prefix="jobs", batch_size=130
    )

    success = converter.convert()

    if success:
        print("✅ 转换成功完成!")
        print(f"📁 输出文件夹: split_csv_files")
        print(f"📊 总数据量: {len(converter.all_jobs)} 条记录")
        print(f"� 文件数量: {(len(converter.all_jobs) + 129) // 130} 个文件")
    else:
        print("❌ 转换失败")

    return success


if __name__ == "__main__":
    main()

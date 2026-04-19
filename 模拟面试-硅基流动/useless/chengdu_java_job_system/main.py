from core.db_operations import DBOperations
from core.data_processing import DataProcessor
from utils.file_utils import FileUtils
from utils.txt_to_json_converter import TxtToJsonConverter
from typing import List
import os


def single_job_test():
    """单条数据测试"""
    test_job = {
        "企业名称": "北京银丰新融科技开发有限公司",
        "岗位名称": "java开发工程师",
        "最低薪资": 8001,
        "最高薪资": 13000,
        "工作城市": "成都",
        "工作区域": "双流",
        "工作街道": "华阳",
        "工作类型": "全职",
        "学历要求": "本科",
        "工作年限要求": "3-5年",
        "岗位要求": "Java基础扎实，能够独立完成模块的设计开发...",
        "岗位职责": "负责模块设计开发，熟练使用mysql或oracle数据库...",
        "岗位发布时间": "2025-07-02 10:56:47",
        "企业规模": "1000-9999人",
        "企业性质": "民营",
        "source": "Boss直聘",
    }
    # 清洗→插入
    cleaned_job = DataProcessor.clean_job_data(test_job)
    if DBOperations.insert_job(cleaned_job):
        print("✅ 单条测试数据入库成功")


def batch_job_import(json_file_path: str):
    """批量导入JSON格式岗位数据"""
    # 读取→清洗→批量插入
    raw_jobs = FileUtils.read_json(json_file_path)
    if not raw_jobs:
        print("⚠ 无有效数据可导入")
        return

    cleaned_jobs = DataProcessor.batch_clean_jobs(raw_jobs)
    success_count = 0
    for job in cleaned_jobs:
        if DBOperations.insert_job(job):
            success_count += 1

    print(
        f"\n📊 批量导入统计：共 {len(cleaned_jobs)} 条，成功 {success_count} 条，失败 {len(cleaned_jobs)-success_count} 条"
    )


def import_company_data(company_list: List[dict]):
    """导入企业数据并关联岗位cid"""
    for company in company_list:
        DBOperations.insert_company(company)
    # 关联更新岗位cid
    DBOperations.update_job_cid()


def convert_txt_to_json():
    """将TXT文件转换为JSON格式"""
    print("\n📁 开始转换TXT文件为JSON格式...")

    # 创建转换后的文件夹
    output_folder = "converted_jobs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 批量转换所有TXT文件
    total_jobs = TxtToJsonConverter.batch_convert_txt_folder(
        "e:\\寒假项目\\jobs", output_folder
    )

    if total_jobs > 0:
        print(f"✅ 数据转换完成! 共转换 {total_jobs} 条岗位数据")
        return True
    else:
        print("❌ 数据转换失败，请检查TXT文件格式")
        return False


def batch_import_all_json():
    """批量导入所有转换后的JSON文件"""
    json_folder = "converted_jobs"
    if not os.path.exists(json_folder):
        print(f"❌ JSON文件夹不存在: {json_folder}")
        return False

    total_imported = 0
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            json_path = os.path.join(json_folder, filename)
            print(f"\n📥 正在导入: {filename}")

            try:
                jobs = FileUtils.read_json(json_path)
                if jobs:
                    cleaned_jobs = DataProcessor.batch_clean_jobs(jobs)
                    count = DBOperations.batch_insert_jobs(cleaned_jobs)
                    total_imported += count
                    print(f"✅ 导入成功: {count} 条数据")
                else:
                    print(f"⚠ 文件为空: {filename}")
            except Exception as e:
                print(f"❌ 导入失败: {filename} - 错误: {e}")

    if total_imported > 0:
        print(f"\n🎉 批量导入完成! 共导入 {total_imported} 条岗位数据")
        return True
    else:
        print("❌ 批量导入失败")
        return False


if __name__ == "__main__":
    # 步骤1：初始化数据库表
    DBOperations.init_tables()

    # 步骤2：单条数据测试
    single_job_test()

    # 步骤3：数据转换（将TXT转换为JSON）
    if convert_txt_to_json():
        # 步骤4：批量导入转换后的数据
        batch_import_all_json()

    # 步骤5：导入企业数据并关联（示例）
    test_companies = [
        {
            "company_name": "北京银丰新融科技开发有限公司",
            "company_scale": "1000-9999人",
            "company_nature": "民营",
            "source": "Boss直聘",
        }
    ]
    import_company_data(test_companies)

    # 步骤6：导出数据验证
    DBOperations.export_jobs("exported_jobs.json")

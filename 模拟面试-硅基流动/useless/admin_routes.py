from flask import (
    Blueprint,
    request,
    jsonify,
    render_template_string,
    session,
    redirect,
    url_for,
    flash,
)
from backend.models.data_source import DataSourceManager
from backend.models.knowledge_base import KnowledgeBaseManager
from backend.models.interview import InterviewManager
import os
import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash

admin_bp = Blueprint("admin", __name__)

# 初始化管理器
data_source_manager = DataSourceManager()
knowledge_base_manager = KnowledgeBaseManager()
interview_manager = InterviewManager()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            # 如果是API请求，返回JSON错误
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "未登录"}), 401
            # 否则重定向到登录页面
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    """管理员登录"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("interview_system.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM admins WHERE username = ?", (username,)
        )
        result = cursor.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            return redirect(url_for("admin.admin_interface"))
        else:
            return render_template_string(
                """
            <!DOCTYPE html>
            <html>
            <head>
                <title>管理员登录</title>
                <style>
                    body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; margin: 0; }
                    .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
                    h2 { text-align: center; color: #333; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                    button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    .error { color: red; text-align: center; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <h2>管理员登录</h2>
                    <div class="error">用户名或密码错误</div>
                    <form method="post">
                        <input type="text" name="username" placeholder="用户名" required>
                        <input type="password" name="password" placeholder="密码" required>
                        <button type="submit">登录</button>
                    </form>
                </div>
            </body>
            </html>
            """
            )

    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>管理员登录</title>
        <style>
            body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; margin: 0; }
            .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
            h2 { text-align: center; color: #333; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>管理员登录</h2>
            <form method="post">
                <input type="text" name="username" placeholder="用户名" required>
                <input type="password" name="password" placeholder="密码" required>
                <button type="submit">登录</button>
            </form>
        </div>
    </body>
    </html>
    """
    )


@admin_bp.route("/admin/logout")
def logout():
    """退出登录"""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/api/data-sources", methods=["GET", "POST"])
@login_required
def handle_data_sources():
    """数据源管理"""
    if request.method == "GET":
        try:
            sources = data_source_manager.get_all_data_sources()
            return jsonify({"success": True, "data_sources": sources})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    elif request.method == "POST":
        try:
            data = request.get_json()
            if (
                not data
                or "name" not in data
                or "type" not in data
                or "config" not in data
            ):
                return jsonify({"success": False, "error": "缺少必要参数"})

            config = data["config"]
            if isinstance(config, str):
                try:
                    import json

                    config = json.loads(config)
                except:
                    return jsonify({"success": False, "error": "配置格式无效"})

            success = data_source_manager.add_data_source(
                data["name"], data["type"], config
            )
            if success:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "数据源名称已存在"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/data-sources/<int:source_id>/status", methods=["PUT"])
@login_required
def update_data_source_status(source_id):
    """更新数据源状态"""
    try:
        data = request.get_json()
        success = data_source_manager.update_data_source_status(
            source_id, data["status"]
        )
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "数据源不存在"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/data-sources/<int:source_id>", methods=["DELETE"])
def delete_data_source(source_id):
    """删除数据源"""
    try:
        success = data_source_manager.delete_data_source(source_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "数据源不存在"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/data-sources/<int:source_id>/test", methods=["POST"])
def test_data_source(source_id):
    """测试数据源"""
    try:
        result = data_source_manager.test_data_source(source_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/data-sources/<int:source_id>/execute", methods=["POST"])
@login_required
def execute_data_source(source_id):
    """执行数据源"""
    try:
        result = data_source_manager.execute_data_source(source_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/knowledge-base", methods=["GET"])
@login_required
def get_knowledge_base():
    """获取知识库文档列表"""
    try:
        documents = knowledge_base_manager.get_all_documents()
        return jsonify({"success": True, "documents": documents})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/knowledge-base/upload", methods=["POST"])
def upload_document():
    """上传文档"""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "没有上传文件"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "没有选择文件"})

        name = request.form.get("name", file.filename)
        category = request.form.get("category", "其他")
        description = request.form.get("description", "")

        result = knowledge_base_manager.upload_document(
            file, name, category, description
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/knowledge-base/<int:doc_id>/download", methods=["GET"])
def download_document(doc_id):
    """下载文档"""
    try:
        doc = knowledge_base_manager.get_document_by_id(doc_id)
        if not doc:
            return jsonify({"success": False, "error": "文档不存在"})

        if not os.path.exists(doc["file_path"]):
            return jsonify({"success": False, "error": "文件不存在"})

        from flask import send_file

        return send_file(
            doc["file_path"], as_attachment=True, download_name=doc["name"]
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/knowledge-base/<int:doc_id>", methods=["DELETE"])
@login_required
def delete_document(doc_id):
    """删除文档"""
    try:
        success = knowledge_base_manager.delete_document(doc_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "文档不存在或删除失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/interview-details/<int:interview_id>", methods=["GET"])
@login_required
def get_interview_details(interview_id):
    """获取面试详情"""
    try:
        interview = interview_manager.get_interview_by_id(interview_id)
        if not interview:
            return jsonify({"success": False, "error": "面试记录不存在"})

        qa_records = interview_manager.get_qa_records_by_interview_id(interview_id)
        return jsonify(
            {"success": True, "interview": interview, "qa_records": qa_records}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/interview-pdf/<int:interview_id>", methods=["GET"])
@login_required
def download_interview_pdf(interview_id):
    """下载面试PDF"""
    try:
        interview = interview_manager.get_interview_by_id(interview_id)
        if not interview:
            return jsonify({"success": False, "error": "面试记录不存在"})

        pdf_path = interview.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify(
                {"success": False, "error": f"[WinError 2] 系统找不到指定的文件。: '{pdf_path}'"}
            )

        from flask import send_file

        return send_file(
            pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path)
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/interview-results", methods=["GET"])
def get_interview_results():
    """获取面试结果"""
    try:
        # 获取查询参数
        job_name = request.args.get("job_name", "")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")

        # 搜索面试记录
        interviews = interview_manager.search_interviews(job_name, start_date, end_date)

        # 获取统计信息
        stats = interview_manager.get_interview_stats()

        return jsonify({"success": True, "interviews": interviews, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@admin_bp.route("/api/interview-results/export", methods=["POST"])
@login_required
def export_interview_results():
    """导出面试结果"""
    try:
        data = request.get_json()
        format_type = data.get("format", "csv")

        # 获取所有面试结果
        interviews = interview_manager.search_interviews()

        if format_type == "csv":
            import csv
            import io
            from flask import send_file

            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(["岗位名称", "面试时间", "题目数量", "通过数量", "通过率", "最终评估"])

            # 写入数据
            for interview in interviews:
                writer.writerow(
                    [
                        interview.get("job_name", ""),
                        interview.get("start_time", ""),
                        interview.get("total_questions", 0),
                        interview.get("passed_questions", 0),
                        f"{interview.get('pass_rate', 0) * 100:.1f}%",
                        interview.get("final_evaluation", ""),
                    ]
                )

            # 创建BytesIO对象
            output.seek(0)
            bytes_output = io.BytesIO()
            bytes_output.write(output.getvalue().encode("utf-8-sig"))
            bytes_output.seek(0)

            return send_file(
                bytes_output,
                as_attachment=True,
                download_name=f'面试结果_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mimetype="text/csv",
            )

        else:
            return jsonify({"success": False, "error": "不支持的导出格式"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 管理端界面
@admin_bp.route("/admin")
@login_required
def admin_interface():
    """管理端界面 - 简化版"""
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>管理端 - 智能面试系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
            .header h1 { margin: 0; font-size: 24px; }
            .logout-btn { color: white; text-decoration: none; border: 1px solid white; padding: 5px 15px; border-radius: 4px; }
            .logout-btn:hover { background: rgba(255,255,255,0.2); }
            .nav-tabs { display: flex; background: #f8f9fa; border-radius: 8px; padding: 10px; margin-bottom: 20px; }
            .nav-tab { padding: 10px 20px; cursor: pointer; border-radius: 5px; margin-right: 10px; background: white; border: 1px solid #ddd; }
            .nav-tab.active { background: #007bff; color: white; border-color: #007bff; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-danger { background: #dc3545; color: white; }
            .form-group { margin: 10px 0; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; font-weight: bold; }
            .status-active { color: #28a745; }
            .status-inactive { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>🎛️ 管理端 - 智能面试系统</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">系统配置与数据管理中心</p>
                </div>
                <a href="/admin/logout" class="logout-btn">退出登录</a>
            </div>
            
            <div class="nav-tabs">
                <div class="nav-tab active" onclick="showTab('data-sources')">数据源配置</div>
                <div class="nav-tab" onclick="showTab('knowledge-base')">知识库管理</div>
                <div class="nav-tab" onclick="showTab('interview-results')">面试结果</div>
            </div>
            
            <!-- 数据源配置 -->
            <div id="data-sources" class="tab-content active">
                <h2>📊 数据源配置</h2>
                <div class="card">
                    <h3>添加新数据源</h3>
                    <div class="form-group">
                        <label>数据源名称:</label>
                        <input type="text" id="source-name" placeholder="例如: 智联招聘爬虫">
                    </div>
                    <div class="form-group">
                        <label>数据源类型:</label>
                        <select id="source-type">
                            <option value="spider">爬虫</option>
                            <option value="file">文件导入</option>
                            <option value="api">API接口</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>配置信息 (JSON格式):</label>
                        <textarea id="source-config" rows="4" placeholder='{"url": "https://example.com", "params": {...}}'></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="addDataSource()">添加数据源</button>
                </div>
                
                <div class="card">
                    <h3>现有数据源</h3>
                    <table id="data-sources-table">
                        <thead>
                            <tr>
                                <th>名称</th>
                                <th>类型</th>
                                <th>状态</th>
                                <th>创建时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody id="data-sources-tbody">
                            <!-- 动态加载 -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 知识库管理 -->
            <div id="knowledge-base" class="tab-content">
                <h2>📚 知识库管理</h2>
                <div class="card">
                    <h3>上传文档</h3>
                    <div class="form-group">
                        <label>文档名称:</label>
                        <input type="text" id="doc-name" placeholder="请输入文档名称">
                    </div>
                    <div class="form-group">
                        <label>文档分类:</label>
                        <select id="doc-category">
                            <option value="面试题库">面试题库</option>
                            <option value="技术文档">技术文档</option>
                            <option value="岗位要求">岗位要求</option>
                            <option value="其他">其他</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>选择文件:</label>
                        <input type="file" id="doc-file" accept=".txt,.pdf,.doc,.docx">
                    </div>
                    <div class="form-group">
                        <label>文档描述:</label>
                        <textarea id="doc-description" rows="3" placeholder="请输入文档描述"></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="uploadDocument()">上传文档</button>
                </div>
                
                <div class="card">
                    <h3>知识库文档列表</h3>
                    <table id="knowledge-base-table">
                        <thead>
                            <tr>
                                <th>文档名称</th>
                                <th>分类</th>
                                <th>上传时间</th>
                                <th>状态</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody id="knowledge-base-tbody">
                            <!-- 动态加载 -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 面试结果 -->
            <div id="interview-results" class="tab-content">
                <h2>📊 面试结果管理</h2>
                <div class="card">
                    <h3>面试记录统计</h3>
                    <div style="display: flex; gap: 20px;">
                        <div style="flex: 1;">
                            <h4>总面试次数</h4>
                            <p id="total-interviews" style="font-size: 24px; color: #007bff;">0</p>
                        </div>
                        <div style="flex: 1;">
                            <h4>平均通过率</h4>
                            <p id="avg-pass-rate" style="font-size: 24px; color: #28a745;">0%</p>
                        </div>
                        <div style="flex: 1;">
                            <h4>热门岗位</h4>
                            <p id="top-job" style="font-size: 18px; color: #ffc107;">暂无数据</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>面试记录列表</h3>
                    <div style="margin-bottom: 15px;">
                        <input type="text" id="search-interview" placeholder="搜索岗位名称..." style="width: 200px; margin-right: 10px;">
                        <input type="date" id="filter-date" style="width: 150px; margin-right: 10px;">
                        <button class="btn btn-primary" onclick="searchInterviews()">搜索</button>
                        <button class="btn btn-success" onclick="exportResults()">导出结果</button>
                    </div>
                    <table id="interview-results-table">
                        <thead>
                            <tr>
                                <th>岗位名称</th>
                                <th>面试时间</th>
                                <th>题目数量</th>
                                <th>通过数量</th>
                                <th>通过率</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody id="interview-results-tbody">
                            <!-- 动态加载 -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
        // 标签页切换
        function showTab(tabName) {
            // 隐藏所有标签页
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 加载对应数据
            loadTabData(tabName);
        }
        
        // 加载标签页数据
        function loadTabData(tabName) {
            switch(tabName) {
                case 'data-sources':
                    loadDataSources();
                    break;
                case 'knowledge-base':
                    loadKnowledgeBase();
                    break;
                case 'interview-results':
                    loadInterviewResults();
                    break;
            }
        }
        
        // 数据源管理函数
        function addDataSource() {
            const name = document.getElementById('source-name').value;
            const type = document.getElementById('source-type').value;
            const config = document.getElementById('source-config').value;
            
            if (!name || !config) {
                alert('请填写完整信息');
                return;
            }
            
            fetch('/api/data-sources', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, type, config: JSON.parse(config)})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('数据源添加成功');
                    loadDataSources();
                    document.getElementById('source-name').value = '';
                    document.getElementById('source-config').value = '';
                } else {
                    alert('添加失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('添加失败');
            });
        }
        
        function loadDataSources() {
            fetch('/api/data-sources')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('data-sources-tbody');
                tbody.innerHTML = '';
                
                data.data_sources.forEach(source => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${source.name}</td>
                        <td>${source.type}</td>
                        <td class="${source.status === 'active' ? 'status-active' : 'status-inactive'}">${source.status}</td>
                        <td>${source.created_at}</td>
                        <td>
                            <button class="btn btn-success" onclick="toggleDataSource(${source.id}, '${source.status}')">${source.status === 'active' ? '禁用' : '启用'}</button>
                            <button class="btn btn-danger" onclick="deleteDataSource(${source.id})">删除</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        // 知识库管理函数
        function uploadDocument() {
            const fileInput = document.getElementById('doc-file');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('请选择文件');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', document.getElementById('doc-name').value);
            formData.append('category', document.getElementById('doc-category').value);
            formData.append('description', document.getElementById('doc-description').value);
            
            fetch('/api/knowledge-base/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('文档上传成功');
                    loadKnowledgeBase();
                    fileInput.value = '';
                    document.getElementById('doc-name').value = '';
                    document.getElementById('doc-description').value = '';
                } else {
                    alert('上传失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('上传失败');
            });
        }
        
        function loadKnowledgeBase() {
            fetch('/api/knowledge-base')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('knowledge-base-tbody');
                tbody.innerHTML = '';
                
                data.documents.forEach(doc => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${doc.name}</td>
                        <td>${doc.category}</td>
                        <td>${doc.upload_time}</td>
                        <td class="${doc.status === 'active' ? 'status-active' : 'status-inactive'}">${doc.status}</td>
                        <td>
                            <button class="btn btn-success" onclick="downloadDocument(${doc.id})">下载</button>
                            <button class="btn btn-danger" onclick="deleteDocument(${doc.id})">删除</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        // 数据源操作函数
        function toggleDataSource(sourceId, currentStatus) {
            const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
            
            fetch(`/api/data-sources/${sourceId}/status`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({status: newStatus})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('状态更新成功');
                    loadDataSources();
                } else {
                    alert('更新失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('更新失败');
            });
        }
        
        function deleteDataSource(sourceId) {
            if (!confirm('确定要删除这个数据源吗？')) return;
            
            fetch(`/api/data-sources/${sourceId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('删除成功');
                    loadDataSources();
                } else {
                    alert('删除失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('删除失败');
            });
        }
        
        // 知识库操作函数
        function downloadDocument(docId) {
            window.open(`/api/knowledge-base/${docId}/download`, '_blank');
        }
        
        function deleteDocument(docId) {
            if (!confirm('确定要删除这个文档吗？')) return;
            
            fetch(`/api/knowledge-base/${docId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('删除成功');
                    loadKnowledgeBase();
                } else {
                    alert('删除失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('删除失败');
            });
        }
        
        // 面试结果管理函数
        function loadInterviewResults() {
            fetch('/api/interview-results')
            .then(response => response.json())
            .then(data => {
                // 更新统计信息
                if (data.stats) {
                    document.getElementById('total-interviews').textContent = data.stats.total_interviews || 0;
                    document.getElementById('avg-pass-rate').textContent = data.stats.avg_pass_rate + '%';
                    document.getElementById('top-job').textContent = data.stats.top_job || '暂无数据';
                }
                
                // 更新表格
                const tbody = document.getElementById('interview-results-tbody');
                tbody.innerHTML = '';
                
                if (data.interviews && data.interviews.length > 0) {
                    data.interviews.forEach(interview => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${interview.job_name}</td>
                            <td>${interview.start_time}</td>
                            <td>${interview.total_questions}</td>
                            <td>${interview.passed_questions}</td>
                            <td>${interview.pass_rate}</td>
                            <td>
                                <button class="btn btn-primary" onclick="viewInterviewDetails(${interview.id})">查看详情</button>
                                <button class="btn btn-success" onclick="downloadPDF(${interview.id})">下载PDF</button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                } else {
                    const row = document.createElement('tr');
                    row.innerHTML = '<td colspan="6" style="text-align: center;">暂无面试记录</td>';
                    tbody.appendChild(row);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        function viewInterviewDetails(interviewId) {
            fetch(`/api/interview-details/${interviewId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 显示面试详情模态框
                    showInterviewDetailsModal(data.interview, data.qa_records);
                } else {
                    alert('获取详情失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('获取详情失败');
            });
        }
        
        function downloadPDF(interviewId) {
            window.open(`/api/interview-pdf/${interviewId}`, '_blank');
        }
        
        function searchInterviews() {
            const jobName = document.getElementById('search-interview').value;
            const filterDate = document.getElementById('filter-date').value;
            
            let url = '/api/interview-results';
            const params = [];
            
            if (jobName) params.push(`job_name=${encodeURIComponent(jobName)}`);
            if (filterDate) params.push(`start_date=${filterDate}`);
            
            if (params.length > 0) {
                url += '?' + params.join('&');
            }
            
            fetch(url)
            .then(response => response.json())
            .then(data => {
                // 更新表格
                const tbody = document.getElementById('interview-results-tbody');
                tbody.innerHTML = '';
                
                if (data.interviews && data.interviews.length > 0) {
                    data.interviews.forEach(interview => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${interview.job_name}</td>
                            <td>${interview.start_time}</td>
                            <td>${interview.total_questions}</td>
                            <td>${interview.passed_questions}</td>
                            <td>${interview.pass_rate}</td>
                            <td>
                                <button class="btn btn-primary" onclick="viewInterviewDetails(${interview.id})">查看详情</button>
                                <button class="btn btn-success" onclick="downloadPDF(${interview.id})">下载PDF</button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                } else {
                    const row = document.createElement('tr');
                    row.innerHTML = '<td colspan="6" style="text-align: center;">没有找到匹配的记录</td>';
                    tbody.appendChild(row);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        function exportResults() {
            alert('导出功能正在开发中...');
        }
        
        // 显示面试详情模态框
        function showInterviewDetailsModal(interview, qaRecords) {
            let modalContent = `
                <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;">
                    <div style="background: white; padding: 20px; border-radius: 8px; max-width: 800px; max-height: 80vh; overflow-y: auto;">
                        <h3>面试详情 - ${interview.job_name}</h3>
                        <p><strong>面试时间:</strong> ${interview.start_time}</p>
                        <p><strong>总题数:</strong> ${interview.total_questions}</p>
                        <p><strong>通过数:</strong> ${interview.passed_questions}</p>
                        <p><strong>通过率:</strong> ${interview.pass_rate}</p>
                        <hr>
                        <h4>问答记录:</h4>
            `;
            
            if (qaRecords && qaRecords.length > 0) {
                qaRecords.forEach((qa, index) => {
                    modalContent += `
                        <div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                            <p><strong>问题 ${index + 1}:</strong> ${qa.question_text}</p>
                            <p><strong>回答:</strong> ${qa.answer_text}</p>
                            <p><strong>评估:</strong> ${qa.evaluation || '无评估'}</p>
                            <p><strong>结果:</strong> ${qa.is_passed ? '✅ 通过' : '❌ 未通过'}</p>
                        </div>
                    `;
                });
            } else {
                modalContent += '<p>暂无问答记录</p>';
            }
            
            modalContent += `
                        <button class="btn btn-primary" onclick="closeModal()" style="margin-top: 20px;">关闭</button>
                    </div>
                </div>
            `;
            
            // 创建模态框
            const modal = document.createElement('div');
            modal.innerHTML = modalContent;
            modal.id = 'interview-details-modal';
            document.body.appendChild(modal);
        }
        
        function closeModal() {
            const modal = document.getElementById('interview-details-modal');
            if (modal) {
                modal.remove();
            }
        }
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadDataSources();
        });
        </script>
    </body>
    </html>
    """
    )

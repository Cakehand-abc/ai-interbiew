from django.db import models
from django.contrib.auth.models import User

class Interview(models.Model):
    """面试记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    job_name = models.CharField(max_length=100)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    final_evaluation = models.TextField(blank=True)
    
    # 新增设置字段
    total_questions = models.IntegerField(default=5)
    passing_threshold = models.IntegerField(default=3)

    def __str__(self):
        return f"{self.job_name} - {self.user.username}"

class QARecord(models.Model):
    """问答记录模型"""
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='qa_records')
    question = models.TextField()
    answer = models.TextField()
    evaluation = models.TextField(blank=True)
    is_passed = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:50]}..."

from django.contrib import admin
from .models import Interview, QARecord

class QARecordInline(admin.TabularInline):
    model = QARecord
    extra = 0  # 不显示额外的空表单

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'session_id', 'start_time', 'end_time')
    inlines = [QARecordInline]

@admin.register(QARecord)
class QARecordAdmin(admin.ModelAdmin):
    list_display = ('interview', 'question', 'is_passed', 'created_at')
    list_filter = ('is_passed',)

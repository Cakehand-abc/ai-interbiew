<template>
  <div class="result-container">
    <div class="report-card">
      <h1>面试评估报告</h1>
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在生成您的专属面试报告，请稍候...</p>
      </div>
      <div v-else-if="finalReport" class="report-content" v-html="renderedReport"></div>
      <div v-else class="report-content">无法加载报告内容</div>
    </div>

    <div class="result-actions">
      <button @click="goHome" class="btn-primary">返回首页</button>
      <button @click="exportPdf" class="btn-secondary" v-if="!isLoading && finalReport && !finalReport.includes('无法加载')">导出为 PDF</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import { getReport } from '../api';

// 配置 marked 和 highlight.js
marked.setOptions({
  breaks: true,
  highlight: function (code: string, lang: string) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
} as any);

const route = useRoute();
const router = useRouter();
const finalReport = ref('');
const isLoading = ref(true);

const renderedReport = computed(() => {
  return finalReport.value ? marked(finalReport.value) : '';
});

onMounted(async () => {
  const sessionId = route.query.session_id as string;
  if (sessionId) {
    try {
      const data = await getReport(sessionId);
      if (data.success) {
        // 构建 Markdown 报告
        let reportMd = `# ${data.job_name} 面试评估报告\n\n`;
        
        // 总体结果
        const passStatus = data.is_passed ? '✅ **通过**' : '❌ **未通过**';
        reportMd += `## 总体评估\n\n`;
        reportMd += `- **面试结果：** ${passStatus}\n`;
        reportMd += `- **总题数：** ${data.total_questions} 题\n`;
        reportMd += `- **合格题数：** ${data.passed_count} 题 (要求 ${data.passing_threshold} 题及格)\n`;
        reportMd += `- **不合格题数：** ${data.failed_count} 题\n\n`;
        
        // 面试总结
        if (data.summary) {
          reportMd += `## 面试总结与建议\n\n${data.summary}\n\n`;
        }
        
        // 问答明细
        if (data.qa_list && data.qa_list.length > 0) {
          reportMd += `## 问答明细\n\n`;
          data.qa_list.forEach((qa: any) => {
            const qaStatus = qa.is_passed ? '✅ 合格' : '❌ 不合格';
            reportMd += `### 第 ${qa.index} 题：${qa.question}\n\n`;
            reportMd += `**你的回答：**\n\n${qa.answer || '*未回答*'}\n\n`;
            reportMd += `**面试官评价 (${qaStatus})：**\n\n> ${qa.evaluation || '*无评价*'}\n\n---\n\n`;
          });
        }
        
        finalReport.value = reportMd;
      } else {
        finalReport.value = '# 无法加载面试报告\n\n获取报告失败，请稍后重试。';
      }
    } catch (error: any) {
      finalReport.value = `# 无法加载面试报告\n\n网络错误：${error.message}`;
    } finally {
      isLoading.value = false;
    }
  } else {
    const report = history.state.finalReport;
    if (report) {
      finalReport.value = report;
    } else {
      finalReport.value = '# 无法加载面试报告\n\n缺少会话信息，请返回首页重试。';
    }
    isLoading.value = false;
  }
});

const goHome = () => {
  router.push({ name: 'Home' });
};

const exportPdf = () => {
  window.print();
};
</script>

<style lang="scss" scoped>
.result-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  background-color: $color-light-gray;
}

.report-card {
  background-color: $color-white;
  padding: 2rem;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  margin-bottom: 2rem;
}

.report-content {
  // 对 v-html 渲染的内容进行样式穿透
  :deep(h1), :deep(h2), :deep(h3) {
    color: $color-text-primary;
    border-bottom: 1px solid $border-color;
    padding-bottom: 0.5rem;
    margin-top: 1.5rem;
  }
  :deep(ul) {
    padding-left: 1.5rem;
  }
  :deep(pre) {
    background-color: #f3f4f6;
    padding: 1rem;
    border-radius: $border-radius-lg;
  }
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: $border-radius-lg;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: $color-primary;
  color: $color-white;
}

.btn-secondary {
  background-color: $color-white;
  color: $color-primary;
  border: 1px solid $color-primary;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: $color-text-secondary;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba($color-primary, 0.2);
  border-top-color: $color-primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media print {
  body {
    background-color: white;
  }
  .result-container {
    padding: 0;
    max-width: 100%;
  }
  .report-card {
    box-shadow: none;
    padding: 0;
    margin: 0;
  }
  .result-actions {
    display: none;
  }
}
</style>

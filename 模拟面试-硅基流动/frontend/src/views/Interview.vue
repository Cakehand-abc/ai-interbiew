<template>
  <div class="interview-container">
    <div class="header-actions">
      <button class="back-btn" @click="goBack">
        <span class="icon">←</span> 返回首页
      </button>
      <div class="progress-container" v-if="totalQuestions > 0">
        <div class="progress-info">
          <span>面试进度</span>
          <span>{{ currentQuestion }} / {{ totalQuestions }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${(currentQuestion / totalQuestions) * 100}%` }"></div>
        </div>
      </div>
    </div>
    <div class="chat-panel">
      <div class="messages-area" ref="messagesArea">
        <div v-for="(msg, index) in messages" :key="index" :class="['message-bubble', msg.sender]">
          <div class="message-content" v-html="formatMessage(msg.text)"></div>
        </div>
        <div v-if="isLoading" class="message-bubble ai">
          <div class="message-content loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      <div class="input-area">
        <textarea 
          v-model="userInput" 
          placeholder="在此输入你的回答... (Enter发送，Shift+Enter换行)" 
          @keydown.enter="handleEnter" 
          :disabled="isLoading"
        ></textarea>
        <button @click="sendMessage" :disabled="isLoading">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import { postChatMessage } from '../api';

marked.setOptions({
  breaks: true, // 保留换行符
  highlight: function (code: string, lang: string) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
} as any);

interface Message {
  sender: 'user' | 'ai' | 'system';
  text: string;
}

const route = useRoute();
const router = useRouter();
const messages = ref<Message[]>([]);
const userInput = ref('');
const sessionId = ref<string | null>(null);
const isLoading = ref(false);
const isFinished = ref(false);
const messagesArea = ref<HTMLElement | null>(null);

const totalQuestions = ref(route.query.total_questions ? parseInt(route.query.total_questions as string) : 5);
const currentQuestion = ref(0); // 初始为0，自我介绍不计入问题数

watch(messages, async () => {
  await nextTick();
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight;
  }
}, { deep: true });

const formatMessage = (text: string) => {
  return marked(text);
};

const goBack = () => {
  if (!isFinished.value && messages.value.length > 2) {
    if (!confirm('正在面试中，若退出面试结果不会保存！确认要返回首页吗？')) {
      return;
    }
  }
  router.push({ name: 'Home' });
};

onMounted(() => {
  const jobName = route.query.job as string;
  const existingSessionId = route.query.session_id as string;
  
  if (jobName) {
    if (existingSessionId) {
      sessionId.value = existingSessionId;
      messages.value.push({ sender: 'system', text: `正在为您恢复 **${jobName}** 面试...` });
      // 如果需要加载历史对话可以在这里发起请求获取
      // 目前后端 chat 接口可能直接返回下一个问题或评估，这里简单处理
      messages.value.push({ sender: 'ai', text: '我们继续吧，请直接回答上一个问题或说“你好”继续。' });
      isLoading.value = false;
    } else {
      startInterview(jobName);
    }
  } else {
    router.push({ name: 'Home' });
  }
});

const startInterview = async (jobName: string) => {
  isLoading.value = true;
  messages.value.push({ sender: 'system', text: `正在为您准备 **${jobName}** 面试...` });

  const totalQuestions = route.query.total_questions ? parseInt(route.query.total_questions as string) : 5;
  const passingThreshold = route.query.passing_threshold ? parseInt(route.query.passing_threshold as string) : 3;

  try {
    const data = await postChatMessage({ 
      message: jobName,
      total_questions: totalQuestions,
      passing_threshold: passingThreshold
    });
    if (data.success) {
      sessionId.value = data.session_id;
      messages.value.push({ sender: 'ai', text: data.message });
    } else {
      messages.value.push({ sender: 'system', text: `面试初始化失败: ${data.error}` });
    }
  } catch (error: any) {
    messages.value.push({ sender: 'system', text: `服务连接失败: ${error.message}` });
  } finally {
    isLoading.value = false;
  }
};

const handleEnter = (e: KeyboardEvent) => {
  if (e.shiftKey) {
    // 按下 Shift+Enter 时，允许默认换行行为
    return;
  }
  // 未按下 Shift 时，阻止默认换行并发送消息
  e.preventDefault();
  sendMessage();
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const userMessage = userInput.value;
  messages.value.push({ sender: 'user', text: userMessage });
  userInput.value = '';
  isLoading.value = true;

  try {
    const data = await postChatMessage({ message: userMessage, session_id: sessionId.value });
    if (data.success) {
      messages.value.push({ sender: 'ai', text: data.message });
      // 更新进度条：使用后端返回的当前问题数
      if (data.current_question_count !== undefined) {
        currentQuestion.value = Math.min(data.current_question_count, totalQuestions.value);
      }
      if (data.interview_ended) {
        isFinished.value = true;
        router.push({ name: 'Result', query: { session_id: sessionId.value } });
      }
    } else {
      messages.value.push({ sender: 'system', text: `处理失败: ${data.error}` });
    }
  } catch (error: any) {
    messages.value.push({ sender: 'system', text: `通信失败: ${error.message}` });
  } finally {
    isLoading.value = false;
  }
};
</script>

<style lang="scss" scoped>
.interview-container {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  overflow: hidden;
  background-color: $color-light-gray;
}

.header-actions {
  padding: 1rem 2rem;
  background-color: $color-white;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  
  .back-btn {
    background: none;
    border: none;
    color: $color-text-secondary;
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: $border-radius-sm;
    transition: all 0.2s;
    flex-shrink: 0;
    
    &:hover {
      background-color: $color-light-gray;
      color: $color-primary;
    }
  }

  .progress-container {
    flex: 1;
    max-width: 300px;
    margin-left: 2rem;
    
    .progress-info {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      color: $color-text-secondary;
      margin-bottom: 0.25rem;
    }

    .progress-bar {
      height: 8px;
      background-color: $color-light-gray;
      border-radius: 4px;
      overflow: hidden;

      .progress-fill {
        height: 100%;
        background-color: $color-primary;
        transition: width 0.3s ease;
      }
    }
  }
}

.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: 1rem;
  background-color: $color-light-gray; // Ensure consistent background
  min-height: 0; /* 关键：允许 flex 子项缩小，避免内容撑破容器 */
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  scroll-behavior: smooth; /* 增加平滑滚动效果 */
  padding-right: 0.5rem; /* 预留滚动条空间 */
  
  /* 隐藏滚动条但保留滚动功能 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  &::-webkit-scrollbar {
    display: none; /* Chrome, Safari and Opera */
  }
}

.message-bubble {
  display: flex;
  margin-bottom: 1rem;

  .message-content {
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    max-width: 80%;
    line-height: 1.5;

    :deep(p) { margin: 0; }
    :deep(pre) { margin: 0.5rem 0; white-space: pre-wrap; }
  }

  &.user {
    justify-content: flex-end;
    .message-content {
      background-color: $color-primary;
      color: $color-white;
      border-bottom-right-radius: 0.25rem;
    }
  }

  &.ai {
    justify-content: flex-start;
    .message-content {
      background-color: #f3f4f6; // 使用更中性的灰色
      color: $color-text-primary;
      border: 1px solid $border-color;
      border-bottom-left-radius: 0.25rem;
    }
  }

  &.system {
    justify-content: center;
    .message-content {
      background-color: #fefce8;
      color: #a16207;
      font-size: 0.9rem;
      text-align: center;
    }
  }
}

.input-area {
  display: flex;
  padding-top: 1rem;
  border-top: 1px solid $border-color;

  textarea {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid $border-color;
    border-radius: 0.5rem;
    resize: none;
    height: 60px;
    transition: height 0.2s;

    &:focus {
      outline: none;
      border-color: $color-primary;
      box-shadow: 0 0 0 2px rgba($color-primary, 0.2);
    }
  }

  button {
    margin-left: 1rem;
    padding: 0 1.5rem;
    border: none;
    border-radius: 0.5rem;
    background-color: $color-primary;
    color: $color-white;
    cursor: pointer;
    transition: background-color 0.2s;

    &:disabled {
      background-color: $color-text-placeholder;
      cursor: not-allowed;
    }
  }
}

.loading-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: $color-text-placeholder;
  margin: 0 2px;
  animation: loading 1.4s infinite ease-in-out both;

  &:nth-child(1) { animation-delay: -0.32s; }
  &:nth-child(2) { animation-delay: -0.16s; }
}

@keyframes loading {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>

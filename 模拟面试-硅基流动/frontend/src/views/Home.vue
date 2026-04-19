<template>
  <div class="home-container">
    <header class="main-header">
      <div class="logo">AI 面试官</div>
      <nav class="main-nav">
        <template v-if="userStore.isLoggedIn">
          <span class="welcome-text">你好，{{ userStore.username }}</span>
          <a href="#" @click.prevent="goToHistory">面试记录</a>
          <a href="#" @click.prevent="handleLogout" class="register-btn">退出登录</a>
        </template>
        <template v-else>
          <a href="#" @click.prevent="showLogin = true">登录</a>
          <a href="#" @click.prevent="showRegister = true" class="register-btn">注册</a>
        </template>
      </nav>
    </header>

    <main class="main-content">
      <h1>选择你的面试方向</h1>
      <p>基于真实岗位要求，模拟不同方向的专业面试</p>
      
      <!-- 面试设置区域 -->
      <div class="settings-section">
        <div class="setting-item">
          <label>面试题目数：</label>
          <input type="number" v-model.number="totalQuestions" min="1" max="20" />
        </div>
        <div class="setting-item">
          <label>合格阈值（答对题数）：</label>
          <input type="number" v-model.number="passingThreshold" min="1" :max="totalQuestions" />
        </div>
      </div>

      <div class="job-categories">
        <div 
          v-for="job in jobSuggestions" 
          :key="job"
          class="category-card"
          @click="startInterview(job)"
        >
          <h3>{{ job }}</h3>
          <p>点击开始面试</p>
        </div>
      </div>
      
      <!-- 自定义岗位输入框 (突出显示) -->
      <div class="custom-hero-card">
        <div class="custom-card-content">
          <h2>自定义岗位</h2>
          <p>找不到想要的岗位？请输入你想面试的具体岗位名称，AI 面试官将为你量身定制面试题。</p>
          <div class="custom-input-wrapper">
            <input 
              type="text" 
              v-model="customJob" 
              placeholder="例如：高级Java工程师、产品经理、UI设计师..." 
              @keyup.enter="startCustomInterview"
            />
            <button class="start-btn" @click="startCustomInterview" :disabled="!customJob.trim()">
              <span class="btn-text">开始面试</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
    </main>

    <footer class="main-footer">
    </footer>

    <!-- 登录弹窗 -->
    <el-dialog v-model="showLogin" title="登录" width="400px">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showLogin = false">取消</el-button>
          <el-button type="primary" @click="handleLogin" :loading="authLoading">登录</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 注册弹窗 -->
    <el-dialog v-model="showRegister" title="注册" width="400px">
      <el-form :model="registerForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRegister = false">取消</el-button>
          <el-button type="primary" @click="handleRegister" :loading="authLoading">注册</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getJobSuggestions, loginUser, registerUser } from '../api';
import { useUserStore } from '../store/user';

const userStore = useUserStore();
const jobSuggestions = ref<string[]>(['前端开发工程师', 'Python后端开发']);
const customJob = ref('');
const totalQuestions = ref(5);
const passingThreshold = ref(3);
const router = useRouter();

// Auth state
const showLogin = ref(false);
const showRegister = ref(false);
const authLoading = ref(false);
const loginForm = ref({ username: '', password: '' });
const registerForm = ref({ username: '', password: '' });

// 确保合格阈值不超过总题数
watch(totalQuestions, (newVal) => {
  if (passingThreshold.value > newVal) {
    passingThreshold.value = newVal;
  }
});

onMounted(async () => {
  await userStore.checkLoginStatus();
  try {
    const data = await getJobSuggestions();
    if (data.success) {
      jobSuggestions.value = data.suggestions.filter((s: string) => s !== '产品经理');
    } else {
      jobSuggestions.value = ['前端开发工程师', 'Python后端开发'];
    }
  } catch (error) {
    console.error('获取岗位建议失败:', error);
  }
});

const startCustomInterview = () => {
  if (customJob.value.trim()) {
    startInterview(customJob.value.trim());
  }
};

const startInterview = (jobName: string) => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再开始面试');
    showLogin.value = true;
    return;
  }
  router.push({ 
    name: 'Interview', 
    query: { 
      job: jobName,
      total_questions: totalQuestions.value,
      passing_threshold: passingThreshold.value
    } 
  });
};

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }
  authLoading.value = true;
  try {
    const res = await loginUser(loginForm.value);
    if (res.success) {
      ElMessage.success('登录成功');
      showLogin.value = false;
      // 直接设置登录状态，而不是重新检查
      userStore.setLoginState(res.username);
      // 清空表单
      loginForm.value = { username: '', password: '' };
    } else {
      ElMessage.error(res.error || '登录失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '登录异常');
  } finally {
    authLoading.value = false;
  }
};

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }
  authLoading.value = true;
  try {
    const res = await registerUser(registerForm.value);
    if (res.success) {
      ElMessage.success('注册成功，已自动登录');
      showRegister.value = false;
      // 直接设置登录状态
      userStore.setLoginState(res.username);
      // 清空表单
      registerForm.value = { username: '', password: '' };
    } else {
      ElMessage.error(res.error || '注册失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '注册异常');
  } finally {
    authLoading.value = false;
  }
};

const handleLogout = async () => {
  await userStore.logout();
  ElMessage.success('已退出登录');
};

const goToHistory = () => {
  router.push({ name: 'History' });
};
</script>

<style lang="scss" scoped>
.home-container {
  background-color: $color-light-gray;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: $color-white;
  box-shadow: $shadow-sm;
  flex-shrink: 0;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: $color-primary;
}

.main-nav a {
  margin-left: 1.5rem;
  text-decoration: none;
  color: $color-text-secondary;
  transition: color 0.2s;

  &.register-btn {
    background-color: $color-primary;
    color: $color-white;
    padding: 0.5rem 1rem;
    border-radius: $border-radius-lg;
  }

  &:hover {
    color: $color-primary;
  }
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.settings-section {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: $color-white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  
  .setting-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    label {
      font-size: 0.95rem;
      color: $color-text-secondary;
    }
    
    input {
      width: 60px;
      padding: 0.25rem 0.5rem;
      border: 1px solid $border-color;
      border-radius: $border-radius-sm;
      text-align: center;
      
      &:focus {
        outline: none;
        border-color: $color-primary;
      }
    }
  }
}

.job-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.category-card {
  background-color: $color-white;
  padding: 2rem;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color;
  box-shadow: $shadow-sm;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: $shadow-hover;
    border-color: $color-primary;
  }

  h3 {
    color: $color-text-primary;
    margin-bottom: 0.5rem;
  }

  p {
    color: $color-text-secondary;
    font-size: 0.9rem;
  }
}

.custom-hero-card {
  margin-top: 2rem;
  background: linear-gradient(135deg, $color-primary, lighten($color-primary, 20%));
  border-radius: $border-radius-lg;
  padding: 3rem 2rem;
  color: $color-white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }

  .custom-card-content {
    position: relative;
    z-index: 1;
    max-width: 600px;
    margin: 0 auto;
    text-align: center;

    h2 {
      font-size: 2rem;
      margin-bottom: 1rem;
    }

    p {
      font-size: 1.1rem;
      opacity: 0.9;
      margin-bottom: 2rem;
    }
  }

  .custom-input-wrapper {
    display: flex;
    gap: 1rem;
    background: $color-white;
    padding: 0.5rem;
    border-radius: 50px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);

    input {
      flex: 1;
      border: none;
      background: transparent;
      padding: 0.8rem 1.5rem;
      font-size: 1.1rem;
      color: $color-text-primary;
      outline: none;

      &::placeholder {
        color: $color-text-placeholder;
      }
    }

    .start-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.8rem 2rem;
      background: $color-primary;
      color: $color-white;
      border: none;
      border-radius: 40px;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        background: darken($color-primary, 5%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
      }

      &:disabled {
        background: $color-text-placeholder;
        cursor: not-allowed;
        opacity: 0.7;
      }

      svg {
        transition: transform 0.3s ease;
      }

      &:hover:not(:disabled) svg {
        transform: translateX(5px);
      }
    }
  }
}

.main-footer {
  flex-shrink: 0;
  text-align: center;
  padding: 2rem;
  color: $color-text-placeholder;
}
</style>

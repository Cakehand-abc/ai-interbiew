<template>
  <div class="history-container">
    <header class="main-header">
      <div class="logo">面试记录</div>
      <nav class="main-nav">
        <a href="#" @click.prevent="goHome">返回首页</a>
        <a href="#" @click.prevent="showPasswordDialog = true" v-if="userStore.isLoggedIn">修改密码</a>
      </nav>
    </header>

    <main class="main-content">
      <!-- 筛选栏 -->
      <div class="filter-bar" v-if="historyList.length > 0">
        <button 
          :class="['filter-btn', { active: filterStatus === 'all' }]"
          @click="filterStatus = 'all'"
        >全部 ({{ historyList.length }})</button>
        <button 
          :class="['filter-btn passed-btn', { active: filterStatus === 'passed' }]"
          @click="filterStatus = 'passed'"
        >通过 ({{ passedCount }})</button>
        <button 
          :class="['filter-btn failed-btn', { active: filterStatus === 'failed' }]"
          @click="filterStatus = 'failed'"
        >未通过 ({{ failedCount }})</button>
        <button 
          :class="['filter-btn ongoing-btn', { active: filterStatus === 'ongoing' }]"
          @click="filterStatus = 'ongoing'"
        >未完成 ({{ ongoingCount }})</button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载面试记录...</p>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="filteredHistory.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>{{ filterStatus === 'all' ? '暂无面试记录' : '没有符合条件的记录' }}</h3>
        <p v-if="filterStatus === 'all'">开始您的第一次模拟面试吧！</p>
        <button @click="goHome" class="btn-primary mt-4">去开始面试</button>
      </div>
      
      <!-- 记录列表 -->
      <div v-else class="history-list">
        <TransitionGroup name="list">
          <div 
            v-for="item in filteredHistory" 
            :key="item.session_id" 
            class="history-card"
          >
            <div class="card-header">
              <div class="header-left">
                <span class="job-icon">{{ getJobIcon(item.job_name) }}</span>
                <div class="job-info">
                  <h3>{{ item.job_name }}</h3>
                  <span class="time">{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
              <span :class="['status-badge', getStatusClass(item)]">
                {{ getStatusText(item) }}
              </span>
            </div>
            
            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">题目设置</span>
                  <span class="stat-value">{{ item.total_questions || '?' }} 题</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">合格标准</span>
                  <span class="stat-value">{{ item.passing_threshold || '?' }} 题</span>
                </div>
                <div class="stat-item" v-if="item.is_finished">
                  <span class="stat-label">答题情况</span>
                  <span class="stat-value" :class="{ 'text-success': item.is_passed, 'text-danger': !item.is_passed }">
                    {{ item.passed_count || 0 }} / {{ item.total_questions || '?' }}
                  </span>
                </div>
              </div>
              
              <!-- 进度条（仅已完成） -->
              <div class="progress-wrapper" v-if="item.is_finished && item.total_questions">
                <div class="progress-bar-small">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${((item.passed_count || 0) / item.total_questions) * 100}%` }"
                    :class="{ 'fill-passed': item.is_passed, 'fill-failed': !item.is_passed }"
                  ></div>
                </div>
                <span class="progress-text">通过率 {{ Math.round(((item.passed_count || 0) / item.total_questions) * 100) }}%</span>
              </div>
            </div>
            
            <div class="card-footer">
              <button 
                v-if="item.is_finished" 
                @click="viewReport(item.session_id)" 
                class="btn-secondary"
              >
                📄 查看报告
              </button>
              <button 
                v-else 
                @click="continueInterview(item)" 
                class="btn-primary"
              >
                ▶️ 继续面试
              </button>
              <button 
                @click="confirmDelete(item)" 
                class="btn-danger"
                title="删除此记录"
              >
                🗑️
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </main>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入原密码" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码(至少6位)" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getHistory, deleteInterview, changePassword } from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '../store/user';

const router = useRouter();
const userStore = useUserStore();

// 数据状态
const historyList = ref<any[]>([]);
const loading = ref(true);
const filterStatus = ref<'all' | 'passed' | 'failed' | 'ongoing'>('all');

// 密码修改相关
const showPasswordDialog = ref(false);
const passwordLoading = ref(false);
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

// 计算属性 - 过滤后的列表
const filteredHistory = computed(() => {
  if (filterStatus.value === 'all') return historyList.value;
  
  return historyList.value.filter((item: any) => {
    if (!item.is_finished) return filterStatus.value === 'ongoing';
    if (item.is_passed) return filterStatus.value === 'passed';
    return filterStatus.value === 'failed';
  });
});

// 统计数据
const passedCount = computed(() => 
  historyList.value.filter((item: any) => item.is_finished && item.is_passed).length
);

const failedCount = computed(() => 
  historyList.value.filter((item: any) => item.is_finished && !item.is_passed).length
);

const ongoingCount = computed(() => 
  historyList.value.filter((item: any) => !item.is_finished).length
);

onMounted(async () => {
  // 如果已经处于登录状态，直接加载数据，不重新检查
  if (!userStore.isLoggedIn) {
    await userStore.checkLoginStatus();
  }
  
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录');
    router.push({ name: 'Home' });
    return;
  }
  await fetchHistory();
});

const fetchHistory = async () => {
  loading.value = true;
  try {
    const data = await getHistory();
    if (data.success) {
      historyList.value = data.history;
    } else {
      ElMessage.error(data.error || '获取历史记录失败');
    }
  } catch (error: any) {
    ElMessage.error('网络错误');
  } finally {
    loading.value = false;
  }
};

const goHome = () => {
  router.push({ name: 'Home' });
};

const viewReport = (sessionId: string) => {
  router.push({ name: 'Result', query: { session_id: sessionId } });
};

const continueInterview = (item: any) => {
  router.push({ 
    name: 'Interview', 
    query: { 
      job: item.job_name,
      total_questions: item.total_questions,
      passing_threshold: item.passing_threshold,
      session_id: item.session_id
    } 
  });
};

const confirmDelete = async (item: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${item.job_name}」的面试记录吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    const res = await deleteInterview(item.session_id);
    if (res.success) {
      ElMessage.success('删除成功');
      // 从列表中移除
      historyList.value = historyList.value.filter(h => h.session_id !== item.session_id);
    } else {
      ElMessage.error(res.error || '删除失败');
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
    }
  }
};

const handleChangePassword = async () => {
  const { old_password, new_password, confirm_password } = passwordForm.value;
  
  if (!old_password || !new_password || !confirm_password) {
    ElMessage.warning('请填写完整信息');
    return;
  }
  
  if (new_password !== confirm_password) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  
  if (new_password.length < 6) {
    ElMessage.warning('新密码长度不能少于6位');
    return;
  }
  
  passwordLoading.value = true;
  try {
    const res = await changePassword({ old_password, new_password });
    if (res.success) {
      ElMessage.success('密码修改成功');
      showPasswordDialog.value = false;
      passwordForm.value = { old_password: '', new_password: '', confirm_password: '' };
    } else {
      ElMessage.error(res.error || '修改失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '修改异常');
  } finally {
    passwordLoading.value = false;
  }
};

// 辅助函数
const formatTime = (timeStr: string) => {
  if (!timeStr) return '';
  const date = new Date(timeStr.replace(/-/g, '/'));
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
};

const getJobIcon = (jobName: string) => {
  const icons: Record<string, string> = {
    'Java': '☕',
    'Python': '🐍',
    '前端': '🎨',
    '后端': '⚙️',
    '产品': '📊',
    '数据': '📈'
  };
  
  for (const [key, icon] of Object.entries(icons)) {
    if (jobName.includes(key)) return icon;
  }
  return '💼';
};

const getStatusClass = (item: any) => {
  if (!item.is_finished) return 'ongoing';
  return item.is_passed ? 'passed' : 'failed';
};

const getStatusText = (item: any) => {
  if (!item.is_finished) return '未完成';
  return item.is_passed ? '✓ 通过' : '✗ 未通过';
};
</script>

<style lang="scss" scoped>
.history-container {
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
  text-decoration: none;
  color: $color-primary;
  transition: color 0.2s;
  margin-left: 1rem;
  &:hover {
    color: darken($color-primary, 10%);
  }
}

.main-content {
  flex: 1;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

// 筛选栏
.filter-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background-color: $color-white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background-color: transparent;
  border: 1px solid $border-color;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9rem;
  color: $color-text-secondary;
  transition: all 0.2s;

  &.active {
    color: white;
    border-color: transparent;
  }

  &.passed-btn.active { background-color: #22c55e; }
  &.failed-btn.active { background-color: #ef4444; }
  &.ongoing-btn.active { background-color: #6366f1; }

  &:hover:not(.active) {
    background-color: rgba($color-primary, 0.05);
    border-color: $color-primary;
  }
}

// 加载和空状态
.loading-state, .empty-state {
  text-align: center;
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
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.mt-4 { margin-top: 1rem; }

.btn-primary {
  padding: 0.6rem 1.25rem;
  background-color: $color-primary;
  color: white;
  border: none;
  border-radius: $border-radius-lg;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  &:hover { 
    background-color: darken($color-primary, 10%);
    transform: translateY(-1px);
  }
}

.btn-secondary {
  padding: 0.6rem 1.25rem;
  background-color: white;
  color: $color-primary;
  border: 1px solid $color-primary;
  border-radius: $border-radius-lg;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  &:hover { 
    background-color: rgba($color-primary, 0.05);
    transform: translateY(-1px);
  }
}

.btn-danger {
  padding: 0.6rem 0.8rem;
  background-color: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: $border-radius-lg;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { 
    background-color: #fef2f2;
  }
}

// 列表动画
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-card {
  background: white;
  border-radius: $border-radius-lg;
  padding: 1.5rem;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-hover;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid $border-color;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .job-icon {
    font-size: 2rem;
    line-height: 1;
  }
  
  .job-info {
    h3 { 
      margin: 0; 
      color: $color-text-primary;
      font-size: 1.1rem;
    }
    .time {
      font-size: 0.85rem;
      color: $color-text-placeholder;
    }
  }
}

.status-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  
  &.passed { background: #dcfce7; color: #166534; }
  &.failed { background: #fee2e2; color: #991b1b; }
  &.ongoing { background: #ede9fe; color: #5b21b6; }
}

.card-body {
  p { margin: 0.5rem 0; color: $color-text-secondary; font-size: 0.95rem; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  .stat-label {
    font-size: 0.8rem;
    color: $color-text-placeholder;
  }
  
  .stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: $color-text-primary;
    
    &.text-success { color: #22c55e; }
    &.text-danger { color: #ef4444; }
  }
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px dashed $border-color;
}

.progress-bar-small {
  flex: 1;
  height: 8px;
  background-color: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  
  .progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
    
    &.fill-passed { background: linear-gradient(90deg, #22c55e, #16a34a); }
    &.fill-failed { background: linear-gradient(90deg, #ef4444, #dc2626); }
  }
}

.progress-text {
  font-size: 0.85rem;
  color: $color-text-secondary;
  font-weight: 500;
  min-width: 70px;
  text-align: right;
}

.card-footer {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid $border-color;
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-bar {
    flex-wrap: wrap;
  }
  
  .history-card {
    padding: 1rem;
  }
}
</style>

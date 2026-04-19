import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getUserInfo as fetchUserInfo, logoutUser } from '../api';

export const useUserStore = defineStore('user', () => {
  const username = ref<string>('');
  const isLoggedIn = ref<boolean>(false);

  // 使用 computed 确保响应式
  const getIsLoggedIn = computed(() => isLoggedIn.value);
  const getUsername = computed(() => username.value);

  const checkLoginStatus = async () => {
    try {
      const data = await fetchUserInfo();
      if (data.success) {
        username.value = data.username;
        isLoggedIn.value = true;
        console.log('[UserStore] Login status: logged in as', data.username);
      } else {
        // 只有明确返回未登录才清除状态
        username.value = '';
        isLoggedIn.value = false;
        console.log('[UserStore] Login status: not logged in');
      }
    } catch (e) {
      // 网络错误时不清除已有的登录状态，保持当前状态
      console.log('[UserStore] Check login status failed (keeping current state):', e);
    }
  };

  const setLoginState = (name: string) => {
    username.value = name;
    isLoggedIn.value = true;
  };

  const clearLoginState = () => {
    username.value = '';
    isLoggedIn.value = false;
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch (e) {
      console.error('Logout API call failed', e);
    }
    // 无论API是否成功，都清除本地状态
    clearLoginState();
  };

  return { 
    username: getUsername, 
    isLoggedIn: getIsLoggedIn, 
    checkLoginStatus, 
    logout,
    setLoginState,
    clearLoginState
  };
});
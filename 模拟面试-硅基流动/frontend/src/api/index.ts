const API_BASE_URL = '/api';

// 封装的 fetch 函数，处理通用逻辑
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`,
     {
      credentials: 'include', // 关键修复：确保每次请求都携带 cookie
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      // 如果 http 状态码不是 2xx，则尝试解析错误信息
      const errorData = await response.json().catch(() => ({ error: '服务器响应异常' }));
      throw new Error(errorData.error || '请求失败');
    }

    return await response.json();
  } catch (error) {
    console.error(`API请求失败: ${endpoint}`, error);
    // 向上抛出错误，让调用方可以捕获
    throw error;
  }
}

// 获取岗位建议
export const getJobSuggestions = () => apiFetch('/job-suggestions');

// 获取面试报告
export const getReport = (sessionId: string) => apiFetch(`/report?session_id=${sessionId}`);

// 发送聊天消息（包括开始面试和后续对话）
export const postChatMessage = (payload: { 
  message: string; 
  session_id?: string | null;
  total_questions?: number;
  passing_threshold?: number;
}) => {
  return apiFetch('/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

// 用户注册
export const registerUser = (credentials: any) => apiFetch('/register', {
  method: 'POST',
  body: JSON.stringify(credentials),
});

// 用户登录
export const loginUser = (credentials: any) => apiFetch('/login', {
  method: 'POST',
  body: JSON.stringify(credentials),
});

// 用户退出
export const logoutUser = () => apiFetch('/logout', { method: 'POST' });

// 获取当前用户信息
export const getUserInfo = () => apiFetch('/user');

// 获取历史记录
export const getHistory = () => apiFetch('/history');

// 删除面试记录
export const deleteInterview = (sessionId: string) => apiFetch('/delete-interview', {
  method: 'POST',
  body: JSON.stringify({ session_id: sessionId }),
});

// 修改密码
export const changePassword = (payload: { old_password: string; new_password: string }) => 
  apiFetch('/change-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

// 新增：专门用于流式读取对话的请求方法 (适配打字机效果)
export const postChatMessageStream = async (
  payload: any,
  onChunk: (text: string) => void,
  onMeta: (meta: any) => void
) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include', // 携带 Cookie 保持会话
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: '请求失败' }));
    throw new Error(errorData.error);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder('utf-8');

  if (!reader) throw new Error("无法读取数据流");

  let done = false;
  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
      const chunkStr = decoder.decode(value, { stream: true });
      const lines = chunkStr.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.replace('data: ', '').trim();
          if (dataStr === '[DONE]') continue;
          try {
            const data = JSON.parse(dataStr);
            if (data.is_meta) {
              onMeta(data);   // 收到后端传来的结束标识、sessionId等
            } else if (data.content) {
              onChunk(data.content); // 收到源源不断的文字流，传给前端渲染
            }
          } catch (e) {
            // 忽略偶尔被截断的JSON错误
          }
        }
      }
    }
  }
};

  
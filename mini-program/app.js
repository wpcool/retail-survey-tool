App({
  globalData: {
    userInfo: null,
    baseUrl: 'http://39.97.236.234',  // 默认使用云端地址
    token: null
  },

  onLaunch() {
    // 检查运行环境
    const systemInfo = wx.getSystemInfoSync();
    console.log('运行平台:', systemInfo.platform);
    
    // 本地开发环境使用 localhost
    if (systemInfo.platform === 'devtools') {
      this.globalData.baseUrl = 'http://127.0.0.1:8000';
    }
    console.log('API 基础地址:', this.globalData.baseUrl);
    
    // 检查登录状态
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      console.log('已登录用户:', userInfo.name, 'ID:', userInfo.id);
    }
  },

  // 全局请求方法
  request(options) {
    const { url, method = 'GET', data, header = {} } = options;
    const token = this.globalData.token;
    const fullUrl = `${this.globalData.baseUrl}${url}`;
    
    console.log(`[API请求] ${method} ${fullUrl}`);
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header,
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        success: (res) => {
          console.log(`[API响应] ${method} ${url} 状态码:`, res.statusCode);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else if (res.statusCode === 401) {
            // Token过期，清除登录状态
            this.clearLoginData();
            wx.reLaunch({ url: '/pages/login/login' });
            reject(new Error('登录已过期'));
          } else {
            console.error('[API错误]', res.data);
            reject(new Error(res.data?.message || `请求失败 (${res.statusCode})`));
          }
        },
        fail: (err) => {
          console.error('[API请求失败]', err);
          reject(new Error('网络请求失败，请检查网络连接'));
        }
      });
    });
  },

  // 清除登录数据
  clearLoginData() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
  },

  // 显示提示
  toast(title, icon = 'none') {
    wx.showToast({ title, icon });
  },

  // 显示加载
  showLoading(title = '加载中...') {
    wx.showLoading({ title, mask: true });
  },

  // 隐藏加载
  hideLoading() {
    wx.hideLoading();
  }
});
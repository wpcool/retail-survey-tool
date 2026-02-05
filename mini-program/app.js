App({
  globalData: {
    userInfo: null,
    baseUrl: 'http://localhost:8000', // 后端API地址
    token: null
  },

  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
    }
  },

  // 全局请求方法
  request(options) {
    const { url, method = 'GET', data, header = {} } = options;
    const token = this.globalData.token;
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.baseUrl}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header,
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else if (res.statusCode === 401) {
            // Token过期，清除登录状态
            this.clearLoginData();
            wx.reLaunch({ url: '/pages/login/login' });
            reject(new Error('登录已过期'));
          } else {
            reject(new Error(res.data?.message || '请求失败'));
          }
        },
        fail: reject
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
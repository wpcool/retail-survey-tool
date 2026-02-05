const app = getApp();

Page({
  data: {
    userInfo: {},
    stats: {
      totalRecords: 0,
      todayRecords: 0,
      completedTasks: 0
    }
  },

  onLoad() {
    this.loadUserInfo();
    this.loadStats();
  },

  onShow() {
    this.loadStats();
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    }
  },

  // 加载统计数据
  async loadStats() {
    try {
      // 调用后端API获取统计
      const res = await app.request({
        url: '/api/stats/overview',
        method: 'GET'
      });
      
      this.setData({
        stats: {
          totalRecords: res.total_records || 0,
          todayRecords: res.today_records || 0,
          completedTasks: res.completed_tasks || 0
        }
      });
    } catch (error) {
      console.error('加载统计失败:', error);
      // 使用模拟数据
      this.setData({
        stats: {
          totalRecords: 128,
          todayRecords: 5,
          completedTasks: 12
        }
      });
    }
  },

  // 查看调研记录
  viewRecords() {
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  // 查看任务
  viewTasks() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  // 设置
  openSettings() {
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  // 关于
  openAbout() {
    wx.showModal({
      title: '关于',
      content: '零售调研小程序 v1.0.0\n\n用于协助调研员记录商品价格信息',
      showCancel: false
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录数据
          app.clearLoginData();
          
          // 跳转到登录页
          wx.reLaunch({
            url: '/pages/login/login'
          });
        }
      }
    });
  }
});
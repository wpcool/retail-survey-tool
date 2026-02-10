const app = getApp();

Page({
  data: {
    userInfo: {},
    stats: {
      totalRecords: 0,
      todayRecords: 0,
      distinctDays: 0,
      distinctProducts: 0
    },
    last7Days: [],
    recentRecords: [],
    loading: true
  },

  onLoad() {
    this.loadUserInfo();
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
    this.setData({ loading: true });
    
    try {
      // 确保获取用户信息
      let userInfo = this.data.userInfo;
      if (!userInfo || !userInfo.id) {
        userInfo = wx.getStorageSync('userInfo');
        if (userInfo && userInfo.id) {
          this.setData({ userInfo });
        } else {
          console.log('未获取到用户信息');
          this.setData({ loading: false });
          return;
        }
      }
      
      console.log('开始加载统计数据，用户ID:', userInfo.id);
      
      // 调用后端API获取统计
      const res = await app.request({
        url: `/api/surveyors/${userInfo.id}/stats`,
        method: 'GET'
      });
      
      console.log('统计API返回:', res);
      
      // 确保数据格式正确
      if (res && typeof res === 'object') {
        this.setData({
          stats: {
            totalRecords: res.total_records || 0,
            todayRecords: res.today_records || 0,
            distinctDays: res.distinct_days || 0,
            distinctProducts: res.distinct_products || 0
          },
          last7Days: res.last_7_days || [],
          recentRecords: res.recent_records || [],
          loading: false
        });
        console.log('统计数据已更新:', this.data.stats);
      } else {
        throw new Error('API返回数据格式不正确');
      }
    } catch (error) {
      console.error('加载统计失败:', error);
      wx.showToast({ 
        title: error.message || '加载失败', 
        icon: 'none',
        duration: 2000
      });
      // 使用模拟数据
      this.setData({
        stats: {
          totalRecords: 128,
          todayRecords: 5,
          distinctDays: 15,
          distinctProducts: 45
        },
        last7Days: [
          { date: '2026-02-05', count: 5 },
          { date: '2026-02-04', count: 8 },
          { date: '2026-02-03', count: 12 },
          { date: '2026-02-02', count: 6 },
          { date: '2026-02-01', count: 10 }
        ],
        recentRecords: [
          { id: 1, product_name: '西红柿', category: '蔬菜', store_name: '永辉超市', price: 5.99, date: '2026-02-05', time: '10:30' },
          { id: 2, product_name: '猪五花肉', category: '肉类', store_name: '永辉超市', price: 28.50, date: '2026-02-05', time: '10:45' }
        ],
        loading: false
      });
    }
  },

  // 查看记录详情
  viewRecordDetail(e) {
    const recordId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/record-detail/record-detail?id=${recordId}`
    });
  },

  // 查看所有记录
  viewAllRecords() {
    wx.switchTab({ url: '/pages/records/records' });
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
      confirmColor: '#ef4444',
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
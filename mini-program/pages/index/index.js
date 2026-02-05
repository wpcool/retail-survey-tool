const app = getApp();

Page({
  data: {
    userInfo: null,
    today: '',
    tasks: [],
    loading: true,
    hasTask: false,
    stats: {
      today: 0,
      completed: 0,
      pending: 0
    }
  },

  onLoad() {
    // 获取用户信息
    const userInfo = wx.getStorageSync('userInfo');
    this.setData({ userInfo });

    // 设置今日日期
    const today = new Date();
    const dateStr = `${today.getMonth() + 1}月${today.getDate()}日 ${this.getWeekDay(today)}`;
    this.setData({ today: dateStr });

    // 加载任务
    this.loadTasks();
  },

  onShow() {
    // 每次显示页面都刷新数据
    this.loadTasks();
  },

  // 获取星期几
  getWeekDay(date) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return days[date.getDay()];
  },

  // 加载任务列表
  async loadTasks() {
    this.setData({ loading: true });

    try {
      const today = new Date().toISOString().split('T')[0];
      
      // 调用后端API获取今日任务
      const res = await app.request({
        url: `/api/tasks?date=${today}`,
        method: 'GET'
      });

      // 处理任务数据
      const tasks = Array.isArray(res) ? res : [];
      
      // 计算统计
      const completed = tasks.filter(t => t.status === 'completed').length;
      const pending = tasks.filter(t => t.status === 'active').length;

      this.setData({
        tasks: tasks,
        hasTask: tasks.length > 0,
        loading: false,
        stats: {
          today: tasks.length,
          completed: completed,
          pending: pending
        }
      });
    } catch (error) {
      console.error('加载任务失败:', error);
      
      // 如果后端未启动，显示模拟数据
      this.setData({
        tasks: this.getMockTasks(),
        hasTask: true,
        loading: false,
        stats: {
          today: 2,
          completed: 0,
          pending: 2
        }
      });
    }
  },

  // 模拟任务数据（用于测试）
  getMockTasks() {
    return [
      {
        id: 1,
        title: '2024-02-05 生鲜品类调研',
        date: '2024-02-05',
        description: '调研各大超市生鲜商品价格，包括蔬菜、水果、肉类等品类',
        status: 'active',
        item_count: 15,
        created_at: '2024-02-05 08:00'
      },
      {
        id: 2,
        title: '2024-02-05 粮油品类调研',
        date: '2024-02-05',
        description: '调研米面粮油价格变动情况',
        status: 'active',
        item_count: 10,
        created_at: '2024-02-05 08:30'
      }
    ];
  },

  // 刷新任务
  refreshTasks() {
    wx.showLoading({ title: '刷新中...' });
    this.loadTasks().finally(() => {
      wx.hideLoading();
      wx.showToast({ title: '已刷新', icon: 'success' });
    });
  },

  // 选择任务（点击卡片）
  onSelectTask(e) {
    const task = e.currentTarget.dataset.task;
    // 存储选中的任务
    wx.setStorageSync('selectedTask', task);
    wx.showToast({ title: '已选择任务', icon: 'success' });
  },

  // 开始调研
  onStartSurvey(e) {
    const task = e.currentTarget.dataset.task;
    
    // 存储选中的任务
    wx.setStorageSync('selectedTask', task);
    
    // 跳转到新建记录页面
    wx.switchTab({
      url: '/pages/create/create'
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadTasks().finally(() => {
      wx.stopPullDownRefresh();
    });
  }
});
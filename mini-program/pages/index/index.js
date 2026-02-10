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
      const userInfo = this.data.userInfo;
      
      // 调用后端API获取今日任务
      const res = await app.request({
        url: `/api/tasks?date=${today}`,
        method: 'GET'
      });

      // 处理任务数据
      let tasks = Array.isArray(res) ? res : [];
      
      // 如果有用户登录，获取每个任务的完成状态
      if (userInfo && userInfo.id && tasks.length > 0) {
        tasks = await this.loadTaskCompletionStatus(tasks, userInfo.id);
      }
      
      // 计算统计
      const completedTasks = tasks.filter(t => t.status === 'completed').length;
      
      // 计算商品完成数
      let totalCompletedItems = 0;
      let totalItems = 0;
      tasks.forEach(task => {
        if (task.items) {
          totalItems += task.items.length;
          totalCompletedItems += task.items.filter(i => i.is_completed).length;
        }
      });

      this.setData({
        tasks: tasks,
        hasTask: tasks.length > 0,
        loading: false,
        stats: {
          today: tasks.length,
          completed: totalCompletedItems,  // 已完成的商品数
          pending: totalItems - totalCompletedItems,  // 待完成的商品数
          totalItems: totalItems
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
          pending: 2,
          totalItems: 4
        }
      });
    }
  },

  // 加载任务完成状态
  async loadTaskCompletionStatus(tasks, surveyorId) {
    try {
      // 并行获取所有任务的完成状态
      const promises = tasks.map(async (task) => {
        try {
          const res = await app.request({
            url: `/api/tasks/${task.id}/completion/${surveyorId}`,
            method: 'GET'
          });
          
          // 将调研次数标记到商品上
          if (task.items && res.items) {
            const itemCountMap = {};
            res.items.forEach(i => {
              itemCountMap[i.item_id] = i.count;
            });
            
            task.items = task.items.map(item => ({
              ...item,
              record_count: itemCountMap[item.id] || 0,
              is_completed: (itemCountMap[item.id] || 0) > 0
            }));
            
            // 计算该任务的完成进度（按调研次数）
            task.completed_count = res.completed_items;
            task.total_records = res.total_records;
            task.completion_percent = task.items.length > 0 
              ? Math.round((res.completed_items / task.items.length) * 100) 
              : 0;
          }
          
          return task;
        } catch (e) {
          console.error(`获取任务${task.id}完成状态失败:`, e);
          return task;
        }
      });
      
      return await Promise.all(promises);
    } catch (error) {
      console.error('加载完成状态失败:', error);
      return tasks;
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
        completed_count: 5,
        completion_percent: 33,
        created_at: '2024-02-05 08:00',
        items: [
          { id: 1, category: '蔬菜', product_name: '西红柿', is_completed: true },
          { id: 2, category: '蔬菜', product_name: '黄瓜', is_completed: false },
          { id: 3, category: '肉类', product_name: '猪五花肉', is_completed: true },
        ]
      },
      {
        id: 2,
        title: '2024-02-05 粮油品类调研',
        date: '2024-02-05',
        description: '调研米面粮油价格变动情况',
        status: 'active',
        item_count: 10,
        completed_count: 0,
        completion_percent: 0,
        created_at: '2024-02-05 08:30',
        items: [
          { id: 4, category: '大米', product_name: '福临门大米', is_completed: false },
          { id: 5, category: '食用油', product_name: '金龙鱼菜籽油', is_completed: false },
        ]
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
    wx.navigateTo({
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
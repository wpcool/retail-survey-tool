const app = getApp();

Page({
  data: {
    records: [],
    loading: true,
    userInfo: null,
    filterDate: '',
    hasMore: true,
    page: 1,
    pageSize: 20
  },

  onLoad() {
    const userInfo = wx.getStorageSync('userInfo');
    this.setData({ userInfo });
    
    // 默认显示今天的日期
    const today = new Date().toISOString().split('T')[0];
    this.setData({ filterDate: today });
    
    this.loadRecords();
  },

  onShow() {
    // 每次显示刷新数据
    this.loadRecords();
  },

  // 加载记录列表
  async loadRecords(reset = true) {
    if (reset) {
      this.setData({ page: 1, records: [], hasMore: true });
    }
    
    this.setData({ loading: true });
    
    try {
      const { userInfo, filterDate, page, pageSize } = this.data;
      
      if (!userInfo || !userInfo.id) {
        this.setData({ loading: false });
        return;
      }
      
      // 调用后端API获取记录
      let url = `/api/records?surveyor_id=${userInfo.id}`;
      if (filterDate) {
        url += `&date=${filterDate}`;
      }
      
      const res = await app.request({
        url: url,
        method: 'GET'
      });
      
      let records = Array.isArray(res) ? res : [];
      
      // 判断每条记录是否可以编辑（只有当天的可以编辑）
      const today = new Date().toISOString().split('T')[0];
      records = records.map(record => {
        const recordDate = record.created_at ? record.created_at.split('T')[0] : '';
        return {
          ...record,
          isToday: recordDate === today,
          canEdit: recordDate === today
        };
      });
      
      this.setData({
        records: reset ? records : [...this.data.records, ...records],
        loading: false,
        hasMore: records.length >= pageSize
      });
      
    } catch (error) {
      console.error('加载记录失败:', error);
      this.setData({ loading: false });
      
      // 显示模拟数据用于测试
      this.setData({
        records: this.getMockRecords()
      });
    }
  },

  // 模拟数据（用于测试）
  getMockRecords() {
    return [
      {
        id: 1,
        product_name: '西红柿',
        category: '蔬菜',
        store_name: '永辉超市',
        price: 5.99,
        promotion_info: '会员价',
        created_at: '2024-02-05 10:30:00'
      },
      {
        id: 2,
        product_name: '猪五花肉',
        category: '肉类',
        store_name: '永辉超市',
        price: 28.50,
        created_at: '2024-02-05 10:45:00'
      }
    ];
  },

  // 日期选择
  onDateChange(e) {
    const date = e.detail.value;
    this.setData({ filterDate: date });
    this.loadRecords(true);
  },

  // 清除日期筛选
  clearDate() {
    this.setData({ filterDate: '' });
    this.loadRecords(true);
  },

  // 查看记录详情
  viewRecord(e) {
    const recordId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/record-detail/record-detail?id=${recordId}`
    });
  },

  // 编辑记录
  editRecord(e) {
    const recordId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/record-edit/record-edit?id=${recordId}`
    });
  },

  // 删除记录
  deleteRecord(e) {
    const recordId = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条记录吗？删除后不可恢复！',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '删除中...' });
            
            await app.request({
              url: `/api/records/${recordId}`,
              method: 'DELETE'
            });
            
            wx.hideLoading();
            wx.showToast({ title: '删除成功', icon: 'success' });
            
            // 刷新列表
            this.loadRecords(true);
            
          } catch (error) {
            wx.hideLoading();
            wx.showToast({ title: error.message || '删除失败', icon: 'none' });
          }
        }
      }
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadRecords(true).finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 加载更多
  loadMore() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 });
      this.loadRecords(false);
    }
  }
});
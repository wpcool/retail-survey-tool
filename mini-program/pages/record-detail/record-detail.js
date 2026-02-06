const app = getApp();

Page({
  data: {
    recordId: null,
    loading: true,
    isToday: false,
    record: {}
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ recordId: parseInt(options.id) });
      this.loadRecordDetail();
    } else {
      wx.showToast({ title: '记录ID无效', icon: 'none' });
      wx.navigateBack();
    }
  },

  // 加载记录详情
  async loadRecordDetail() {
    this.setData({ loading: true });
    
    try {
      const { recordId } = this.data;
      
      const res = await app.request({
        url: `/api/records/${recordId}`,
        method: 'GET'
      });
      
      // 判断是否是今天的记录
      const today = new Date().toISOString().split('T')[0];
      const recordDate = res.created_at ? res.created_at.split('T')[0] : '';
      const isToday = recordDate === today;
      
      this.setData({
        record: res,
        isToday,
        loading: false
      });
      
    } catch (error) {
      console.error('加载记录失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
      this.setData({ loading: false });
      wx.navigateBack();
    }
  },

  // 返回列表
  goBack() {
    wx.navigateBack();
  }
});
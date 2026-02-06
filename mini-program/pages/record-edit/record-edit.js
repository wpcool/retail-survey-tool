const app = getApp();

Page({
  data: {
    recordId: null,
    loading: true,
    saving: false,
    form: {
      productName: '',
      category: '',
      storeName: '',
      storeAddress: '',
      price: '',
      promotionInfo: '',
      remark: ''
    }
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
      
      this.setData({
        form: {
          productName: res.product_name || '',
          category: res.category || '',
          storeName: res.store_name || '',
          storeAddress: res.store_address || '',
          price: res.price ? String(res.price) : '',
          promotionInfo: res.promotion_info || '',
          remark: res.remark || ''
        },
        loading: false
      });
      
    } catch (error) {
      console.error('加载记录失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
      this.setData({ loading: false });
      wx.navigateBack();
    }
  },

  // 输入框变化
  onInput(e) {
    const { field } = e.currentTarget.dataset;
    const { value } = e.detail;
    
    this.setData({
      [`form.${field}`]: value
    });
  },

  // 验证表单
  validateForm() {
    const { form } = this.data;
    
    if (!form.storeName.trim()) {
      wx.showToast({ title: '请输入店铺名称', icon: 'none' });
      return false;
    }
    
    if (!form.price) {
      wx.showToast({ title: '请输入价格', icon: 'none' });
      return false;
    }
    
    return true;
  },

  // 保存修改
  async saveRecord() {
    if (!this.validateForm()) return;
    
    this.setData({ saving: true });
    wx.showLoading({ title: '保存中...', mask: true });
    
    try {
      const { recordId, form } = this.data;
      
      // 构建提交数据
      const submitData = {
        store_name: form.storeName.trim(),
        store_address: form.storeAddress.trim() || null,
        price: parseFloat(form.price),
        promotion_info: form.promotionInfo.trim() || null,
        remark: form.remark.trim() || null
      };
      
      // 调用后端API更新记录
      await app.request({
        url: `/api/records/${recordId}`,
        method: 'PUT',
        data: submitData
      });
      
      wx.hideLoading();
      this.setData({ saving: false });
      
      wx.showToast({
        title: '修改成功',
        icon: 'success',
        duration: 1500,
        success: () => {
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        }
      });
      
    } catch (error) {
      wx.hideLoading();
      this.setData({ saving: false });
      wx.showToast({ title: error.message || '保存失败', icon: 'none' });
    }
  },

  // 取消编辑
  cancelEdit() {
    wx.navigateBack();
  }
});
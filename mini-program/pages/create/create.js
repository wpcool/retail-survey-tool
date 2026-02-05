const app = getApp();

Page({
  data: {
    taskId: null,
    taskTitle: '',
    categories: ['生鲜', '粮油', '饮料', '零食', '日用品', '家电', '服装', '其他'],
    form: {
      name: '',
      category: '',
      specification: '',
      brand: '',
      price: '',
      promoPrice: '',
      promoInfo: '',
      shop: '',
      shopAddress: '',
      remark: '',
      longitude: null,
      latitude: null
    }
  },

  onLoad(options) {
    // 获取任务信息
    if (options.taskId) {
      this.setData({
        taskId: parseInt(options.taskId),
        taskTitle: decodeURIComponent(options.taskTitle || '')
      });
    }
  },

  onShow() {
    // 每次显示检查是否有选中的任务
    const selectedTask = wx.getStorageSync('selectedTask');
    if (selectedTask && !this.data.taskId) {
      this.setData({
        taskId: selectedTask.id,
        taskTitle: selectedTask.title
      });
      // 清除存储，避免重复
      wx.removeStorageSync('selectedTask');
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

  // 品类选择
  onCategoryChange(e) {
    const { value } = e.detail;
    const category = this.data.categories[value];
    this.setData({
      'form.category': category
    });
  },

  // 获取定位
  getLocation() {
    wx.showLoading({ title: '定位中...' });
    
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const { latitude, longitude } = res;
        
        // 使用腾讯地图API反地理编码
        this.reverseGeocode(latitude, longitude);
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '定位失败', icon: 'none' });
      }
    });
  },

  // 反地理编码
  reverseGeocode(lat, lng) {
    const key = 'YOUR_TENCENT_MAP_KEY';
    const url = `https://apis.map.qq.com/ws/geocoder/v1/?location=${lat},${lng}&key=${key}`;
    
    wx.request({
      url,
      success: (res) => {
        wx.hideLoading();
        
        if (res.data && res.data.status === 0) {
          const address = res.data.result.address;
          this.setData({
            'form.shopAddress': address,
            'form.latitude': lat,
            'form.longitude': lng
          });
          wx.showToast({ title: '定位成功', icon: 'success' });
        } else {
          this.setData({
            'form.shopAddress': `经纬度: ${lat.toFixed(4)}, ${lng.toFixed(4)}`,
            'form.latitude': lat,
            'form.longitude': lng
          });
        }
      },
      fail: () => {
        wx.hideLoading();
        this.setData({
          'form.shopAddress': `经纬度: ${lat.toFixed(4)}, ${lng.toFixed(4)}`,
          'form.latitude': lat,
          'form.longitude': lng
        });
      }
    });
  },

  // 验证表单
  validateForm() {
    const { form, taskId } = this.data;
    
    if (!taskId) {
      wx.showToast({ title: '请先从"任务"页选择调研任务', icon: 'none' });
      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' });
      }, 1500);
      return false;
    }
    
    if (!form.name.trim()) {
      wx.showToast({ title: '请输入商品名称', icon: 'none' });
      return false;
    }
    
    if (!form.category) {
      wx.showToast({ title: '请选择品类', icon: 'none' });
      return false;
    }
    
    if (!form.price) {
      wx.showToast({ title: '请输入价格', icon: 'none' });
      return false;
    }
    
    if (!form.shop.trim()) {
      wx.showToast({ title: '请输入店铺名称', icon: 'none' });
      return false;
    }
    
    return true;
  },

  // 保存记录
  async saveRecord() {
    if (!this.validateForm()) return;
    
    wx.showLoading({ title: '保存中...', mask: true });
    
    try {
      const { form, taskId } = this.data;
      
      // 构建提交数据
      const submitData = {
        task_id: taskId,
        name: form.name.trim(),
        category: form.category,
        specification: form.specification.trim(),
        brand: form.brand.trim(),
        price: parseFloat(form.price),
        promo_price: form.promoPrice ? parseFloat(form.promoPrice) : null,
        promo_info: form.promoInfo.trim() || null,
        shop: form.shop.trim(),
        shop_address: form.shopAddress.trim() || null,
        longitude: form.longitude,
        latitude: form.latitude,
        remark: form.remark.trim() || null
      };
      
      // 调用后端API保存记录
      const res = await app.request({
        url: '/api/records',
        method: 'POST',
        data: submitData
      });
      
      wx.hideLoading();
      
      wx.showToast({
        title: '保存成功',
        icon: 'success',
        duration: 1500
      });
      
      // 清空表单（保留店铺地址）
      this.setData({
        form: {
          name: '',
          category: '',
          specification: '',
          brand: '',
          price: '',
          promoPrice: '',
          promoInfo: '',
          shop: form.shop,  // 保留店铺名
          shopAddress: form.shopAddress,  // 保留地址
          remark: '',
          longitude: form.longitude,
          latitude: form.latitude
        }
      });
      
    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: error.message || '保存失败', icon: 'none' });
    }
  }
});
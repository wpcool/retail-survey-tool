const app = getApp();

Page({
  data: {
    taskId: null,
    taskTitle: '',
    taskItems: [],
    selectedItem: null,
    completedCount: 0,
    totalCount: 0,
    suggestList: [],
    showSuggest: false,
    suggestTimer: null,
    categories: ['生鲜', '粮油', '饮料', '零食', '日用品', '家电', '服装', '其他'],
    // 照片列表
    photos: [],
    form: {
      itemId: null,
      name: '',
      category: '',
      specification: '',
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
    if (options.taskId) {
      this.setData({
        taskId: parseInt(options.taskId),
        taskTitle: decodeURIComponent(options.taskTitle || '')
      });
    }
  },

  onShow() {
    const selectedTask = wx.getStorageSync('selectedTask');
    if (selectedTask) {
      this.setData({
        taskId: selectedTask.id,
        taskTitle: selectedTask.title,
        taskItems: selectedTask.items || []
      });
      
      // 加载完成状态
      this.loadCompletionStatus(selectedTask.id);
      
      if (selectedTask.items && selectedTask.items.length === 1) {
        this.selectTaskItem(selectedTask.items[0]);
      }
    }
  },

  // 加载完成状态
  async loadCompletionStatus(taskId) {
    const userInfo = wx.getStorageSync('userInfo');
    if (!userInfo || !userInfo.id) return;
    
    try {
      const res = await app.request({
        url: `/api/tasks/${taskId}/completion/${userInfo.id}`,
        method: 'GET'
      });
      
      if (res.items) {
        // 更新商品的调研次数
        const itemCountMap = {};
        res.items.forEach(i => {
          itemCountMap[i.item_id] = i.count;
        });
        
        const taskItems = this.data.taskItems.map(item => ({
          ...item,
          is_completed: (itemCountMap[item.id] || 0) > 0,
          record_count: itemCountMap[item.id] || 0
        }));
        
        // 计算调研总次数和已完成商品数
        const completedCount = taskItems.filter(i => i.record_count > 0).length;
        const totalRecordCount = res.total_records || 0;
        
        this.setData({ 
          taskItems,
          completedCount,
          totalCount: taskItems.length,
          totalRecordCount
        });
      }
    } catch (error) {
      console.error('加载完成状态失败:', error);
    }
  },

  onSelectItem(e) {
    const item = e.currentTarget.dataset.item;
    this.selectTaskItem(item);
  },

  selectTaskItem(item) {
    // 如果已经填写过，提示用户
    if (item.is_completed) {
      wx.showModal({
        title: '提示',
        content: '该商品您已经填写过了，确定要重新填写吗？',
        success: (res) => {
          if (res.confirm) {
            this.setSelectedItem(item);
          }
        }
      });
    } else {
      this.setSelectedItem(item);
    }
  },

  setSelectedItem(item) {
    this.setData({
      selectedItem: item,
      'form.itemId': item.id,
      'form.name': item.product_name,
      'form.category': item.category,
      'form.specification': item.product_spec || ''
    });
  },

  onNameInput(e) {
    const value = e.detail.value;
    this.setData({ 'form.name': value });
    
    if (this.data.suggestTimer) {
      clearTimeout(this.data.suggestTimer);
    }
    
    if (!value || value.length < 1) {
      this.setData({ suggestList: [], showSuggest: false });
      return;
    }
    
    const timer = setTimeout(() => {
      this.fetchSuggestions(value);
    }, 300);
    
    this.setData({ suggestTimer: timer });
  },

  async fetchSuggestions(keyword) {
    try {
      const res = await app.request({
        url: '/api/products/suggest?keyword=' + encodeURIComponent(keyword) + '&limit=10',
        method: 'GET'
      });
      
      if (Array.isArray(res)) {
        this.setData({
          suggestList: res,
          showSuggest: true
        });
      }
    } catch (error) {
      console.error('get suggest failed:', error);
    }
  },

  onSelectSuggest(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({
      'form.name': item.name,
      'form.category': item.category,
      'form.specification': item.spec || '',
      suggestList: [],
      showSuggest: false
    });
  },

  onNameFocus() {
    if (this.data.suggestList.length > 0) {
      this.setData({ showSuggest: true });
    }
  },

  onNameBlur() {
    setTimeout(() => {
      this.setData({ showSuggest: false });
    }, 200);
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({ ['form.' + field]: value });
  },

  onCategoryChange(e) {
    const idx = e.detail.value;
    const category = this.data.categories[idx];
    this.setData({ 'form.category': category });
  },

  getLocation() {
    wx.showLoading({ title: '定位中...' });
    
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        const lat = res.latitude;
        const lng = res.longitude;
        this.reverseGeocode(lat, lng);
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '定位失败', icon: 'none' });
      }
    });
  },

  reverseGeocode(lat, lng) {
    const url = 'https://apis.map.qq.com/ws/geocoder/v1/?location=' + lat + ',' + lng + '&key=YOUR_TENCENT_MAP_KEY';
    
    wx.request({
      url: url,
      success: (res) => {
        wx.hideLoading();
        if (res.data && res.data.status === 0) {
          this.setData({
            'form.shopAddress': res.data.result.address,
            'form.latitude': lat,
            'form.longitude': lng
          });
          wx.showToast({ title: '定位成功', icon: 'success' });
        } else {
          this.setData({
            'form.shopAddress': 'lat:' + lat.toFixed(4) + ', lng:' + lng.toFixed(4),
            'form.latitude': lat,
            'form.longitude': lng
          });
        }
      },
      fail: () => {
        wx.hideLoading();
        this.setData({
          'form.shopAddress': 'lat:' + lat.toFixed(4) + ', lng:' + lng.toFixed(4),
          'form.latitude': lat,
          'form.longitude': lng
        });
      }
    });
  },

  validateForm() {
    const form = this.data.form;
    const taskId = this.data.taskId;
    const selectedItem = this.data.selectedItem;
    const photos = this.data.photos;
    
    if (!taskId) {
      wx.showToast({ title: '请先从任务页选择调研任务', icon: 'none' });
      setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 1500);
      return false;
    }
    
    if (!selectedItem) {
      wx.showToast({ title: '请选择要调研的商品', icon: 'none' });
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
    
    if (photos.length === 0) {
      wx.showToast({ title: '请至少拍摄一张商品照片', icon: 'none' });
      return false;
    }
    
    return true;
  },

  async saveRecord() {
    if (!this.validateForm()) return;
    
    wx.showLoading({ title: '保存中...', mask: true });
    
    try {
      const form = this.data.form;
      const selectedItem = this.data.selectedItem;
      const userInfo = wx.getStorageSync('userInfo');
      const photos = this.data.photos;
      
      // 先上传照片
      const uploadedPhotos = [];
      for (let i = 0; i < photos.length; i++) {
        try {
          const uploadRes = await this.uploadPhoto(photos[i]);
          if (uploadRes && uploadRes.url) {
            uploadedPhotos.push(uploadRes.url);
          }
        } catch (err) {
          console.error('上传照片失败:', err);
        }
      }
      
      const submitData = {
        item_id: selectedItem.id,
        surveyor_id: userInfo.id || 1,
        store_name: form.shop.trim(),
        store_address: form.shopAddress.trim() || null,
        price: parseFloat(form.price),
        promotion_info: form.promoInfo.trim() || null,
        remark: form.remark.trim() || null,
        longitude: form.longitude,
        latitude: form.latitude,
        photos: uploadedPhotos
      };
      
      await app.request({
        url: '/api/records',
        method: 'POST',
        data: submitData
      });
      
      wx.hideLoading();
      
      wx.showModal({
        title: '保存成功',
        content: '调研记录已保存',
        confirmText: '继续录入',
        cancelText: '返回任务',
        success: (modalRes) => {
          if (modalRes.confirm) {
            this.resetFormForNext();
          } else {
            wx.switchTab({ url: '/pages/index/index' });
          }
        }
      });
      
    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: error.message || '保存失败', icon: 'none', duration: 2000 });
    }
  },

  // ========== 拍照相关方法 ==========

  // 上传单张照片
  uploadPhoto(filePath) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/upload`,
        filePath: filePath,
        name: 'file',
        formData: { type: 'image' },
        header: {
          'Authorization': `Bearer ${app.globalData.token || ''}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            try {
              const data = JSON.parse(res.data);
              resolve(data);
            } catch (e) {
              reject(new Error('解析响应失败'));
            }
          } else {
            reject(new Error('上传失败'));
          }
        },
        fail: reject
      });
    });
  },

  // 拍照
  takePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        const photos = this.data.photos.concat(tempFilePath);
        this.setData({ photos });
      },
      fail: (err) => {
        if (err.errMsg && err.errMsg.includes('cancel')) {
          return; // 用户取消，不提示
        }
        wx.showToast({ title: '拍照失败', icon: 'none' });
      }
    });
  },

  // 预览照片
  previewPhoto(e) {
    const index = e.currentTarget.dataset.index;
    wx.previewImage({
      urls: this.data.photos,
      current: this.data.photos[index]
    });
  },

  // 删除照片
  deletePhoto(e) {
    const index = e.currentTarget.dataset.index;
    const photos = this.data.photos.filter((_, i) => i !== index);
    this.setData({ photos });
  },

  resetFormForNext() {
    const form = this.data.form;
    this.setData({
      selectedItem: null,
      suggestList: [],
      showSuggest: false,
      photos: [],
      form: {
        itemId: null,
        name: '',
        category: '',
        specification: '',
        price: '',
        promoPrice: '',
        promoInfo: '',
        shop: form.shop,
        shopAddress: form.shopAddress,
        remark: '',
        longitude: form.longitude,
        latitude: form.latitude
      }
    });
    
    wx.showToast({ title: '请继续选择商品录入', icon: 'none', duration: 1500 });
  }
});

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
    return new Promise((resolve, reject) => {
      wx.showLoading({ title: '定位中...' });
      
      wx.getLocation({
        type: 'gcj02',
        success: (res) => {
          const lat = res.latitude;
          const lng = res.longitude;
          this.reverseGeocode(lat, lng).then(resolve).catch(reject);
        },
        fail: () => {
          wx.hideLoading();
          wx.showToast({ title: '定位失败', icon: 'none' });
          reject(new Error('定位失败'));
        }
      });
    });
  },

  reverseGeocode(lat, lng) {
    return new Promise((resolve, reject) => {
      const url = 'https://apis.map.qq.com/ws/geocoder/v1/?location=' + lat + ',' + lng + '&key=4C2BZ-TD3KJ-RLSFO-DU6JY-PATN5-C4BDJ';
      
      wx.request({
        url: url,
        success: (res) => {
          wx.hideLoading();
          console.log('腾讯地图 API 返回:', res.data);
          
          if (res.data && res.data.status === 0) {
            // 逆地理编码成功
            const address = res.data.result && res.data.result.address ? res.data.result.address : '';
            const formattedAddress = res.data.result && res.data.result.formatted_addresses && res.data.result.formatted_addresses.recommend ? 
              res.data.result.formatted_addresses.recommend : address;
            
            console.log('获取到地址:', formattedAddress || address);
            
            if (formattedAddress || address) {
              this.setData({
                'form.shopAddress': formattedAddress || address,
                'form.latitude': lat,
                'form.longitude': lng
              });
              wx.showToast({ title: '定位成功', icon: 'success' });
            } else {
              // 有响应但没有地址
              wx.showToast({ title: '未获取到地址信息', icon: 'none' });
              this.setData({
                'form.latitude': lat,
                'form.longitude': lng
              });
            }
            resolve();
          } else {
            // API 返回错误
            console.error('地理编码失败:', res.data);
            const errorMsg = res.data && res.data.message ? res.data.message : '未知错误';
            
            // 常见错误提示
            let tip = '';
            if (res.data && res.data.status === 311) {
              tip = 'Key未绑定小程序，请在腾讯地图控制台绑定';
            } else if (res.data && res.data.status === 310) {
              tip = 'Key权限不足，请申请webservice API权限';
            }
            
            if (tip) {
              wx.showModal({
                title: '定位服务配置错误',
                content: tip + '\n错误码: ' + res.data.status,
                showCancel: false
              });
            }
            
            // 失败时不设置 shopAddress，让水印显示坐标
            this.setData({
              'form.latitude': lat,
              'form.longitude': lng
            });
            resolve();
          }
        },
        fail: (err) => {
          wx.hideLoading();
          console.error('请求失败:', err);
          wx.showToast({ title: '网络请求失败', icon: 'none' });
          this.setData({
            'form.latitude': lat,
            'form.longitude': lng
          });
          resolve(); // 即使失败也继续
        }
      });
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
    // 如果还没有获取位置，先获取位置
    const form = this.data.form;
    if (!form.latitude || !form.longitude) {
      this.getLocation().then(() => {
        this.doTakePhoto();
      }).catch(() => {
        // 获取位置失败也继续拍照
        this.doTakePhoto();
      });
    } else {
      this.doTakePhoto();
    }
  },

  // 执行拍照
  doTakePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: async (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        
        wx.showLoading({ title: '处理中...', mask: true });
        
        try {
          // 添加水印
          const watermarkedPath = await this.addWatermark(tempFilePath);
          const photos = this.data.photos.concat(watermarkedPath);
          this.setData({ photos });
          wx.hideLoading();
        } catch (err) {
          console.error('添加水印失败:', err);
          wx.hideLoading();
          // 如果水印添加失败，使用原图
          const photos = this.data.photos.concat(tempFilePath);
          this.setData({ photos });
          wx.showToast({ title: '水印添加失败，使用原图', icon: 'none' });
        }
      },
      fail: (err) => {
        if (err.errMsg && err.errMsg.includes('cancel')) {
          return; // 用户取消，不提示
        }
        wx.showToast({ title: '拍照失败', icon: 'none' });
      }
    });
  },

  // 添加水印
  addWatermark(imagePath) {
    return new Promise((resolve, reject) => {
      // 获取图片信息
      wx.getImageInfo({
        src: imagePath,
        success: (imageInfo) => {
          const width = imageInfo.width;
          const height = imageInfo.height;
          
          // 创建 canvas 上下文
          const query = wx.createSelectorQuery();
          query.select('#watermarkCanvas')
            .fields({ node: true, size: true })
            .exec((res) => {
              if (!res[0] || !res[0].node) {
                reject(new Error('canvas 创建失败'));
                return;
              }
              
              const canvas = res[0].node;
              const ctx = canvas.getContext('2d');
              
              // 设置 canvas 尺寸为图片尺寸
              canvas.width = width;
              canvas.height = height;
              
              // 绘制原图
              const img = canvas.createImage();
              img.src = imagePath;
              img.onload = () => {
                ctx.drawImage(img, 0, 0, width, height);
                
                // 获取当前时间和位置信息
                const now = new Date();
                const timeStr = now.toLocaleString('zh-CN', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit'
                });
                
                const form = this.data.form;
                const locationStr = form.shopAddress || '未知位置';
                const latStr = form.latitude ? `Lat: ${form.latitude.toFixed(4)}` : '';
                const lngStr = form.longitude ? `Lng: ${form.longitude.toFixed(4)}` : '';
                
                // 水印样式
                const padding = 20;
                const lineHeight = 36;
                const fontSize = 24;
                const bgPadding = 12;
                
                // 计算水印背景高度
                let textY = height - padding - bgPadding;
                const lines = [];
                
                // 添加时间行
                lines.push(`📅 ${timeStr}`);
                
                // 添加位置行（只有当有真实地址时，且地址不是坐标字符串）
                if (locationStr && locationStr.trim() !== '' && 
                    locationStr !== '未知位置' && 
                    !locationStr.includes('lat:')) {
                  lines.push(`📍 ${locationStr}`);
                }
                
                // 添加坐标行（无论地址是否获取成功，都显示坐标）
                if (latStr && lngStr) {
                  lines.push(`🌐 ${latStr}, ${lngStr}`);
                }
                
                const bgHeight = lines.length * lineHeight + bgPadding * 2;
                const bgY = height - bgHeight - padding;
                
                // 绘制半透明背景
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(padding, bgY, width - padding * 2, bgHeight);
                
                // 绘制文字
                ctx.fillStyle = '#ffffff';
                ctx.font = `${fontSize}px sans-serif`;
                ctx.textBaseline = 'top';
                
                lines.forEach((line, index) => {
                  const y = bgY + bgPadding + index * lineHeight;
                  ctx.fillText(line, padding + bgPadding, y);
                });
                
                // 导出图片
                wx.canvasToTempFilePath({
                  canvas: canvas,
                  success: (exportRes) => {
                    resolve(exportRes.tempFilePath);
                  },
                  fail: reject
                });
              };
              
              img.onerror = () => {
                reject(new Error('图片加载失败'));
              };
            });
        },
        fail: reject
      });
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
  },

  // ========== 测试功能 ==========
  
  // 测试逆地理编码（用于排查问题）
  testGeocoder() {
    wx.showLoading({ title: '测试中...' });
    
    // 使用北京天安门作为测试坐标
    const testLat = 39.9049;
    const testLng = 116.4053;
    
    const url = 'https://apis.map.qq.com/ws/geocoder/v1/?location=' + testLat + ',' + testLng + '&key=4C2BZ-TD3KJ-RLSFO-DU6JY-PATN5-C4BDJ';
    
    wx.request({
      url: url,
      success: (res) => {
        wx.hideLoading();
        console.log('测试逆地理编码返回:', res.data);
        
        if (res.data && res.data.status === 0) {
          const address = res.data.result && res.data.result.address ? res.data.result.address : '';
          const recommend = res.data.result && res.data.result.formatted_addresses && res.data.result.formatted_addresses.recommend ? 
            res.data.result.formatted_addresses.recommend : '';
          
          wx.showModal({
            title: '逆地理编码测试成功',
            content: `标准地址: ${address}\n推荐地址: ${recommend}`,
            showCancel: false
          });
        } else {
          const status = res.data ? res.data.status : '未知';
          const message = res.data && res.data.message ? res.data.message : '未知错误';
          
          let tip = '';
          if (status === 311) tip = '（Key未绑定小程序）';
          else if (status === 310) tip = '（Key权限不足）';
          else if (status === 120) tip = '（请求来源未被授权）';
          
          wx.showModal({
            title: '逆地理编码测试失败',
            content: `状态码: ${status}\n错误信息: ${message}${tip}\n\n请在腾讯地图控制台检查Key配置`,
            showCancel: false
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('测试请求失败:', err);
        wx.showModal({
          title: '请求失败',
          content: '网络请求失败，请检查网络连接和域名配置',
          showCancel: false
        });
      }
    });
  }
});

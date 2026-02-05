const app = getApp();

Page({
  data: {
    username: '',
    password: '',
    loading: false,
    isWechatLogin: false // 是否使用微信登录
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token');
    if (token) {
      wx.switchTab({ url: '/pages/index/index' });
    }
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 切换登录方式
  switchLoginType() {
    this.setData({
      isWechatLogin: !this.data.isWechatLogin,
      username: '',
      password: ''
    });
  },

  // 账号密码登录
  async onLogin() {
    const { username, password } = this.data;

    // 表单验证
    if (!username.trim()) {
      wx.showToast({ title: '请输入用户名', icon: 'none' });
      return;
    }

    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }

    if (password.length < 6) {
      wx.showToast({ title: '密码至少6位', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      const res = await app.request({
        url: '/api/login',
        method: 'POST',
        data: {
          username: username.trim(),
          password: password
        }
      });

      if (res.success) {
        // 保存登录信息
        wx.setStorageSync('token', res.token || 'mock_token');
        wx.setStorageSync('userInfo', {
          id: res.user_id,
          name: res.name,
          username: username.trim()
        });

        app.globalData.token = res.token || 'mock_token';
        app.globalData.userInfo = {
          id: res.user_id,
          name: res.name,
          username: username.trim()
        };

        wx.showToast({ 
          title: `欢迎，${res.name}`, 
          icon: 'success',
          duration: 1500
        });

        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' });
        }, 1500);
      } else {
        wx.showToast({ title: res.message || '登录失败', icon: 'none' });
      }
    } catch (error) {
      console.error('登录失败:', error);
      wx.showToast({ 
        title: error.message || '网络错误，请稍后重试', 
        icon: 'none' 
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 微信一键登录
  async onWechatLogin() {
    this.setData({ loading: true });

    try {
      // 获取微信登录code
      const loginRes = await wx.login();
      
      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败');
      }

      // 调用后端微信登录接口
      const res = await app.request({
        url: '/api/wechat/login',
        method: 'POST',
        data: {
          code: loginRes.code
        }
      });

      if (res.success) {
        // 保存登录信息
        wx.setStorageSync('token', res.token);
        wx.setStorageSync('userInfo', {
          id: res.user_id,
          name: res.name,
          openid: res.openid
        });

        app.globalData.token = res.token;
        app.globalData.userInfo = {
          id: res.user_id,
          name: res.name,
          openid: res.openid
        };

        wx.showToast({ 
          title: `欢迎，${res.name}`, 
          icon: 'success' 
        });

        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' });
        }, 1500);
      } else {
        // 如果是新用户，可能需要绑定账号
        if (res.need_bind) {
          wx.showModal({
            title: '账号未绑定',
            content: '您的微信尚未绑定调研账号，请联系管理员进行绑定',
            showCancel: false
          });
        } else {
          wx.showToast({ title: res.message || '登录失败', icon: 'none' });
        }
      }
    } catch (error) {
      console.error('微信登录失败:', error);
      wx.showToast({ 
        title: error.message || '微信登录失败', 
        icon: 'none' 
      });
    } finally {
      this.setData({ loading: false });
    }
  }
});
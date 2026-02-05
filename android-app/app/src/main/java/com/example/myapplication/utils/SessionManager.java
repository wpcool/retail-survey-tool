package com.example.myapplication.utils;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * 会话管理类
 * 管理用户登录状态和信息
 */
public class SessionManager {
    
    // SharedPreferences 名称
    private static final String PREF_NAME = "SurveySession";
    
    // 存储的键
    private static final String KEY_IS_LOGGED_IN = "isLoggedIn";
    private static final String KEY_USER_ID = "userId";
    private static final String KEY_USER_NAME = "userName";
    private static final String KEY_USER_USERNAME = "userUsername";
    private static final String KEY_LOGIN_TIME = "loginTime";
    
    private SharedPreferences pref;
    private SharedPreferences.Editor editor;
    
    public SessionManager(Context context) {
        pref = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        editor = pref.edit();
    }
    
    /**
     * 创建登录会话
     */
    public void createLoginSession(int userId, String userName, String username) {
        editor.putBoolean(KEY_IS_LOGGED_IN, true);
        editor.putInt(KEY_USER_ID, userId);
        editor.putString(KEY_USER_NAME, userName);
        editor.putString(KEY_USER_USERNAME, username);
        editor.putLong(KEY_LOGIN_TIME, System.currentTimeMillis());
        editor.commit();
    }
    
    /**
     * 检查是否已登录
     */
    public boolean isLoggedIn() {
        return pref.getBoolean(KEY_IS_LOGGED_IN, false);
    }
    
    /**
     * 获取用户ID
     */
    public int getUserId() {
        return pref.getInt(KEY_USER_ID, -1);
    }
    
    /**
     * 获取用户姓名
     */
    public String getUserName() {
        return pref.getString(KEY_USER_NAME, "");
    }
    
    /**
     * 获取用户名
     */
    public String getUsername() {
        return pref.getString(KEY_USER_USERNAME, "");
    }
    
    /**
     * 获取登录时间
     */
    public long getLoginTime() {
        return pref.getLong(KEY_LOGIN_TIME, 0);
    }
    
    /**
     * 清除会话（退出登录）
     */
    public void clearSession() {
        editor.clear();
        editor.commit();
    }
    
    /**
     * 检查会话是否过期（默认7天）
     */
    public boolean isSessionExpired() {
        long loginTime = getLoginTime();
        if (loginTime == 0) return true;
        
        long currentTime = System.currentTimeMillis();
        long sessionDuration = 7 * 24 * 60 * 60 * 1000; // 7天
        
        return (currentTime - loginTime) > sessionDuration;
    }
}
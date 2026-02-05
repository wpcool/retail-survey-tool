package com.example.myapplication.model;

import com.google.gson.annotations.SerializedName;

/**
 * 登录响应数据类
 */
public class LoginResponse {
    
    private boolean success;
    private String message;
    
    @SerializedName("user_id")
    private int userId;
    
    private String name;
    private String token;
    
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public int getUserId() {
        return userId;
    }
    
    public void setUserId(int userId) {
        this.userId = userId;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getToken() {
        return token;
    }
    
    public void setToken(String token) {
        this.token = token;
    }
}
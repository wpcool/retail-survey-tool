package com.example.myapplication.model;

import com.google.gson.annotations.SerializedName;

/**
 * 调研人员数据类
 */
public class Surveyor {
    
    private int id;
    private String username;
    private String name;
    private String phone;
    
    @SerializedName("is_active")
    private boolean isActive;
    
    @SerializedName("created_at")
    private String createdAt;
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getPhone() {
        return phone;
    }
    
    public void setPhone(String phone) {
        this.phone = phone;
    }
    
    public boolean isActive() {
        return isActive;
    }
    
    public void setActive(boolean active) {
        isActive = active;
    }
    
    public String getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}
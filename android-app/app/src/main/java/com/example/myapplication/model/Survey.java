package com.example.myapplication.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class Survey {
    private int id;
    
    // 任务相关字段
    private String title;
    private String date;
    private String description;
    private String status;
    
    @SerializedName("item_count")
    private int itemCount;
    
    // 记录相关字段
    @SerializedName("store_name")
    private String storeName;
    
    @SerializedName("store_address")
    private String storeAddress;
    
    @SerializedName("surveyor_id")
    private int surveyorId;
    
    @SerializedName("item_id")
    private int itemId;
    
    private Double latitude;
    private Double longitude;
    private List<String> images;

    // 构造函数
    public Survey() {}

    public Survey(String storeName, String date, String description) {
        this.storeName = storeName;
        this.date = date;
        this.description = description;
    }

    // Getter 和 Setter
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDate() { return date; }
    public void setDate(String date) { this.date = date; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public int getItemCount() { return itemCount; }
    public void setItemCount(int itemCount) { this.itemCount = itemCount; }

    public String getStoreName() { return storeName; }
    public void setStoreName(String storeName) { this.storeName = storeName; }

    public String getStoreAddress() { return storeAddress; }
    public void setStoreAddress(String storeAddress) { this.storeAddress = storeAddress; }

    public int getSurveyorId() { return surveyorId; }
    public void setSurveyorId(int surveyorId) { this.surveyorId = surveyorId; }

    public int getItemId() { return itemId; }
    public void setItemId(int itemId) { this.itemId = itemId; }

    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }

    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }

    public List<String> getImages() { return images; }
    public void setImages(List<String> images) { this.images = images; }
}

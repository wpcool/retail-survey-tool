package com.example.myapplication.api;

import com.example.myapplication.model.LoginRequest;
import com.example.myapplication.model.LoginResponse;
import com.example.myapplication.model.Survey;
import com.example.myapplication.model.Surveyor;
import java.util.List;
import java.util.Map;
import okhttp3.MultipartBody;
import retrofit2.Call;
import retrofit2.http.*;

public interface SurveyApi {
    
    // ==================== 登录相关 ====================
    
    /**
     * 用户登录
     */
    @POST("api/login")
    Call<LoginResponse> login(@Body LoginRequest request);
    
    /**
     * 获取人员信息（用于检查账号状态）
     */
    @GET("api/surveyors/{surveyor_id}")
    Call<Surveyor> getSurveyor(@Path("surveyor_id") int surveyorId);
    
    // ==================== 任务相关 ====================
    
    /**
     * 获取任务列表
     */
    @GET("api/tasks")
    Call<List<Survey>> getSurveys();
    
    /**
     * 获取今日任务
     */
    @GET("api/tasks/today/{surveyor_id}")
    Call<Survey> getTodayTask(@Path("surveyor_id") int surveyorId);
    
    // ==================== 记录相关 ====================
    
    /**
     * 创建调研记录
     */
    @POST("api/records")
    Call<Map<String, Object>> createSurvey(@Body Survey survey);
    
    /**
     * 上传图片
     */
    @Multipart
    @POST("api/upload/image")
    Call<Map<String, String>> uploadImage(@Part MultipartBody.Part image);
}
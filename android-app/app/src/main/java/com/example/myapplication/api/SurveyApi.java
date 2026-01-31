package com.example.myapplication.api;

import com.example.myapplication.model.Survey;
import java.util.List;
import java.util.Map;
import okhttp3.MultipartBody;
import retrofit2.Call;
import retrofit2.http.*;

public interface SurveyApi {
    
    // 获取任务列表（替代原来的 surveys）
    @GET("api/tasks")
    Call<List<Survey>> getSurveys();
    
    // 创建记录（替代原来的 survey/upload）
    @POST("api/records")
    Call<Map<String, Object>> createSurvey(@Body Survey survey);
    
    @Multipart
    @POST("api/upload/image")
    Call<Map<String, String>> uploadImage(@Part MultipartBody.Part image);
}

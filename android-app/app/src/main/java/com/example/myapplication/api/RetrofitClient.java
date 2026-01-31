package com.example.myapplication.api;

import android.util.Log;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import java.util.concurrent.TimeUnit;

public class RetrofitClient {
    
    private static final String TAG = "RetrofitClient";
    
    // 修改为你的服务器地址
    // 模拟器测试: http://10.0.2.2:8000/
    // 真机测试: http://你的电脑IP:8000/
    private static final String BASE_URL = "http://10.0.2.2:8000/";
    
    private static Retrofit retrofit = null;
    
    public static SurveyApi getApi() {
        if (retrofit == null) {
            Log.d(TAG, "初始化 Retrofit，BASE_URL: " + BASE_URL);
            
            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);
            
            OkHttpClient client = new OkHttpClient.Builder()
                    .addInterceptor(logging)
                    .connectTimeout(10, TimeUnit.SECONDS)
                    .readTimeout(10, TimeUnit.SECONDS)
                    .writeTimeout(10, TimeUnit.SECONDS)
                    .build();
            
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .client(client)
                    .build();
        }
        return retrofit.create(SurveyApi.class);
    }
}

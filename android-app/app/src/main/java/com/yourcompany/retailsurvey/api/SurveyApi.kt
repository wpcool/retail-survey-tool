package com.yourcompany.retailsurvey.api

import com.yourcompany.retailsurvey.data.model.*
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface SurveyApi {
    
    @GET("api/surveys")
    suspend fun getSurveys(): Response<List<SurveyData>>
    
    @GET("api/surveys/{id}")
    suspend fun getSurvey(@Path("id") id: String): Response<SurveyData>
    
    @POST("api/survey/upload")
    suspend fun uploadSurvey(
        @Body survey: CreateSurveyRequest
    ): Response<UploadResult>
    
    @Multipart
    @POST("api/upload/image")
    suspend fun uploadImage(
        @Part image: MultipartBody.Part
    ): Response<Map<String, String>>
    
    @DELETE("api/surveys/{id}")
    suspend fun deleteSurvey(@Path("id") id: String): Response<ApiResponse<Unit>>
}

package com.yourcompany.retailsurvey.di

import com.yourcompany.retailsurvey.api.RetrofitClient
import com.yourcompany.retailsurvey.api.SurveyApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideSurveyApi(): SurveyApi {
        return RetrofitClient.api
    }
}

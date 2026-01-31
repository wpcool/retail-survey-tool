package com.yourcompany.retailsurvey.ui.viewmodel

import android.content.Context
import android.location.Location
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.yourcompany.retailsurvey.api.SurveyApi
import com.yourcompany.retailsurvey.data.model.*
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

@HiltViewModel
class SurveyViewModel @Inject constructor(
    private val api: SurveyApi,
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val _surveys = MutableStateFlow<List<SurveyData>>(emptyList())
    val surveys: StateFlow<List<SurveyData>> = _surveys

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    private val _uploadProgress = MutableStateFlow(0)
    val uploadProgress: StateFlow<Int> = _uploadProgress

    private val _currentLocation = MutableStateFlow<Location?>(null)
    val currentLocation: StateFlow<Location?> = _currentLocation

    fun loadSurveys() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val response = api.getSurveys()
                if (response.isSuccessful) {
                    _surveys.value = response.body() ?: emptyList()
                } else {
                    _error.value = "加载失败: ${response.message()}"
                }
            } catch (e: Exception) {
                _error.value = "网络错误: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun createSurvey(
        storeName: String,
        surveyType: SurveyType,
        locationName: String?,
        imageUris: List<Uri>,
        onSuccess: () -> Unit
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            _uploadProgress.value = 0

            try {
                // 上传图片
                val imageUrls = mutableListOf<String>()
                imageUris.forEachIndexed { index, uri ->
                    val url = uploadImage(uri)
                    if (url != null) {
                        imageUrls.add(url)
                    }
                    _uploadProgress.value = ((index + 1) * 100) / imageUris.size
                }

                // 创建调研数据
                val survey = CreateSurveyRequest(
                    storeName = storeName,
                    surveyDate = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date()),
                    surveyType = surveyType.name,
                    locationName = locationName,
                    latitude = _currentLocation.value?.latitude,
                    longitude = _currentLocation.value?.longitude,
                    images = imageUrls
                )

                val response = api.uploadSurvey(survey)
                if (response.isSuccessful && response.body()?.success == true) {
                    onSuccess()
                    loadSurveys()
                } else {
                    _error.value = response.body()?.message ?: "上传失败"
                }
            } catch (e: Exception) {
                _error.value = "错误: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    private suspend fun uploadImage(uri: Uri): String? {
        return try {
            val file = uriToFile(uri) ?: return null
            val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
            val body = MultipartBody.Part.createFormData("file", file.name, requestFile)
            
            val response = api.uploadImage(body)
            if (response.isSuccessful) {
                response.body()?.get("url") ?: response.body()?.get("filename")
            } else null
        } catch (e: Exception) {
            null
        }
    }

    private fun uriToFile(uri: Uri): File? {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return null
            val file = File(context.cacheDir, "temp_image_${System.currentTimeMillis()}.jpg")
            file.outputStream().use { output ->
                inputStream.copyTo(output)
            }
            file
        } catch (e: Exception) {
            null
        }
    }

    fun updateLocation(location: Location) {
        _currentLocation.value = location
    }

    fun clearError() {
        _error.value = null
    }
}

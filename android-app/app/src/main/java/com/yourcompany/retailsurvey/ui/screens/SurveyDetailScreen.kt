package com.yourcompany.retailsurvey.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.rememberAsyncImagePainter
import com.yourcompany.retailsurvey.ui.viewmodel.SurveyViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SurveyDetailScreen(
    surveyId: String?,
    onBack: () -> Unit,
    viewModel: SurveyViewModel = hiltViewModel()
) {
    val surveys by viewModel.surveys.collectAsState()
    val survey = surveys.find { it.id == surveyId }
    
    LaunchedEffect(surveyId) {
        if (surveys.isEmpty()) {
            viewModel.loadSurveys()
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("调研详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                }
            )
        }
    ) { padding ->
        if (survey == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(padding)
                    .padding(16.dp)
            ) {
                // 门店名称
                Text(
                    text = survey.storeName,
                    style = MaterialTheme.typography.headlineSmall
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // 信息卡片
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        DetailItem(
                            icon = Icons.Default.Category,
                            label = "调研类型",
                            value = getSurveyTypeDisplay(survey.surveyType)
                        )
                        
                        DetailItem(
                            icon = Icons.Default.CalendarToday,
                            label = "调研日期",
                            value = survey.surveyDate
                        )
                        
                        if (!survey.locationName.isNullOrEmpty()) {
                            DetailItem(
                                icon = Icons.Default.LocationOn,
                                label = "位置",
                                value = survey.locationName
                            )
                        }
                        
                        if (survey.latitude != null && survey.longitude != null) {
                            DetailItem(
                                icon = Icons.Default.Map,
                                label = "坐标",
                                value = "${String.format("%.6f", survey.latitude)}, ${String.format("%.6f", survey.longitude)}"
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // 照片
                if (!survey.images.isNullOrEmpty()) {
                    Text(
                        text = "照片 (${survey.images.size})",
                        style = MaterialTheme.typography.titleMedium
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(survey.images) { imageUrl ->
                            val fullUrl = if (imageUrl.startsWith("http")) {
                                imageUrl
                            } else {
                                // 假设图片在服务器上的路径
                                "http://10.0.2.2:8000/uploads/$imageUrl"
                            }
                            
                            Card(
                                modifier = Modifier.size(150.dp)
                            ) {
                                Image(
                                    painter = rememberAsyncImagePainter(fullUrl),
                                    contentDescription = null,
                                    modifier = Modifier.fillMaxSize(),
                                    contentScale = ContentScale.Crop
                                )
                            }
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // 创建时间
                Text(
                    text = "创建时间: ${formatDate(survey.createdAt)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun DetailItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(24.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        
        Spacer(modifier = Modifier.width(16.dp))
        
        Column {
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

private fun getSurveyTypeDisplay(type: String): String {
    return when (type) {
        "PRICE_CHECK" -> "价格检查"
        "INVENTORY" -> "库存盘点"
        "SHELF_CHECK" -> "货架检查"
        "PROMOTION" -> "促销活动"
        "COMPETITOR" -> "竞品调研"
        else -> type
    }
}

private fun formatDate(dateString: String?): String {
    if (dateString == null) return "未知"
    return try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val outputFormat = SimpleDateFormat("yyyy年MM月dd日 HH:mm", Locale.getDefault())
        val date = inputFormat.parse(dateString)
        outputFormat.format(date ?: Date())
    } catch (e: Exception) {
        dateString
    }
}

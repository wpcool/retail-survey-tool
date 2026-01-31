package com.yourcompany.retailsurvey

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.yourcompany.retailsurvey.ui.screens.*
import com.yourcompany.retailsurvey.ui.theme.RetailSurveyTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            RetailSurveyTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    
                    NavHost(
                        navController = navController,
                        startDestination = "survey_list"
                    ) {
                        composable("survey_list") {
                            SurveyListScreen(
                                onCreateNew = { navController.navigate("create_survey") },
                                onSurveyClick = { surveyId ->
                                    navController.navigate("survey_detail/$surveyId")
                                }
                            )
                        }
                        
                        composable("create_survey") {
                            CreateSurveyScreen(
                                onBack = { navController.popBackStack() },
                                onSurveyCreated = { navController.popBackStack() }
                            )
                        }
                        
                        composable("survey_detail/{surveyId}") { backStackEntry ->
                            val surveyId = backStackEntry.arguments?.getString("surveyId")
                            SurveyDetailScreen(
                                surveyId = surveyId,
                                onBack = { navController.popBackStack() }
                            )
                        }
                    }
                }
            }
        }
    }
}

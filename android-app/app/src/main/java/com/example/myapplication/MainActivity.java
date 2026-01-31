package com.example.myapplication;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.myapplication.api.RetrofitClient;
import com.example.myapplication.model.Survey;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private RecyclerView recyclerView;
    private SurveyAdapter adapter;
    private ProgressBar progressBar;
    private Button btnCreate;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        recyclerView = findViewById(R.id.recyclerView);
        progressBar = findViewById(R.id.progressBar);
        btnCreate = findViewById(R.id.btnCreate);

        adapter = new SurveyAdapter();
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);

        btnCreate.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, CreateSurveyActivity.class);
            startActivity(intent);
        });

        loadSurveys();
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadSurveys();
    }

    private void loadSurveys() {
        progressBar.setVisibility(android.view.View.VISIBLE);
        Log.d(TAG, "开始加载调研列表...");

        RetrofitClient.getApi().getSurveys().enqueue(new Callback<List<Survey>>() {
            @Override
            public void onResponse(Call<List<Survey>> call, Response<List<Survey>> response) {
                progressBar.setVisibility(android.view.View.GONE);
                Log.d(TAG, "响应码: " + response.code());
                
                if (response.isSuccessful() && response.body() != null) {
                    Log.d(TAG, "加载成功，数量: " + response.body().size());
                    adapter.setSurveys(response.body());
                } else {
                    Log.e(TAG, "加载失败，响应码: " + response.code());
                    Toast.makeText(MainActivity.this, 
                        "加载失败: " + response.code(), Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<List<Survey>> call, Throwable t) {
                progressBar.setVisibility(android.view.View.GONE);
                Log.e(TAG, "网络错误: " + t.getMessage(), t);
                Toast.makeText(MainActivity.this, 
                    "网络错误: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}

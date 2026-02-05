package com.example.myapplication;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.myapplication.api.RetrofitClient;
import com.example.myapplication.model.Survey;
import com.example.myapplication.utils.SessionManager;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 主Activity - 显示调研任务列表
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    
    private RecyclerView recyclerView;
    private SurveyAdapter adapter;
    private ProgressBar progressBar;
    private Button btnCreate;
    private TextView tvEmpty;
    
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 检查登录状态
        sessionManager = new SessionManager(this);
        if (!sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }
        
        setContentView(R.layout.activity_main);
        
        // 设置Toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("零售调研系统");
        }
        
        // 显示欢迎信息
        String userName = sessionManager.getUserName();
        Toast.makeText(this, "欢迎，" + userName, Toast.LENGTH_SHORT).show();
        
        // 初始化视图
        recyclerView = findViewById(R.id.recyclerView);
        progressBar = findViewById(R.id.progressBar);
        btnCreate = findViewById(R.id.btnCreate);
        tvEmpty = findViewById(R.id.tvEmpty);
        
        // 设置RecyclerView
        adapter = new SurveyAdapter();
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);
        
        // 创建调研按钮
        btnCreate.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, CreateSurveyActivity.class);
            startActivity(intent);
        });
        
        // 加载数据
        loadSurveys();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        loadSurveys();
    }
    
    /**
     * 加载调研任务列表
     */
    private void loadSurveys() {
        progressBar.setVisibility(View.VISIBLE);
        tvEmpty.setVisibility(View.GONE);

        RetrofitClient.getApi().getSurveys().enqueue(new Callback<List<Survey>>() {
            @Override
            public void onResponse(Call<List<Survey>> call, Response<List<Survey>> response) {
                progressBar.setVisibility(View.GONE);
                
                if (response.isSuccessful() && response.body() != null) {
                    List<Survey> surveys = response.body();
                    
                    if (surveys.isEmpty()) {
                        tvEmpty.setVisibility(View.VISIBLE);
                        recyclerView.setVisibility(View.GONE);
                    } else {
                        tvEmpty.setVisibility(View.GONE);
                        recyclerView.setVisibility(View.VISIBLE);
                        adapter.setSurveys(surveys);
                    }
                } else {
                    Toast.makeText(MainActivity.this, 
                        "加载失败: " + response.code(), Toast.LENGTH_LONG).show();
                    tvEmpty.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(Call<List<Survey>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Toast.makeText(MainActivity.this, 
                    "网络错误: " + t.getMessage(), Toast.LENGTH_LONG).show();
                tvEmpty.setVisibility(View.VISIBLE);
            }
        });
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        
        if (id == R.id.action_refresh) {
            loadSurveys();
            return true;
        } else if (id == R.id.action_logout) {
            showLogoutConfirm();
            return true;
        }
        
        return super.onOptionsItemSelected(item);
    }
    
    /**
     * 显示退出登录确认对话框
     */
    private void showLogoutConfirm() {
        new AlertDialog.Builder(this)
            .setTitle("退出登录")
            .setMessage("确定要退出登录吗？")
            .setPositiveButton("确定", (dialog, which) -> {
                sessionManager.clearSession();
                Intent intent = new Intent(MainActivity.this, LoginActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                startActivity(intent);
                Toast.makeText(this, "已退出登录", Toast.LENGTH_SHORT).show();
            })
            .setNegativeButton("取消", null)
            .show();
    }
    
    /**
     * 处理返回键 - 双击退出
     */
    private long exitTime = 0;
    
    @Override
    public void onBackPressed() {
        if ((System.currentTimeMillis() - exitTime) > 2000) {
            Toast.makeText(this, "再按一次退出应用", Toast.LENGTH_SHORT).show();
            exitTime = System.currentTimeMillis();
        } else {
            super.onBackPressed();
        }
    }
}
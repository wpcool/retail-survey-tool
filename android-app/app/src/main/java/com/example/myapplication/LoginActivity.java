package com.example.myapplication;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.myapplication.api.RetrofitClient;
import com.example.myapplication.model.LoginRequest;
import com.example.myapplication.model.LoginResponse;
import com.example.myapplication.utils.SessionManager;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 登录Activity
 */
public class LoginActivity extends AppCompatActivity {

    private EditText etUsername, etPassword;
    private Button btnLogin;
    private ProgressBar progressBar;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 初始化SessionManager
        sessionManager = new SessionManager(this);
        
        // 检查是否已登录
        if (sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, MainActivity.class));
            finish();
            return;
        }
        
        setContentView(R.layout.activity_login);
        
        // 初始化视图
        etUsername = findViewById(R.id.etUsername);
        etPassword = findViewById(R.id.etPassword);
        btnLogin = findViewById(R.id.btnLogin);
        progressBar = findViewById(R.id.progressBar);
        
        // 登录按钮点击事件
        btnLogin.setOnClickListener(v -> attemptLogin());
    }
    
    /**
     * 尝试登录
     */
    private void attemptLogin() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        
        // 输入验证
        if (username.isEmpty()) {
            etUsername.setError("请输入用户名");
            etUsername.requestFocus();
            return;
        }
        
        if (password.isEmpty()) {
            etPassword.setError("请输入密码");
            etPassword.requestFocus();
            return;
        }
        
        if (password.length() < 6) {
            etPassword.setError("密码至少6位");
            etPassword.requestFocus();
            return;
        }
        
        // 显示加载状态
        showLoading(true);
        
        // 调用登录API
        LoginRequest request = new LoginRequest(username, password);
        RetrofitClient.getApi().login(request).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
                showLoading(false);
                
                if (response.isSuccessful() && response.body() != null) {
                    LoginResponse loginResponse = response.body();
                    
                    if (loginResponse.isSuccess()) {
                        // 登录成功，保存用户信息
                        sessionManager.createLoginSession(
                            loginResponse.getUserId(),
                            loginResponse.getName(),
                            username
                        );
                        
                        Toast.makeText(LoginActivity.this, 
                            "欢迎，" + loginResponse.getName(), Toast.LENGTH_SHORT).show();
                        
                        // 跳转到主界面
                        startActivity(new Intent(LoginActivity.this, MainActivity.class));
                        finish();
                    } else {
                        // 登录失败
                        Toast.makeText(LoginActivity.this, 
                            loginResponse.getMessage(), Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(LoginActivity.this, 
                        "登录失败：" + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            
            @Override
            public void onFailure(Call<LoginResponse> call, Throwable t) {
                showLoading(false);
                Toast.makeText(LoginActivity.this, 
                    "网络错误：" + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
    
    private void showLoading(boolean show) {
        btnLogin.setEnabled(!show);
        progressBar.setVisibility(show ? android.view.View.VISIBLE : android.view.View.GONE);
        btnLogin.setText(show ? "登录中..." : "登录");
    }
}
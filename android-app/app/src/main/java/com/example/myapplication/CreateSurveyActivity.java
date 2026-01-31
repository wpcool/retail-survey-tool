package com.example.myapplication;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Location;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.text.SimpleDateFormat;
import java.util.Date;

public class CreateSurveyActivity extends AppCompatActivity {

    private EditText etStoreName, etLocation;
    private Spinner spinnerType;
    private TextView tvPhotoCount;
    private Button btnSubmit;

    private List<Uri> photoUris = new ArrayList<>();
    private Double latitude, longitude;
    private Uri currentPhotoUri;

    private static final int REQUEST_CAMERA = 1;
    private static final int REQUEST_GALLERY = 2;
    private static final int REQUEST_CAMERA_PERMISSION = 100;
    private static final int REQUEST_LOCATION_PERMISSION = 101;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_survey);

        etStoreName = findViewById(R.id.etStoreName);
        etLocation = findViewById(R.id.etLocation);
        spinnerType = findViewById(R.id.spinnerType);
        tvPhotoCount = findViewById(R.id.tvPhotoCount);
        btnSubmit = findViewById(R.id.btnSubmit);

        // 设置调研类型下拉框
        String[] types = {"价格检查", "库存盘点", "货架检查", "促销活动", "竞品调研", "其他"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, types);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerType.setAdapter(adapter);

        // 拍照按钮
        findViewById(R.id.btnTakePhoto).setOnClickListener(v -> {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, 
                        new String[]{Manifest.permission.CAMERA}, REQUEST_CAMERA_PERMISSION);
            } else {
                takePhoto();
            }
        });

        // 选择照片按钮
        findViewById(R.id.btnSelectPhoto).setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.setType("image/*");
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
            startActivityForResult(intent, REQUEST_GALLERY);
        });

        // 提交按钮（简化版，仅显示Toast）
        btnSubmit.setOnClickListener(v -> {
            String storeName = etStoreName.getText().toString().trim();
            if (storeName.isEmpty()) {
                Toast.makeText(this, "请输入门店名称", Toast.LENGTH_SHORT).show();
                return;
            }
            // TODO: 调用后端API创建记录
            Toast.makeText(this, "功能开发中：" + storeName, Toast.LENGTH_SHORT).show();
            finish();
        });

        // 获取位置
        getLocation();
    }

    private void takePhoto() {
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        File photoFile = new File(getCacheDir(), "photo_" + System.currentTimeMillis() + ".jpg");
        currentPhotoUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", photoFile);
        intent.putExtra(MediaStore.EXTRA_OUTPUT, currentPhotoUri);
        startActivityForResult(intent, REQUEST_CAMERA);
    }

    private void getLocation() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) 
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, REQUEST_LOCATION_PERMISSION);
            return;
        }

        FusedLocationProviderClient client = LocationServices.getFusedLocationProviderClient(this);
        client.getLastLocation().addOnSuccessListener(this, location -> {
            if (location != null) {
                latitude = location.getLatitude();
                longitude = location.getLongitude();
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            if (requestCode == REQUEST_CAMERA) {
                photoUris.add(currentPhotoUri);
                updatePhotoCount();
            } else if (requestCode == REQUEST_GALLERY && data != null) {
                if (data.getClipData() != null) {
                    int count = data.getClipData().getItemCount();
                    for (int i = 0; i < count; i++) {
                        photoUris.add(data.getClipData().getItemAt(i).getUri());
                    }
                } else if (data.getData() != null) {
                    photoUris.add(data.getData());
                }
                updatePhotoCount();
            }
        }
    }

    private void updatePhotoCount() {
        tvPhotoCount.setText("已选择 " + photoUris.size() + " 张照片");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA_PERMISSION && grantResults.length > 0 
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            takePhoto();
        } else if (requestCode == REQUEST_LOCATION_PERMISSION && grantResults.length > 0 
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            getLocation();
        }
    }
}

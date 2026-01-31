package com.example.myapplication;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.myapplication.model.Survey;
import java.util.ArrayList;
import java.util.List;

public class SurveyAdapter extends RecyclerView.Adapter<SurveyAdapter.ViewHolder> {

    private List<Survey> surveys = new ArrayList<>();
    private OnItemClickListener listener;

    public interface OnItemClickListener {
        void onItemClick(Survey survey);
    }

    public void setOnItemClickListener(OnItemClickListener listener) {
        this.listener = listener;
    }

    public void setSurveys(List<Survey> surveys) {
        this.surveys = surveys;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_survey, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        Survey survey = surveys.get(position);
        
        // 显示标题（任务标题或门店名称）
        String displayTitle = survey.getTitle() != null ? survey.getTitle() : survey.getStoreName();
        holder.tvStoreName.setText(displayTitle != null ? displayTitle : "未命名");
        
        // 显示状态
        String status = survey.getStatus() != null ? survey.getStatus() : "pending";
        holder.tvSurveyType.setText(getStatusDisplay(status));
        
        // 显示日期
        holder.tvDate.setText(survey.getDate() != null ? survey.getDate() : "");
        
        // 显示描述或地址
        String location = survey.getDescription() != null ? survey.getDescription() : survey.getStoreAddress();
        holder.tvLocation.setText(location != null ? location : "");

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onItemClick(survey);
            }
        });
    }

    @Override
    public int getItemCount() {
        return surveys.size();
    }

    private String getStatusDisplay(String status) {
        if (status == null) return "待处理";
        switch (status) {
            case "pending": return "待处理";
            case "in_progress": return "进行中";
            case "completed": return "已完成";
            default: return status;
        }
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvStoreName, tvSurveyType, tvDate, tvLocation;

        ViewHolder(View itemView) {
            super(itemView);
            tvStoreName = itemView.findViewById(R.id.tvStoreName);
            tvSurveyType = itemView.findViewById(R.id.tvSurveyType);
            tvDate = itemView.findViewById(R.id.tvDate);
            tvLocation = itemView.findViewById(R.id.tvLocation);
        }
    }
}

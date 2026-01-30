"""
API客户端 - 与后端通信
"""
import requests
import json
from config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
    
    def login(self, username, password):
        """用户登录"""
        try:
            response = requests.post(
                f"{self.base_url}/api/login",
                json={"username": username, "password": password},
                timeout=10
            )
            data = response.json()
            if data.get("success"):
                self.token = data.get("token")
            return data
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "无法连接服务器，请检查网络"}
        except Exception as e:
            return {"success": False, "message": f"请求错误: {str(e)}"}
    
    def get_today_task(self, surveyor_id):
        """获取今日任务"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/today/{surveyor_id}",
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_today_records(self, surveyor_id):
        """获取今日已完成的记录"""
        try:
            response = requests.get(
                f"{self.base_url}/api/records/surveyor/{surveyor_id}/today",
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"completed_item_ids": []}
    
    def submit_record(self, data, photo_path=None):
        """提交调研记录"""
        try:
            files = {}
            data_dict = {
                "item_id": data["item_id"],
                "surveyor_id": data["surveyor_id"],
                "store_name": data["store_name"],
                "price": str(data["price"]),
            }
            
            # 可选字段
            for field in ["store_address", "promotion_info", "remark", "latitude", "longitude"]:
                if data.get(field):
                    data_dict[field] = str(data[field])
            
            # 添加照片
            if photo_path:
                files["photo"] = open(photo_path, "rb")
            
            response = requests.post(
                f"{self.base_url}/api/records",
                data=data_dict,
                files=files,
                timeout=30
            )
            
            if photo_path:
                files["photo"].close()
            
            return response.json()
        except Exception as e:
            return {"success": False, "message": str(e)}


# 全局API客户端实例
api = APIClient()

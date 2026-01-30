"""
零售市场调研工具 - 后端服务
FastAPI + SQLite
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import hashlib
from datetime import datetime

from models import get_db, SessionLocal, Surveyor, SurveyTask, SurveyItem, SurveyRecord
from schemas import *

# 创建应用
app = FastAPI(title="零售市场调研API", version="1.0.0")

# 配置CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录（存储照片）
os.makedirs("static/photos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 密码加密盐值
PASSWORD_SALT = "retail_survey_salt_2024"


def get_password_hash(password: str) -> str:
    """使用SHA256+Salt哈希密码"""
    salted = f"{password}{PASSWORD_SALT}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return get_password_hash(plain_password) == hashed_password


# ========== 健康检查 ==========
@app.get("/")
def root():
    return {"message": "零售市场调研API服务运行中", "version": "1.0.0"}


# ========== 登录相关 ==========
@app.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """调研人员登录"""
    user = db.query(Surveyor).filter(Surveyor.username == request.username).first()
    if not user:
        return LoginResponse(success=False, message="用户不存在")
    if not verify_password(request.password, user.password_hash):
        return LoginResponse(success=False, message="密码错误")
    if not user.is_active:
        return LoginResponse(success=False, message="账号已被禁用")
    
    return LoginResponse(
        success=True,
        message="登录成功",
        user_id=user.id,
        name=user.name,
        token=f"token_{user.id}_{int(datetime.now().timestamp())}"
    )


# ========== 调研人员管理 ==========
@app.post("/api/surveyors", response_model=SurveyorResponse)
def create_surveyor(surveyor: SurveyorCreate, db: Session = Depends(get_db)):
    """创建调研人员"""
    db_surveyor = db.query(Surveyor).filter(Surveyor.username == surveyor.username).first()
    if db_surveyor:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_surveyor = Surveyor(
        username=surveyor.username,
        password_hash=get_password_hash(surveyor.password),
        name=surveyor.name,
        phone=surveyor.phone
    )
    db.add(new_surveyor)
    db.commit()
    db.refresh(new_surveyor)
    return new_surveyor


@app.get("/api/surveyors", response_model=List[SurveyorResponse])
def list_surveyors(db: Session = Depends(get_db)):
    """获取所有调研人员"""
    return db.query(Surveyor).all()


# ========== 调研任务管理 ==========
@app.post("/api/tasks", response_model=SurveyTaskResponse)
def create_task(task: SurveyTaskCreate, db: Session = Depends(get_db)):
    """创建调研任务"""
    # 创建任务
    new_task = SurveyTask(
        title=task.title,
        date=task.date,
        description=task.description
    )
    db.add(new_task)
    db.flush()  # 获取task.id
    
    # 创建调研项目
    for item in task.items:
        db_item = SurveyItem(
            task_id=new_task.id,
            category=item.category,
            product_name=item.product_name,
            product_spec=item.product_spec,
            barcode=item.barcode,
            description=item.description,
            sort_order=item.sort_order
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/api/tasks", response_model=List[SurveyTaskSimple])
def list_tasks(date: Optional[str] = None, db: Session = Depends(get_db)):
    """获取任务列表"""
    query = db.query(SurveyTask)
    if date:
        query = query.filter(SurveyTask.date == date)
    query = query.order_by(SurveyTask.date.desc())
    
    tasks = query.all()
    result = []
    for task in tasks:
        result.append(SurveyTaskSimple(
            id=task.id,
            title=task.title,
            date=task.date,
            status=task.status,
            item_count=len(task.items)
        ))
    return result


@app.get("/api/tasks/{task_id}", response_model=SurveyTaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = db.query(SurveyTask).filter(SurveyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@app.get("/api/tasks/today/{surveyor_id}", response_model=SurveyTaskResponse)
def get_today_task(surveyor_id: int, db: Session = Depends(get_db)):
    """获取今日任务（供App使用）"""
    today = datetime.now().strftime("%Y-%m-%d")
    task = db.query(SurveyTask).filter(SurveyTask.date == today).first()
    if not task:
        raise HTTPException(status_code=404, detail="今日没有调研任务")
    return task


# ========== 调研记录相关 ==========
@app.post("/api/records")
def create_record(
    item_id: int = Form(...),
    surveyor_id: int = Form(...),
    store_name: str = Form(...),
    store_address: Optional[str] = Form(None),
    price: float = Form(...),
    promotion_info: Optional[str] = Form(None),
    remark: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """创建调研记录（支持上传照片）"""
    # 保存照片
    photo_path = None
    if photo:
        timestamp = int(datetime.now().timestamp())
        filename = f"{surveyor_id}_{item_id}_{timestamp}.jpg"
        file_path = f"static/photos/{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_path = f"/static/photos/{filename}"
    
    # 创建记录
    record = SurveyRecord(
        item_id=item_id,
        surveyor_id=surveyor_id,
        store_name=store_name,
        store_address=store_address,
        price=price,
        promotion_info=promotion_info,
        remark=remark,
        latitude=latitude,
        longitude=longitude,
        photo_path=photo_path
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {"success": True, "message": "记录保存成功", "record_id": record.id}


@app.get("/api/records", response_model=List[SurveyRecordResponse])
def list_records(
    surveyor_id: Optional[int] = None,
    task_id: Optional[int] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取调研记录"""
    query = db.query(SurveyRecord, SurveyItem, Surveyor).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).join(
        Surveyor, SurveyRecord.surveyor_id == Surveyor.id
    )
    
    if surveyor_id:
        query = query.filter(SurveyRecord.surveyor_id == surveyor_id)
    if task_id:
        query = query.filter(SurveyItem.task_id == task_id)
    if date:
        query = query.filter(SurveyRecord.created_at.contains(date))
    
    results = query.order_by(SurveyRecord.created_at.desc()).all()
    
    records = []
    for record, item, surveyor in results:
        records.append(SurveyRecordResponse(
            id=record.id,
            item_id=record.item_id,
            surveyor_id=record.surveyor_id,
            store_name=record.store_name,
            store_address=record.store_address,
            price=record.price,
            promotion_info=record.promotion_info,
            remark=record.remark,
            latitude=record.latitude,
            longitude=record.longitude,
            photo_path=record.photo_path,
            created_at=record.created_at,
            updated_at=record.updated_at,
            product_name=item.product_name,
            category=item.category,
            surveyor_name=surveyor.name
        ))
    
    return records


@app.get("/api/records/surveyor/{surveyor_id}/today")
def get_surveyor_today_records(surveyor_id: int, db: Session = Depends(get_db)):
    """获取调研人员今日记录（供App使用）"""
    today = datetime.now().strftime("%Y-%m-%d")
    query = db.query(SurveyRecord, SurveyItem).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).filter(
        SurveyRecord.surveyor_id == surveyor_id,
        SurveyRecord.created_at.contains(today)
    )
    
    results = query.all()
    completed_item_ids = [r.SurveyRecord.item_id for r in results]
    
    return {
        "completed_count": len(results),
        "completed_item_ids": completed_item_ids
    }


# ========== 数据统计 ==========
@app.get("/api/statistics/daily")
def get_daily_statistics(date: Optional[str] = None, db: Session = Depends(get_db)):
    """获取每日统计数据"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 当日任务数
    tasks = db.query(SurveyTask).filter(SurveyTask.date == date).all()
    total_tasks = len(tasks)
    total_items = sum(len(t.items) for t in tasks)
    
    # 当日完成记录数
    records = db.query(SurveyRecord).filter(SurveyRecord.created_at.contains(date)).all()
    completed_records = len(records)
    
    completion_rate = 0
    if total_items > 0:
        # 按调研人员统计完成率
        surveyor_ids = db.query(Surveyor.id).filter(Surveyor.is_active == True).count()
        if surveyor_ids > 0:
            expected_total = total_items * surveyor_ids
            completion_rate = round(completed_records / expected_total * 100, 2)
    
    return DailyStatistics(
        date=date,
        total_tasks=total_tasks,
        total_items=total_items,
        completed_records=completed_records,
        completion_rate=completion_rate
    )


# ========== 初始化数据 ==========
@app.on_event("startup")
def init_data():
    """初始化测试数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(Surveyor).first():
            return
        
        print("初始化测试数据...")
        
        # 创建测试用户
        test_user = Surveyor(
            username="test",
            password_hash=get_password_hash("123456"),
            name="测试用户",
            phone="13800138000"
        )
        db.add(test_user)
        
        # 创建示例任务
        today = datetime.now().strftime("%Y-%m-%d")
        task = SurveyTask(
            title=f"{today} 生鲜品类调研",
            date=today,
            description="调研附近超市的生鲜品类价格"
        )
        db.add(task)
        db.flush()
        
        # 创建示例调研项
        sample_items = [
            SurveyItem(task_id=task.id, category="蔬菜", product_name="西红柿", product_spec="500g", sort_order=1),
            SurveyItem(task_id=task.id, category="蔬菜", product_name="黄瓜", product_spec="500g", sort_order=2),
            SurveyItem(task_id=task.id, category="蔬菜", product_name="大白菜", product_spec="每颗", sort_order=3),
            SurveyItem(task_id=task.id, category="肉类", product_name="猪五花肉", product_spec="500g", sort_order=4),
            SurveyItem(task_id=task.id, category="肉类", product_name="鸡胸肉", product_spec="500g", sort_order=5),
            SurveyItem(task_id=task.id, category="水果", product_name="红富士苹果", product_spec="500g", sort_order=6),
            SurveyItem(task_id=task.id, category="水果", product_name="香蕉", product_spec="500g", sort_order=7),
            SurveyItem(task_id=task.id, category="水果", product_name="脐橙", product_spec="500g", sort_order=8),
        ]
        for item in sample_items:
            db.add(item)
        
        db.commit()
        print("测试数据初始化完成")
        print(f"测试账号: test / 123456")
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

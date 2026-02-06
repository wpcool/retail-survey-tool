"""
零售市场调研工具 - 后端服务
FastAPI + SQLite
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import shutil
import os
import hashlib
from datetime import datetime, timedelta

from models import get_db, SessionLocal, Surveyor, SurveyTask, SurveyItem, SurveyRecord, Product
from schemas import *


# ========== 请求模型 ==========
class PasswordResetRequest(BaseModel):
    new_password: str

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
    return {"message": "零售市场调研API服务运行中", "version": "1.0.0", "admin": "/admin"}


# ========== 管理后台 ==========
@app.get("/admin")
def admin_page():
    """重定向到管理后台页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


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


@app.get("/api/surveyors/{surveyor_id}", response_model=SurveyorResponse)
def get_surveyor(surveyor_id: int, db: Session = Depends(get_db)):
    """获取调研人员详情"""
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(status_code=404, detail="人员不存在")
    return surveyor


@app.put("/api/surveyors/{surveyor_id}", response_model=SurveyorResponse)
def update_surveyor(surveyor_id: int, surveyor_update: SurveyorUpdate, db: Session = Depends(get_db)):
    """更新调研人员信息"""
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    if surveyor_update.name is not None:
        surveyor.name = surveyor_update.name
    if surveyor_update.phone is not None:
        surveyor.phone = surveyor_update.phone
    if surveyor_update.is_active is not None:
        surveyor.is_active = surveyor_update.is_active
    
    db.commit()
    db.refresh(surveyor)
    return surveyor


@app.post("/api/surveyors/{surveyor_id}/reset-password")
def reset_surveyor_password(surveyor_id: int, request: PasswordResetRequest, db: Session = Depends(get_db)):
    """重置调研人员密码"""
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    surveyor.password_hash = get_password_hash(request.new_password)
    db.commit()
    return {"success": True, "message": "密码重置成功"}


@app.delete("/api/surveyors/{surveyor_id}")
def delete_surveyor(surveyor_id: int, db: Session = Depends(get_db)):
    """删除调研人员"""
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    db.delete(surveyor)
    db.commit()
    return {"success": True, "message": "删除成功"}


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
        # 构建商品列表
        items = []
        for item in task.items:
            items.append(SurveyItemResponse(
                id=item.id,
                task_id=item.task_id,
                category=item.category,
                product_name=item.product_name,
                product_spec=item.product_spec,
                barcode=item.barcode,
                description=item.description,
                sort_order=item.sort_order
            ))
        
        result.append(SurveyTaskSimple(
            id=task.id,
            title=task.title,
            date=task.date,
            status=task.status,
            description=task.description,
            item_count=len(task.items),
            items=items,
            created_at=task.created_at
        ))
    return result


@app.get("/api/tasks/{task_id}", response_model=SurveyTaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = db.query(SurveyTask).filter(SurveyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@app.put("/api/tasks/{task_id}", response_model=SurveyTaskResponse)
def update_task(task_id: int, task_update: SurveyTaskUpdate, db: Session = Depends(get_db)):
    """更新调研任务"""
    task = db.query(SurveyTask).filter(SurveyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.date is not None:
        task.date = task_update.date
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    
    db.commit()
    db.refresh(task)
    return task


@app.post("/api/tasks/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """作废调研任务"""
    task = db.query(SurveyTask).filter(SurveyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task.status = "cancelled"
    db.commit()
    return {"success": True, "message": "作废成功"}


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除调研任务（物理删除）"""
    task = db.query(SurveyTask).filter(SurveyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    return {"success": True, "message": "删除成功"}


@app.get("/api/tasks/today/{surveyor_id}")
def get_today_task(surveyor_id: int, db: Session = Depends(get_db)):
    """获取今日任务（供App使用）"""
    today = datetime.now().strftime("%Y-%m-%d")
    task = db.query(SurveyTask).filter(SurveyTask.date == today).first()
    if not task:
        raise HTTPException(status_code=404, detail="今日没有调研任务")
    
    # 检查任务是否已作废
    if task.status == "cancelled":
        return {
            "id": task.id,
            "title": task.title,
            "date": task.date,
            "status": "cancelled",
            "cancelled": True,
            "message": "该任务已作废",
            "items": []
        }
    
    return task


# ========== 调研记录相关 ==========
class RecordCreateRequest(BaseModel):
    """创建调研记录请求（JSON格式）"""
    item_id: int
    surveyor_id: int
    store_name: str
    store_address: Optional[str] = None
    price: float
    promotion_info: Optional[str] = None
    remark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[str]] = None  # 照片URL列表


@app.post("/api/records")
def create_record(
    request: RecordCreateRequest,
    db: Session = Depends(get_db)
):
    """创建调研记录（JSON格式，供小程序使用）"""
    import json
    
    # 处理照片数据
    photos_json = None
    if request.photos and len(request.photos) > 0:
        photos_json = json.dumps(request.photos, ensure_ascii=False)
    
    # 创建记录
    record = SurveyRecord(
        item_id=request.item_id,
        surveyor_id=request.surveyor_id,
        store_name=request.store_name,
        store_address=request.store_address,
        price=request.price,
        promotion_info=request.promotion_info,
        remark=request.remark,
        latitude=request.latitude,
        longitude=request.longitude,
        photo_path=request.photos[0] if request.photos and len(request.photos) > 0 else None,
        photos=photos_json
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {"success": True, "message": "记录保存成功", "record_id": record.id}


@app.post("/api/records/upload")
def create_record_with_photo(
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
    """创建调研记录（支持上传照片，Form格式）"""
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


@app.post("/api/upload")
def upload_file(
    file: UploadFile = File(...),
    type: str = Form("image")
):
    """通用文件上传接口"""
    # 验证文件类型
    if type == "image":
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.content_type}")
    
    # 生成文件名
    timestamp = int(datetime.now().timestamp())
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{type}_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}.{file_ext}"
    
    # 确保目录存在
    upload_dir = f"static/photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = f"{upload_dir}/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回文件访问URL
    file_url = f"/static/photos/{filename}"
    
    return {
        "success": True,
        "url": file_url,
        "filename": filename,
        "type": type
    }


@app.get("/api/records", response_model=List[SurveyRecordResponse])
def list_records(
    surveyor_id: Optional[int] = None,
    task_id: Optional[int] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取调研记录"""
    query = db.query(SurveyRecord, SurveyItem, Surveyor, Product).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).join(
        Surveyor, SurveyRecord.surveyor_id == Surveyor.id
    ).outerjoin(
        Product, SurveyItem.product_name == Product.name
    )
    
    if surveyor_id:
        query = query.filter(SurveyRecord.surveyor_id == surveyor_id)
    if task_id:
        query = query.filter(SurveyItem.task_id == task_id)
    if date:
        query = query.filter(SurveyRecord.created_at.contains(date))
    
    results = query.order_by(SurveyRecord.created_at.desc()).all()
    
    records = []
    for record, item, surveyor, product in results:
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
            surveyor_name=surveyor.name,
            category_level1_name=product.category_level1_name if product else None,
            category_level2_name=product.category_level2_name if product else None,
            category_level3_name=product.category_level3_name if product else None,
            category_level4_name=product.category_level4_name if product else None
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


@app.get("/api/tasks/{task_id}/completion/{surveyor_id}")
def get_task_completion_status(task_id: int, surveyor_id: int, db: Session = Depends(get_db)):
    """获取某任务下当前用户每个商品的调研次数"""
    from sqlalchemy import func
    
    # 查询该任务下的所有商品项
    task_items = db.query(SurveyItem).filter(SurveyItem.task_id == task_id).all()
    item_ids = [item.id for item in task_items]
    
    # 查询每个商品的调研次数
    record_counts = db.query(
        SurveyRecord.item_id,
        func.count(SurveyRecord.id).label('count')
    ).filter(
        SurveyRecord.surveyor_id == surveyor_id,
        SurveyRecord.item_id.in_(item_ids)
    ).group_by(SurveyRecord.item_id).all()
    
    # 构建商品调研次数字典
    item_count_map = {item_id: count for item_id, count in record_counts}
    
    # 构建详细列表
    items_detail = []
    for item in task_items:
        count = item_count_map.get(item.id, 0)
        items_detail.append({
            "item_id": item.id,
            "category": item.category,
            "product_name": item.product_name,
            "count": count,
            "completed": count > 0
        })
    
    # 统计信息
    completed_items = sum(1 for i in items_detail if i['count'] > 0)
    total_records = sum(i['count'] for i in items_detail)
    
    return {
        "task_id": task_id,
        "surveyor_id": surveyor_id,
        "total_items": len(item_ids),
        "completed_items": completed_items,
        "total_records": total_records,
        "items": items_detail
    }


@app.get("/api/surveyors/{surveyor_id}/stats")
def get_surveyor_stats(surveyor_id: int, db: Session = Depends(get_db)):
    """获取调研人员个人统计"""
    from sqlalchemy import func, distinct
    
    # 基础统计
    total_records = db.query(SurveyRecord).filter(
        SurveyRecord.surveyor_id == surveyor_id
    ).count()
    
    # 今日统计
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = db.query(SurveyRecord).filter(
        SurveyRecord.surveyor_id == surveyor_id,
        SurveyRecord.created_at.contains(today)
    ).count()
    
    # 调研天数（有记录的不同日期数）
    distinct_days = db.query(func.count(func.distinct(
        func.strftime('%Y-%m-%d', SurveyRecord.created_at)
    ))).filter(
        SurveyRecord.surveyor_id == surveyor_id
    ).scalar()
    
    # 调研过的不同商品数
    distinct_products = db.query(func.count(distinct(SurveyRecord.item_id))).filter(
        SurveyRecord.surveyor_id == surveyor_id
    ).scalar()
    
    # 最近7天的调研记录
    last_7_days = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        count = db.query(SurveyRecord).filter(
            SurveyRecord.surveyor_id == surveyor_id,
            SurveyRecord.created_at.contains(date)
        ).count()
        if count > 0:
            last_7_days.append({"date": date, "count": count})
    
    # 最近10条详细记录
    recent_records = db.query(SurveyRecord, SurveyItem).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).filter(
        SurveyRecord.surveyor_id == surveyor_id
    ).order_by(SurveyRecord.created_at.desc()).limit(10).all()
    
    recent_list = []
    for record, item in recent_records:
        recent_list.append({
            "id": record.id,
            "product_name": item.product_name,
            "category": item.category,
            "store_name": record.store_name,
            "price": record.price,
            "date": record.created_at.strftime("%Y-%m-%d"),
            "time": record.created_at.strftime("%H:%M")
        })
    
    return {
        "total_records": total_records,
        "today_records": today_records,
        "distinct_days": distinct_days or 0,
        "distinct_products": distinct_products or 0,
        "last_7_days": last_7_days,
        "recent_records": recent_list
    }


@app.get("/api/records/{record_id}", response_model=SurveyRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条记录详情"""
    result = db.query(SurveyRecord, SurveyItem, Surveyor).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).join(
        Surveyor, SurveyRecord.surveyor_id == Surveyor.id
    ).filter(SurveyRecord.id == record_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    record, item, surveyor = result
    return SurveyRecordResponse(
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
    )


class RecordUpdateRequest(BaseModel):
    """更新调研记录请求"""
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    price: Optional[float] = None
    promotion_info: Optional[str] = None
    remark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@app.put("/api/records/{record_id}")
def update_record(
    record_id: int,
    request: RecordUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新调研记录"""
    record = db.query(SurveyRecord).filter(SurveyRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 更新字段
    if request.store_name is not None:
        record.store_name = request.store_name
    if request.store_address is not None:
        record.store_address = request.store_address
    if request.price is not None:
        record.price = request.price
    if request.promotion_info is not None:
        record.promotion_info = request.promotion_info
    if request.remark is not None:
        record.remark = request.remark
    if request.latitude is not None:
        record.latitude = request.latitude
    if request.longitude is not None:
        record.longitude = request.longitude
    
    db.commit()
    db.refresh(record)
    
    return {"success": True, "message": "更新成功"}


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


# ========== 调研人员当日明细 ==========
@app.get("/api/surveyors/{surveyor_id}/today-details")
def get_surveyor_today_details(surveyor_id: int, date: Optional[str] = None, db: Session = Depends(get_db)):
    """获取调研人员当日调研明细（商品+超市）"""
    from sqlalchemy import func
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 查询当日该人员的所有调研记录
    records = db.query(
        SurveyRecord.store_name,
        SurveyItem.product_name,
        SurveyItem.category,
        SurveyRecord.price,
        SurveyRecord.created_at
    ).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).filter(
        SurveyRecord.surveyor_id == surveyor_id,
        func.date(SurveyRecord.created_at) == date
    ).order_by(SurveyRecord.created_at.desc()).all()
    
    result = []
    for store_name, product_name, category, price, created_at in records:
        result.append({
            "store_name": store_name,
            "product_name": product_name,
            "category": category,
            "price": price,
            "time": created_at.strftime("%H:%M") if created_at else ""
        })
    
    return result


# ========== 今日调研人员排行 ==========
@app.get("/api/statistics/surveyor-ranking")
def get_surveyor_ranking(date: Optional[str] = None, db: Session = Depends(get_db)):
    """获取今日调研人员排行（完成数量、超市数量、完成率）"""
    from sqlalchemy import func
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 获取今日任务品类总数
    task_items_count = db.query(SurveyItem).join(SurveyTask).filter(
        SurveyTask.date == date
    ).count()
    
    # 获取每个调研人员今日的提交记录数和超市数量
    ranking = db.query(
        Surveyor.id,
        Surveyor.name,
        func.count(SurveyRecord.id).label('record_count'),
        func.count(func.distinct(SurveyRecord.store_name)).label('store_count')
    ).join(
        SurveyRecord, Surveyor.id == SurveyRecord.surveyor_id
    ).filter(
        func.date(SurveyRecord.created_at) == date
    ).group_by(
        Surveyor.id, Surveyor.name
    ).order_by(func.count(SurveyRecord.id).desc()).all()
    
    result = []
    for surveyor_id, name, record_count, store_count in ranking:
        # 计算完成率
        completion_rate = 0
        if task_items_count > 0:
            completion_rate = round(record_count / task_items_count * 100, 1)
        
        result.append({
            "id": surveyor_id,
            "name": name,
            "count": record_count,
            "store_count": store_count,
            "completion_rate": completion_rate
        })
    
    return result


# ========== 品类分布数据（按一级分类细分二级分类） ==========
@app.get("/api/statistics/category-distribution")
def get_category_distribution(days: int = 7, db: Session = Depends(get_db)):
    """获取食品杂货和生鲜的二级分类分布数据"""
    from sqlalchemy import func
    
    # 计算日期范围
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 查询食品杂货的二级分类分布
    grocery_data = db.query(
        Product.category_level2_name.label('subcategory'),
        func.count(SurveyRecord.id).label('count')
    ).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).join(
        Product, SurveyItem.product_name == Product.name
    ).filter(
        Product.category_level1_name == '食品杂货',
        func.date(SurveyRecord.created_at) >= start_date
    ).group_by(
        Product.category_level2_name
    ).order_by(func.count(SurveyRecord.id).desc()).all()
    
    # 查询生鲜的二级分类分布
    fresh_data = db.query(
        Product.category_level2_name.label('subcategory'),
        func.count(SurveyRecord.id).label('count')
    ).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    ).join(
        Product, SurveyItem.product_name == Product.name
    ).filter(
        Product.category_level1_name == '生鲜',
        func.date(SurveyRecord.created_at) >= start_date
    ).group_by(
        Product.category_level2_name
    ).order_by(func.count(SurveyRecord.id).desc()).all()
    
    return {
        "grocery": [{"name": item.subcategory or '其他', "count": item.count} for item in grocery_data],
        "fresh": [{"name": item.subcategory or '其他', "count": item.count} for item in fresh_data]
    }


# ========== 7天趋势数据 ==========
@app.get("/api/statistics/trend")
def get_trend_data(days: int = 7, db: Session = Depends(get_db)):
    """获取近N天调研趋势数据（记录数 + 完成率）"""
    from sqlalchemy import func
    
    # 获取活跃调研人员数
    active_surveyors = db.query(Surveyor).filter(Surveyor.is_active == True).count()
    
    result = []
    for i in range(days - 1, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # 当日记录数
        record_count = db.query(SurveyRecord).filter(
            func.date(SurveyRecord.created_at) == date
        ).count()
        
        # 当日任务品类总数
        task_items = db.query(SurveyItem).join(SurveyTask).filter(
            SurveyTask.date == date
        ).count()
        
        # 完成率
        completion_rate = 0
        if task_items > 0 and active_surveyors > 0:
            expected = task_items * active_surveyors
            completion_rate = round(record_count / expected * 100, 1)
        
        result.append({
            "date": date,
            "record_count": record_count,
            "completion_rate": completion_rate
        })
    
    return result


# ========== 统计报表接口 ==========
@app.get("/api/statistics/monthly-trend")
def get_monthly_trend(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    """获取月度调研趋势（按天统计）"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # 获取该月天数
    import calendar
    _, days_in_month = calendar.monthrange(year, month)
    
    result = []
    for day in range(1, days_in_month + 1):
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 统计当天的调研记录数
        record_count = db.query(func.count(SurveyRecord.id)).filter(
            func.date(SurveyRecord.created_at) == date_obj
        ).scalar() or 0
        
        result.append({
            "day": day,
            "date": date_str,
            "record_count": record_count
        })
    
    return result


@app.get("/api/statistics/surveyor-stats")
def get_surveyor_stats(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    """获取人员调研统计（按月）"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # 计算月份起始和结束日期
    import calendar
    start_date = datetime(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    end_date = datetime(year, month, days_in_month, 23, 59, 59)
    
    # 按调研人员统计记录数
    stats = db.query(
        Surveyor.name,
        func.count(SurveyRecord.id).label("record_count")
    ).join(
        SurveyRecord, Surveyor.id == SurveyRecord.surveyor_id
    ).filter(
        SurveyRecord.created_at >= start_date,
        SurveyRecord.created_at <= end_date
    ).group_by(
        Surveyor.id,
        Surveyor.name
    ).order_by(
        func.count(SurveyRecord.id).desc()
    ).all()
    
    result = [{"name": s.name, "record_count": s.record_count} for s in stats]
    
    # 如果超过5人，合并剩余为"其他"
    if len(result) > 5:
        top5 = result[:5]
        others_count = sum(r["record_count"] for r in result[5:])
        top5.append({"name": "其他", "record_count": others_count})
        result = top5
    
    return result


# ========== 调研记录删除 ==========
@app.delete("/api/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """删除调研记录"""
    record = db.query(SurveyRecord).filter(SurveyRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 删除照片文件
    if record.photo_path:
        photo_file = record.photo_path.replace("/static/", "static/")
        if os.path.exists(photo_file):
            os.remove(photo_file)
    
    db.delete(record)
    db.commit()
    return {"success": True, "message": "删除成功"}


# ========== 商品库管理 ==========
@app.get("/api/products", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    level1: Optional[str] = None,
    level2: Optional[str] = None,
    level3: Optional[str] = None,
    level4: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取商品列表，支持搜索和四级分类筛选"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        # 支持任意一级分类搜索
        query = query.filter(
            (Product.category_level1_name == category) |
            (Product.category_level2_name == category) |
            (Product.category_level3_name == category) |
            (Product.category_level4_name == category)
        )
    # 四级分类筛选
    if level1:
        query = query.filter(Product.category_level1_name == level1)
    if level2:
        query = query.filter(Product.category_level2_name == level2)
    if level3:
        query = query.filter(Product.category_level3_name == level3)
    if level4:
        query = query.filter(Product.category_level4_name == level4)
    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) | 
            (Product.barcode.contains(keyword))
        )
    
    products = query.order_by(Product.category_level1_name, Product.category_level2_name, 
                              Product.category_level3_name, Product.category_level4_name, 
                              Product.name).offset(skip).limit(limit).all()
    return products


@app.get("/api/products/categories")
def list_categories(level: int = 1, parent: Optional[str] = None, db: Session = Depends(get_db)):
    """获取品类列表，支持按层级和父分类筛选
    
    Args:
        level: 分类层级 (1-4)
        parent: 父分类名称（用于获取子分类）
    """
    level = max(1, min(4, level))
    
    if level == 1:
        field = Product.category_level1_name
        query = db.query(field)
    elif level == 2:
        field = Product.category_level2_name
        query = db.query(field)
        if parent:
            query = query.filter(Product.category_level1_name == parent)
    elif level == 3:
        field = Product.category_level3_name
        query = db.query(field)
        if parent:
            query = query.filter(Product.category_level2_name == parent)
    else:  # level == 4
        field = Product.category_level4_name
        query = db.query(field)
        if parent:
            query = query.filter(Product.category_level3_name == parent)
    
    categories = query.filter(
        Product.is_active == True,
        field.isnot(None),
        field != ""
    ).distinct().all()
    
    return [c[0] for c in categories if c[0]]


@app.get("/api/products/suggest")
def suggest_products(
    keyword: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """根据关键词自动补全商品"""
    if not keyword or len(keyword) < 1:
        return []
    
    products = db.query(Product).filter(
        Product.is_active == True,
        (Product.name.contains(keyword)) | 
        (Product.barcode.contains(keyword)) |
        (Product.category_level4_name.contains(keyword))
    ).limit(limit).all()
    
    return [{
        "id": p.id,
        "category_level1_name": p.category_level1_name,
        "category_level2_name": p.category_level2_name,
        "category_level3_name": p.category_level3_name,
        "category_level4_name": p.category_level4_name,
        "name": p.name,
        "spec": p.spec,
        "barcode": p.barcode,
        "brand_name": p.brand_name
    } for p in products]


@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """创建商品"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.post("/api/products/batch")
def batch_create_products(products: List[ProductCreate], db: Session = Depends(get_db)):
    """批量创建商品"""
    db_products = [Product(**p.model_dump()) for p in products]
    db.add_all(db_products)
    db.commit()
    return {"success": True, "imported": len(db_products)}


@app.post("/api/products/import")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从Excel导入商品 - 支持标准格式和商品数据.xlsx格式"""
    import pandas as pd
    import io
    import re
    
    # 读取Excel文件
    contents = await file.read()
    
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        return {
            "success": False,
            "message": f"Excel文件解析失败: {str(e)}",
            "total": 0,
            "imported": 0,
            "errors": []
        }
    
    # 列名映射（支持所有25个字段）
    column_mapping = {
        # === 四级分类 ===
        '一级分类编码': 'category_level1_code',
        '一级分类': 'category_level1_name',
        '一级类目': 'category_level1_name',
        '商品分类名称1': 'category_level1_name',
        '二级分类编码': 'category_level2_code',
        '二级分类': 'category_level2_name',
        '二级类目': 'category_level2_name',
        '商品分类名称2': 'category_level2_name',
        '三级分类编码': 'category_level3_code',
        '三级分类': 'category_level3_name',
        '三级类目': 'category_level3_name',
        '商品分类名称3': 'category_level3_name',
        '四级分类编码': 'category_level4_code',
        '四级分类': 'category_level4_name',
        '四级类目': 'category_level4_name',
        '商品分类名称4': 'category_level4_name',
        '小类': 'category_level4_name',
        '品类': 'category_level4_name',
        
        # === 商品基础信息 ===
        '商品编码': 'product_code',
        '商品名称': 'name',
        'name': 'name',
        '商品名': 'name',
        '条码': 'barcode',
        '商品条码': 'barcode',
        'barcode': 'barcode',
        '规格': 'spec',
        'spec': 'spec',
        '规格型号': 'spec',
        '单位': 'unit',
        '计量单位': 'unit',
        '基本计量单位': 'unit',
        
        # === 品牌产地 ===
        '品牌编码': 'brand_code',
        '品牌': 'brand_name',
        'brand': 'brand_name',
        'brand_name': 'brand_name',
        '产地': 'origin',
        
        # === 价格信息 ===
        '进价': 'purchase_price',
        '参考进价': 'purchase_price',
        'purchase_price': 'purchase_price',
        '售价': 'sale_price',
        '参考售价': 'sale_price',
        'sale_price': 'sale_price',
        
        # === 供应商 ===
        '供应商编码': 'supplier_code',
        '供应商': 'supplier_name',
        'supplier_name': 'supplier_name',
        
        # === 状态 ===
        '经营状态': 'status',
        'status': 'status',
    }
    
    # 重命名列
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # 检查必需列
    if 'name' not in df.columns:
        return {
            "success": False,
            "message": "Excel缺少必需列：商品名称",
            "total": 0,
            "imported": 0,
            "errors": []
        }
    
    # 辅助函数：从商品名称中提取规格
    def extract_spec(name):
        # 匹配模式: 5kg, 1L, 280g, 15g, 2.45L, 100ml 等
        matches = re.findall(r'(\d+\.?\d*)([kgmlL升克gML]{1,3})', name)
        if matches:
            # 取最后一个匹配（通常是规格）
            return ''.join(matches[-1])
        return None
    
    # 导入数据
    imported = 0
    updated = 0
    errors = []
    
    def get_str_value(row, col_name):
        """获取字符串值，处理NaN"""
        if col_name in df.columns and pd.notna(row.get(col_name)):
            return str(row.get(col_name)).strip()
        return None
    
    def get_float_value(row, col_name):
        """获取浮点数值，处理NaN和各种格式"""
        if col_name in df.columns and pd.notna(row.get(col_name)):
            try:
                val = row.get(col_name)
                if isinstance(val, (int, float)):
                    return float(val)
                # 处理字符串，移除货币符号和逗号
                val_str = str(val).replace('¥', '').replace(',', '').replace('，', '').strip()
                return float(val_str)
            except:
                return None
        return None
    
    for idx, row in df.iterrows():
        try:
            name = get_str_value(row, 'name')
            if not name:
                errors.append(f"第{idx+2}行: 商品名称为空")
                continue
            
            # === 获取所有字段 ===
            # 四级分类编码和名称
            cat1_code = get_str_value(row, 'category_level1_code')
            cat1_name = get_str_value(row, 'category_level1_name')
            cat2_code = get_str_value(row, 'category_level2_code')
            cat2_name = get_str_value(row, 'category_level2_name')
            cat3_code = get_str_value(row, 'category_level3_code')
            cat3_name = get_str_value(row, 'category_level3_name')
            cat4_code = get_str_value(row, 'category_level4_code')
            cat4_name = get_str_value(row, 'category_level4_name')
            
            # 如果没有四级分类名称，尝试用三级或默认值
            if not cat4_name:
                cat4_name = cat3_name or '未分类'
            
            # 商品基础信息
            product_code = get_str_value(row, 'product_code')
            barcode = get_str_value(row, 'barcode')
            spec = get_str_value(row, 'spec')
            if not spec:
                spec = extract_spec(name)
            unit = get_str_value(row, 'unit')
            
            # 品牌产地
            brand_code = get_str_value(row, 'brand_code')
            brand_name = get_str_value(row, 'brand_name')
            origin = get_str_value(row, 'origin')
            
            # 价格信息
            purchase_price = get_float_value(row, 'purchase_price')
            sale_price = get_float_value(row, 'sale_price')
            
            # 供应商
            supplier_code = get_str_value(row, 'supplier_code')
            supplier_name = get_str_value(row, 'supplier_name')
            
            # 状态
            status = get_str_value(row, 'status') or '正常'
            
            # 检查是否已存在（按条码 > 商品编码 > 名称+四级分类）
            existing = None
            if barcode:
                existing = db.query(Product).filter(Product.barcode == barcode).first()
            if not existing and product_code:
                existing = db.query(Product).filter(Product.product_code == product_code).first()
            if not existing:
                existing = db.query(Product).filter(
                    Product.category_level4_name == cat4_name,
                    Product.name == name
                ).first()
            
            if existing:
                # === 更新已有商品（所有字段）===
                if cat1_code: existing.category_level1_code = cat1_code
                if cat1_name: existing.category_level1_name = cat1_name
                if cat2_code: existing.category_level2_code = cat2_code
                if cat2_name: existing.category_level2_name = cat2_name
                if cat3_code: existing.category_level3_code = cat3_code
                if cat3_name: existing.category_level3_name = cat3_name
                if cat4_code: existing.category_level4_code = cat4_code
                if cat4_name: existing.category_level4_name = cat4_name
                
                if product_code: existing.product_code = product_code
                if barcode: existing.barcode = barcode
                if spec: existing.spec = spec
                if unit: existing.unit = unit
                
                if brand_code: existing.brand_code = brand_code
                if brand_name: existing.brand_name = brand_name
                if origin: existing.origin = origin
                
                if purchase_price is not None: existing.purchase_price = purchase_price
                if sale_price is not None: existing.sale_price = sale_price
                
                if supplier_code: existing.supplier_code = supplier_code
                if supplier_name: existing.supplier_name = supplier_name
                if status: existing.status = status
                
                existing.is_active = True
                updated += 1
            else:
                # === 创建新商品（所有字段）===
                product = Product(
                    category_level1_code=cat1_code,
                    category_level1_name=cat1_name,
                    category_level2_code=cat2_code,
                    category_level2_name=cat2_name,
                    category_level3_code=cat3_code,
                    category_level3_name=cat3_name,
                    category_level4_code=cat4_code,
                    category_level4_name=cat4_name,
                    product_code=product_code,
                    name=name,
                    barcode=barcode,
                    spec=spec,
                    unit=unit,
                    brand_code=brand_code,
                    brand_name=brand_name,
                    origin=origin,
                    purchase_price=purchase_price,
                    sale_price=sale_price,
                    supplier_code=supplier_code,
                    supplier_name=supplier_name,
                    status=status,
                    is_active=True
                )
                db.add(product)
                imported += 1
            
        except Exception as e:
            errors.append(f"第{idx+2}行: {str(e)}")
    
    db.commit()
    
    return {
        "success": True,
        "message": f"导入完成：新增 {imported} 条，更新 {updated} 条",
        "total": len(df),
        "imported": imported,
        "updated": updated,
        "errors": errors[:10]
    }


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """更新商品信息"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    for field, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除商品（软删除）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    product.is_active = False
    db.commit()
    return {"success": True, "message": "删除成功"}


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

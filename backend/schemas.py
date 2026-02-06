"""
数据验证模型（Pydantic）
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ========== 调研人员相关 ==========
class SurveyorBase(BaseModel):
    username: str
    name: str
    phone: Optional[str] = None


class SurveyorCreate(SurveyorBase):
    password: str


class SurveyorResponse(SurveyorBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SurveyorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


# ========== 调研任务相关 ==========
class SurveyItemBase(BaseModel):
    category: str
    product_name: str
    product_spec: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class SurveyItemCreate(SurveyItemBase):
    pass


class SurveyItemResponse(SurveyItemBase):
    id: int
    task_id: int
    
    class Config:
        from_attributes = True


class SurveyTaskBase(BaseModel):
    title: str
    date: str
    description: Optional[str] = None


class SurveyTaskCreate(SurveyTaskBase):
    items: List[SurveyItemCreate]


class SurveyTaskResponse(SurveyTaskBase):
    id: int
    status: str
    created_at: datetime
    items: List[SurveyItemResponse]
    
    class Config:
        from_attributes = True


class SurveyTaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SurveyTaskSimple(BaseModel):
    """简化版任务（用于列表）"""
    id: int
    title: str
    date: str
    status: str
    description: Optional[str] = None
    item_count: int
    items: List[SurveyItemResponse] = []  # 添加商品列表
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 调研记录相关 ==========
class SurveyRecordBase(BaseModel):
    item_id: int
    store_name: str
    store_address: Optional[str] = None
    price: float
    promotion_info: Optional[str] = None
    remark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SurveyRecordCreate(SurveyRecordBase):
    pass


class SurveyRecordResponse(SurveyRecordBase):
    id: int
    surveyor_id: int
    photo_path: Optional[str] = None  # 兼容旧数据，第一张图片
    photos: Optional[List[str]] = None  # 多张照片URL列表
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    product_name: Optional[str] = None
    category: Optional[str] = None
    surveyor_name: Optional[str] = None
    
    # 四级分类信息
    category_level1_name: Optional[str] = None
    category_level2_name: Optional[str] = None
    category_level3_name: Optional[str] = None
    category_level4_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== 登录相关 ==========
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    name: Optional[str] = None
    token: Optional[str] = None


# ========== 统计相关 ==========
class DailyStatistics(BaseModel):
    date: str
    total_tasks: int
    total_items: int
    completed_records: int
    completion_rate: float


# ========== 商品库相关 ==========
class ProductBase(BaseModel):
    # 四级分类体系
    category_level1_code: Optional[int] = None
    category_level1_name: Optional[str] = None
    category_level2_code: Optional[int] = None
    category_level2_name: Optional[str] = None
    category_level3_code: Optional[int] = None
    category_level3_name: Optional[str] = None
    category_level4_code: Optional[int] = None
    category_level4_name: Optional[str] = None
    # 商品基本信息
    product_code: Optional[str] = None
    name: str
    barcode: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    # 品牌产地
    brand_code: Optional[str] = None
    brand_name: Optional[str] = None
    origin: Optional[str] = None
    # 价格信息
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    # 供应商
    supplier_code: Optional[str] = None
    supplier_name: Optional[str] = None
    # 状态
    status: Optional[str] = "正常"
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    category_level4_name: Optional[str] = None
    name: Optional[str] = None
    spec: Optional[str] = None
    barcode: Optional[str] = None
    brand_name: Optional[str] = None
    is_active: Optional[bool] = None


class ProductImportResult(BaseModel):
    success: bool
    message: str
    total: int
    imported: int
    errors: List[str] = []

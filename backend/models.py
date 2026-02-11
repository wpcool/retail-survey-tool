"""
数据模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 创建数据库目录
os.makedirs("data", exist_ok=True)

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///data/survey.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Surveyor(Base):
    """调研人员"""
    __tablename__ = "surveyors"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    name = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    surveys = relationship("SurveyRecord", back_populates="surveyor")


class SurveyTask(Base):
    """调研任务（每天发布）"""
    __tablename__ = "survey_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))  # 任务标题，如：2024-01-30 生鲜品类调研
    date = Column(String(10), index=True)  # 调研日期 YYYY-MM-DD
    description = Column(Text)  # 任务说明
    status = Column(String(20), default="active")  # active, completed
    created_at = Column(DateTime, default=datetime.now)
    
    items = relationship("SurveyItem", back_populates="task", cascade="all, delete-orphan")


class SurveyItem(Base):
    """调研项目（品类）"""
    __tablename__ = "survey_items"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("survey_tasks.id"))
    category = Column(String(100))  # 大类：生鲜、粮油、日用...
    product_name = Column(String(200))  # 商品名称
    product_spec = Column(String(100))  # 规格：500g/瓶
    barcode = Column(String(50), nullable=True)  # 条码（可选）
    description = Column(Text, nullable=True)  # 调研说明
    sort_order = Column(Integer, default=0)  # 排序
    
    task = relationship("SurveyTask", back_populates="items")
    records = relationship("SurveyRecord", back_populates="item")


class SurveyRecord(Base):
    """调研记录（调研人员填写的数据）"""
    __tablename__ = "survey_records"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("survey_items.id"))
    surveyor_id = Column(Integer, ForeignKey("surveyors.id"))
    own_store_name = Column(String(100), nullable=True)  # 自己的门店名称（如：蔡家坡店）
    store_name = Column(String(200))  # 竞争店铺名称（如：超美佳）
    store_address = Column(String(500), nullable=True)  # 地址
    price = Column(Float)  # 单价
    promotion_info = Column(String(500), nullable=True)  # 促销信息
    photo_path = Column(String(500), nullable=True)  # 照片路径（单张，兼容旧数据）
    photos = Column(Text, nullable=True)  # 多张照片路径，JSON格式存储
    remark = Column(Text, nullable=True)  # 备注
    latitude = Column(Float, nullable=True)  # 纬度
    longitude = Column(Float, nullable=True)  # 经度
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    item = relationship("SurveyItem", back_populates="records")
    surveyor = relationship("Surveyor", back_populates="surveys")


class Product(Base):
    """商品库（用于自动补全）"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 分类信息（四级分类）
    category_level1_code = Column(String(20), nullable=True)  # 一级分类编码
    category_level1_name = Column(String(100), nullable=True)  # 一级分类名称
    category_level2_code = Column(String(20), nullable=True)  # 二级分类编码
    category_level2_name = Column(String(100), nullable=True)  # 二级分类名称
    category_level3_code = Column(String(20), nullable=True)  # 三级分类编码
    category_level3_name = Column(String(100), nullable=True)  # 三级分类名称
    category_level4_code = Column(String(20), nullable=True, index=True)  # 四级分类编码
    category_level4_name = Column(String(100), nullable=True, index=True)  # 四级分类名称（商品小类）
    
    # 商品基本信息
    product_code = Column(String(50), nullable=True, index=True)  # 商品编码
    name = Column(String(200), index=True)  # 商品名称
    barcode = Column(String(50), nullable=True, index=True)  # 基本条码
    spec = Column(String(100), nullable=True)  # 规格型号
    unit = Column(String(20), nullable=True)  # 基本计量单位
    
    # 品牌和产地
    brand_code = Column(String(50), nullable=True)  # 品牌编码
    brand_name = Column(String(100), nullable=True, index=True)  # 品牌名称
    origin = Column(String(200), nullable=True)  # 商品产地
    
    # 价格信息（参考）
    purchase_price = Column(Float, nullable=True)  # 参考进价
    sale_price = Column(Float, nullable=True)  # 参考售价
    
    # 供应商信息
    supplier_code = Column(String(50), nullable=True)  # 供应商编码
    supplier_name = Column(String(200), nullable=True)  # 供应商名称
    purchaser = Column(String(50), nullable=True)  # 采购员
    product_attribute = Column(String(50), nullable=True)  # 商品属性
    
    # 状态
    status = Column(String(50), nullable=True)  # 经营状态名称
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CompetitorStore(Base):
    """竞店信息"""
    __tablename__ = "competitor_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String(100), index=True, nullable=False)  # 门店名称（如：蔡家坡店）
    competitor_name = Column(String(200), nullable=False)  # 竞店名称
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 创建数据库表
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

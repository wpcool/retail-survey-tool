"""
导入商品明细数据
先清空旧数据，然后导入新的商品明细.xlsx
"""
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product, Base
from datetime import datetime

# 数据库配置
DATABASE_URL = "sqlite:///data/survey.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_old_products():
    """清空旧商品数据"""
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        print(f"正在清空 {count} 条旧商品数据...")
        db.query(Product).delete()
        db.commit()
        print("✓ 旧数据已清空")
    except Exception as e:
        db.rollback()
        print(f"✗ 清空失败: {e}")
        raise
    finally:
        db.close()

def import_new_products():
    """导入新商品数据"""
    # 读取Excel
    print("\n正在读取商品明细.xlsx...")
    df = pd.read_excel('../商品明细.xlsx')
    print(f"✓ 读取完成，共 {len(df)} 条数据")
    
    # 查看列名
    print(f"\n数据列: {df.columns.tolist()}")
    
    # 数据清洗和转换
    print("\n正在处理数据...")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        batch_size = 1000
        total = len(df)
        imported = 0
        
        for idx, row in df.iterrows():
            try:
                # 创建商品对象
                product = Product(
                    # 四级分类
                    category_level1_code=str(row.get('一级分类编码', '')) if pd.notna(row.get('一级分类编码')) else None,
                    category_level1_name=str(row.get('一级分类名称', '')) if pd.notna(row.get('一级分类名称')) else None,
                    category_level2_code=str(row.get('二级分类编码', '')) if pd.notna(row.get('二级分类编码')) else None,
                    category_level2_name=str(row.get('二级分类名称', '')) if pd.notna(row.get('二级分类名称')) else None,
                    category_level3_code=str(row.get('三级分类编码', '')) if pd.notna(row.get('三级分类编码')) else None,
                    category_level3_name=str(row.get('三级分类名称', '')) if pd.notna(row.get('三级分类名称')) else None,
                    category_level4_code=str(row.get('四级分类编码', '')) if pd.notna(row.get('四级分类编码')) else None,
                    category_level4_name=str(row.get('四级分类名称', '')) if pd.notna(row.get('四级分类名称')) else None,
                    
                    # 商品基本信息
                    product_code=str(row.get('商品编码', '')) if pd.notna(row.get('商品编码')) else None,
                    name=str(row.get('商品名称', '')).strip() if pd.notna(row.get('商品名称')) else '',
                    barcode=str(row.get('基本条码', '')) if pd.notna(row.get('基本条码')) else None,
                    spec=str(row.get('规格型号', '')) if pd.notna(row.get('规格型号')) else None,
                    unit=str(row.get('基本计量单位', '')) if pd.notna(row.get('基本计量单位')) else None,
                    
                    # 品牌和产地
                    brand_code=str(row.get('品牌编码', '')) if pd.notna(row.get('品牌编码')) else None,
                    brand_name=str(row.get('品牌名称', '')) if pd.notna(row.get('品牌名称')) else None,
                    origin=str(row.get('商品产地', '')) if pd.notna(row.get('商品产地')) else None,
                    
                    # 价格
                    purchase_price=float(row.get('参考进价', 0)) if pd.notna(row.get('参考进价')) else None,
                    sale_price=float(row.get('参考售价', 0)) if pd.notna(row.get('参考售价')) else None,
                    
                    # 供应商
                    supplier_code=str(row.get('供应商编码', '')) if pd.notna(row.get('供应商编码')) else None,
                    supplier_name=str(row.get('供应商名称', '')) if pd.notna(row.get('供应商名称')) else None,
                    
                    # 状态
                    status=str(row.get('经营状态名称', '')) if pd.notna(row.get('经营状态名称')) else None,
                    is_active=True
                )
                
                db.add(product)
                imported += 1
                
                # 批量提交
                if imported % batch_size == 0:
                    db.commit()
                    progress = (imported / total) * 100
                    print(f"  进度: {imported}/{total} ({progress:.1f}%)")
                
            except Exception as e:
                print(f"  第 {idx+1} 行导入失败: {e}")
                continue
        
        # 提交剩余数据
        db.commit()
        print(f"\n✓ 导入完成！成功导入 {imported} 条商品数据")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 导入失败: {e}")
        raise
    finally:
        db.close()

def show_stats():
    """显示导入后的统计"""
    db = SessionLocal()
    try:
        total = db.query(Product).count()
        print(f"\n=== 导入后统计 ===")
        print(f"总商品数: {total}")
        
        # 一级分类统计
        print(f"\n一级分类分布:")
        from sqlalchemy import func
        categories = db.query(Product.category_level1_name, func.count(Product.id)).group_by(Product.category_level1_name).all()
        for cat, count in sorted(categories, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cat}: {count}个")
        
        # 品牌统计
        print(f"\n品牌分布(前10):")
        brands = db.query(Product.brand_name, func.count(Product.id)).filter(Product.brand_name != None).group_by(Product.brand_name).all()
        for brand, count in sorted(brands, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {brand}: {count}个")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("商品数据导入工具")
    print("=" * 60)
    
    # 确认操作
    print("\n⚠️  警告: 这将清空所有旧商品数据并导入新数据！")
    response = input("是否继续? (输入 'yes' 确认): ")
    
    if response.lower() != 'yes':
        print("操作已取消")
        sys.exit(0)
    
    try:
        # 1. 清空旧数据
        clear_old_products()
        
        # 2. 导入新数据
        import_new_products()
        
        # 3. 显示统计
        show_stats()
        
        print("\n" + "=" * 60)
        print("✓ 数据导入完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)
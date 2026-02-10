"""
竞店管理模块
支持从Excel导入初始数据，后续通过数据库进行增删改查
"""
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from models import CompetitorStore, get_db

# 标记是否已从Excel导入数据
_data_imported = False

def import_from_excel(db: Session) -> bool:
    """从Excel文件导入竞店数据到数据库（仅首次）"""
    global _data_imported
    
    if _data_imported:
        return True
    
    # 检查数据库中是否已有数据
    if db.query(CompetitorStore).first():
        _data_imported = True
        return True
    
    excel_path = Path(__file__).parent.parent / "excel_file" / "竟争店.xlsx"
    
    if not excel_path.exists():
        print(f"Excel文件不存在: {excel_path}")
        return False
    
    try:
        df = pd.read_excel(excel_path, header=None)
        current_store = None
        imported_count = 0
        
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[0, col_idx]
            
            # 如果遇到店铺名称（不为NaN），开始新的门店
            if pd.notna(cell_value) and str(cell_value).strip():
                current_store = str(cell_value).strip()
            
            # 将竞店名称添加到当前门店
            if current_store and pd.notna(df.iloc[1, col_idx]):
                competitor = str(df.iloc[1, col_idx]).strip()
                if competitor:
                    # 检查是否已存在
                    exists = db.query(CompetitorStore).filter(
                        CompetitorStore.store_name == current_store,
                        CompetitorStore.competitor_name == competitor
                    ).first()
                    
                    if not exists:
                        cs = CompetitorStore(
                            store_name=current_store,
                            competitor_name=competitor
                        )
                        db.add(cs)
                        imported_count += 1
        
        db.commit()
        _data_imported = True
        print(f"已从Excel导入 {imported_count} 条竞店数据")
        return True
    except Exception as e:
        print(f"导入竞店数据失败: {e}")
        db.rollback()
        return False


def get_all_stores(db: Session) -> List[str]:
    """获取所有门店列表"""
    import_from_excel(db)
    stores = db.query(CompetitorStore.store_name).distinct().all()
    return [s[0] for s in stores]


def get_store_competitors(db: Session, store_name: str) -> List[Dict]:
    """获取指定门店的竞店列表"""
    import_from_excel(db)
    competitors = db.query(CompetitorStore).filter(
        CompetitorStore.store_name == store_name
    ).all()
    return [{"id": c.id, "name": c.competitor_name} for c in competitors]


def get_all_competitor_stores(db: Session) -> List[Dict]:
    """获取所有门店及其竞店信息"""
    import_from_excel(db)
    
    # 获取所有门店名称
    store_names = get_all_stores(db)
    result = []
    
    for store_name in store_names:
        competitors = db.query(CompetitorStore).filter(
            CompetitorStore.store_name == store_name
        ).all()
        result.append({
            "store": store_name,
            "competitors": [c.competitor_name for c in competitors],
            "count": len(competitors)
        })
    
    return result


def get_all_competitors(db: Session) -> List[str]:
    """获取所有竞店名称（去重）"""
    import_from_excel(db)
    competitors = db.query(CompetitorStore.competitor_name).distinct().all()
    return [c[0] for c in competitors]


def search_competitors(db: Session, keyword: str = "", store: str = "") -> List[Dict]:
    """
    搜索竞店
    :param keyword: 竞店名称关键词
    :param store: 门店名称筛选
    :return: 筛选后的竞店数据
    """
    import_from_excel(db)
    
    query = db.query(CompetitorStore)
    
    if store:
        query = query.filter(CompetitorStore.store_name == store)
    
    if keyword:
        query = query.filter(CompetitorStore.competitor_name.ilike(f"%{keyword}%"))
    
    results = query.all()
    
    # 按门店分组
    store_map = {}
    for r in results:
        if r.store_name not in store_map:
            store_map[r.store_name] = []
        store_map[r.store_name].append(r.competitor_name)
    
    return [
        {"store": store_name, "competitors": competitors, "count": len(competitors)}
        for store_name, competitors in store_map.items()
    ]


def get_competitor_stats(db: Session) -> Dict:
    """获取竞店统计数据"""
    import_from_excel(db)
    
    total_stores = db.query(CompetitorStore.store_name).distinct().count()
    total_competitors = db.query(CompetitorStore).count()
    avg_competitors = round(total_competitors / total_stores, 1) if total_stores > 0 else 0
    
    # 竞店最多的门店
    from sqlalchemy import func
    store_counts = db.query(
        CompetitorStore.store_name,
        func.count(CompetitorStore.id).label('count')
    ).group_by(CompetitorStore.store_name).order_by(func.count(CompetitorStore.id).desc()).first()
    
    max_store = store_counts[0] if store_counts else ""
    max_count = store_counts[1] if store_counts else 0
    
    return {
        "total_stores": total_stores,
        "total_competitors": total_competitors,
        "avg_competitors": avg_competitors,
        "max_store": max_store,
        "max_count": max_count
    }


def add_competitor(db: Session, store_name: str, competitor_name: str) -> bool:
    """添加竞店"""
    # 检查是否已存在
    exists = db.query(CompetitorStore).filter(
        CompetitorStore.store_name == store_name,
        CompetitorStore.competitor_name == competitor_name
    ).first()
    
    if exists:
        return False
    
    cs = CompetitorStore(
        store_name=store_name,
        competitor_name=competitor_name
    )
    db.add(cs)
    db.commit()
    return True


def update_competitor(db: Session, competitor_id: int, new_name: str) -> bool:
    """修改竞店名称"""
    competitor = db.query(CompetitorStore).filter(CompetitorStore.id == competitor_id).first()
    
    if not competitor:
        return False
    
    competitor.competitor_name = new_name
    db.commit()
    return True


def delete_competitor(db: Session, competitor_id: int) -> bool:
    """删除竞店"""
    competitor = db.query(CompetitorStore).filter(CompetitorStore.id == competitor_id).first()
    
    if not competitor:
        return False
    
    db.delete(competitor)
    db.commit()
    return True

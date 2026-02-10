"""
竞店管理模块
从Excel文件读取各门店的竞店信息
"""
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

# 缓存竞店数据
_competitor_data: Optional[Dict[str, List[str]]] = None

def load_competitor_data() -> Dict[str, List[str]]:
    """从Excel文件加载竞店数据"""
    global _competitor_data
    
    if _competitor_data is not None:
        return _competitor_data
    
    excel_path = Path(__file__).parent.parent / "excel_file" / "竟争店.xlsx"
    
    if not excel_path.exists():
        return {}
    
    try:
        df = pd.read_excel(excel_path, header=None)
        stores = {}
        current_store = None
        
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[0, col_idx]
            
            # 如果遇到店铺名称（不为NaN），开始新的门店
            if pd.notna(cell_value) and str(cell_value).strip():
                current_store = str(cell_value).strip()
                stores[current_store] = []
            
            # 将竞店名称添加到当前门店
            if current_store and pd.notna(df.iloc[1, col_idx]):
                competitor = str(df.iloc[1, col_idx]).strip()
                if competitor and competitor not in stores[current_store]:
                    stores[current_store].append(competitor)
        
        _competitor_data = stores
        return stores
    except Exception as e:
        print(f"加载竞店数据失败: {e}")
        return {}

def get_all_stores() -> List[str]:
    """获取所有门店列表"""
    data = load_competitor_data()
    return list(data.keys())

def get_store_competitors(store_name: str) -> List[str]:
    """获取指定门店的竞店列表"""
    data = load_competitor_data()
    return data.get(store_name, [])

def get_all_competitors() -> List[str]:
    """获取所有竞店名称（去重）"""
    data = load_competitor_data()
    all_competitors = set()
    for competitors in data.values():
        all_competitors.update(competitors)
    return sorted(list(all_competitors))

def search_competitors(keyword: str = "", store: str = "") -> Dict:
    """
    搜索竞店
    :param keyword: 竞店名称关键词
    :param store: 门店名称筛选
    :return: 筛选后的竞店数据
    """
    data = load_competitor_data()
    result = {}
    
    for store_name, competitors in data.items():
        # 门店筛选
        if store and store != store_name:
            continue
        
        # 关键词筛选
        if keyword:
            filtered = [c for c in competitors if keyword.lower() in c.lower()]
            if filtered:
                result[store_name] = filtered
        else:
            result[store_name] = competitors
    
    return result

def get_competitor_stats() -> Dict:
    """获取竞店统计数据"""
    data = load_competitor_data()
    
    total_stores = len(data)
    total_competitors = sum(len(competitors) for competitors in data.values())
    avg_competitors = round(total_competitors / total_stores, 1) if total_stores > 0 else 0
    
    # 竞店最多的门店
    max_store = ""
    max_count = 0
    for store_name, competitors in data.items():
        if len(competitors) > max_count:
            max_count = len(competitors)
            max_store = store_name
    
    return {
        "total_stores": total_stores,
        "total_competitors": total_competitors,
        "avg_competitors": avg_competitors,
        "max_store": max_store,
        "max_count": max_count
    }

# 市场调研分析功能整合方案

## 一、现状分析

### 1.1 当前系统数据结构

**已有数据表：**
- `SurveyRecord`: 调研记录（价格、促销、照片等）
- `Product`: 商品库（四级分类、参考进价、参考售价、商品属性等）
- `SurveyItem`: 调研任务商品项
- `CompetitorStore`: 竞店信息

**缺失字段（需补充）：**
- Product表缺少：`商品属性`（畅销/快消/正常/低周转/滞销）
- SurveyRecord表缺少：与商品的完整关联（目前通过name匹配）

### 1.2 BusinessAnalysis功能梳理

| 功能模块 | 说明 | 复用价值 |
|---------|------|---------|
| `market_data_filter` | 解析三级表头Excel | ❌ 不需要，数据已在数据库 |
| `adjust_price_by_attribute` | 根据商品属性调价 | ✅ 核心算法复用 |
| `regional_analysis` | 区域维度汇总 | ✅ 改为按"门店+区域"分析 |
| `purchase_analysis` | 采购员维度汇总 | ✅ 改为按"商品分类"分析 |
| `save_excel` | Excel格式化导出 | ✅ 复用导出逻辑 |

---

## 二、整合方案

### 2.1 数据库层面

**新增字段：**
```python
# Product表新增
product_attribute = Column(String(50), nullable=True)  # 商品属性：畅销商品/快消商品/正常商品/低周转商品/滞销商品

# SurveyRecord表新增（可选，用于更精确关联）
product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
```

**商品属性调价系数（复用原逻辑）：**
```python
ATTRIBUTE_PRICE_FACTORS = {
    '畅销商品': 0.95,
    '快消商品': 0.96,
    '正常商品': 0.97,
    '低周转商品': 0.98,
    '滞销商品': 0.99
}
```

### 2.2 后端API设计

#### 2.2.1 新增分析模块 `backend/market_analysis.py`

```python
"""
市场调研分析模块
整合自 BusinessAnalysis/market_search.py
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import SurveyRecord, Product, SurveyItem
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

# 商品属性调价系数
ATTRIBUTE_PRICE_FACTORS = {
    '畅销商品': 0.95,
    '快消商品': 0.96,
    '正常商品': 0.97,
    '低周转商品': 0.98,
    '滞销商品': 0.99
}


def calculate_adjusted_price(product: Product) -> Optional[float]:
    """
    根据商品属性计算调整后售价
    属性系数 * 参考售价
    """
    if not product.sale_price:
        return None
    
    factor = ATTRIBUTE_PRICE_FACTORS.get(product.product_attribute, 1.0)
    return product.sale_price * factor


def calculate_price_index(our_price: float, competitor_price: float) -> Optional[float]:
    """
    计算价格指数 = 本店售价 / 竞争店售价
    """
    if not competitor_price or competitor_price == 0:
        return None
    return our_price / competitor_price


def analyze_by_own_store_and_product(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    own_store_name: Optional[str] = None
) -> pd.DataFrame:
    """
    分析结果（替代原区域分析）
    按【自己门店+商品分类】维度汇总
    
    输出字段：
    - 日期、自己门店、商品分类
    - 本店供价(合计)、本店售价(合计)、调整后售价(合计)
    - 竞争店售价(合计/平均)、价格指数(平均)
    - 市调单品数、市调单品数占总数比
    """
    # 1. 查询调研记录，关联商品信息
    query = db.query(
        SurveyRecord,
        Product
    ).outerjoin(
        Product, SurveyRecord.item_id == SurveyItem.id
    ).join(
        SurveyItem, SurveyRecord.item_id == SurveyItem.id
    )
    
    # 2. 应用筛选条件
    if start_date:
        query = query.filter(SurveyRecord.created_at >= f"{start_date} 00:00:00")
    if end_date:
        query = query.filter(SurveyRecord.created_at <= f"{end_date} 23:59:59")
    if own_store_name:
        query = query.filter(SurveyRecord.own_store_name == own_store_name)
    
    records = query.all()
    
    # 3. 构建分析数据
    data = []
    for survey_record, product in records:
        adjusted_price = calculate_adjusted_price(product) if product else None
        price_index = calculate_price_index(
            product.sale_price if product else 0,
            survey_record.price
        )
        
        data.append({
            '日期': survey_record.created_at.strftime('%Y-%m-%d'),
            '自己门店': survey_record.own_store_name or '未指定',
            '商品分类': product.category_level3_name if product else '未分类',
            '商品名称': survey_record.item.product_name if survey_record.item else '',
            '商品条码': product.barcode if product else '',
            '本店供价': product.purchase_price if product else 0,
            '本店售价': product.sale_price if product else 0,
            '调整后售价': adjusted_price,
            '竞争店名称': survey_record.store_name,
            '竞争店售价': survey_record.price,
            '竞争店促销价': survey_record.promotion_info,  # 需解析促销价
            '价格指数': price_index,
            '商品属性': product.product_attribute if product else '正常商品'
        })
    
    df = pd.DataFrame(data)
    
    # 4. 按【自己门店+商品分类】汇总
    grouped = df.groupby(['日期', '自己门店', '商品分类']).agg({
        '本店供价': 'sum',
        '本店售价': 'sum',
        '调整后售价': 'sum',
        '竞争店售价': ['sum', 'mean'],
        '价格指数': 'mean',
        '商品名称': 'nunique'  # 市调单品数
    }).reset_index()
    
    # 5. 重命名列
    grouped.columns = ['日期', '自己门店', '商品分类', '本店供价', '本店售价', 
                       '调整后售价', '竞争店售价(合计)', '竞争店售价(平均)', 
                       '价格指数(平均)', '市调单品数']
    
    # 6. 计算毛利率
    grouped['调前毛利率'] = (grouped['本店售价'] - grouped['本店供价']) / grouped['本店售价']
    grouped['调后毛利率'] = (grouped['调整后售价'] - grouped['本店供价']) / grouped['调整后售价']
    
    return grouped


def analyze_by_category_and_brand(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    分析结果（替代原采购分析）
    按【商品分类+品牌】维度汇总
    """
    # 类似上述逻辑，按category_level4_name + brand_name分组
    pass


def export_analysis_to_excel(
    df_store_analysis: pd.DataFrame,
    df_category_analysis: pd.DataFrame,
    output_path: str
):
    """
    导出分析结果到Excel（复用原save_excel逻辑）
    - 门店分析Sheet
    - 分类分析Sheet
    - 格式化：百分比、条件标红（价格指数>0.95标红）
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_store_analysis.to_excel(writer, sheet_name='门店分析', index=False)
        df_category_analysis.to_excel(writer, sheet_name='分类分析', index=False)
    
    # 应用格式化（百分比、条件标红）
    format_excel_output(output_path)


def format_excel_output(file_path: str):
    """
    格式化Excel输出（从原market_search.py迁移）
    - 毛利率、价格指数格式化为百分比
    - 价格指数>0.95的单元格标红
    """
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill
    
    book = load_workbook(file_path)
    
    for sheet_name in book.sheetnames:
        ws = book[sheet_name]
        
        # 找到需要格式化的列
        percent_columns = ['调前毛利率', '调后毛利率', '价格指数(平均)', '市调单品数占总数比']
        price_index_cols = []
        
        for col_idx in range(1, ws.max_column + 1):
            header = ws.cell(row=1, column=col_idx).value
            if header in percent_columns:
                price_index_cols.append(col_idx)
        
        # 格式化数据行
        red_fill = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
        
        for row_idx in range(2, ws.max_row + 1):
            for col_idx in price_index_cols:
                cell = ws.cell(row=row_idx, column=col_idx)
                if cell.value is not None:
                    try:
                        value = float(cell.value)
                        cell.number_format = '0.00%'
                        
                        # 价格指数>0.95标红
                        if '价格指数' in str(ws.cell(row=1, column=col_idx).value) and value > 0.95:
                            cell.fill = red_fill
                    except:
                        pass
    
    book.save(file_path)
```

#### 2.2.2 新增API端点 `backend/main.py`

```python
# ========== 市场调研分析API ==========

@app.get("/api/analysis/store")
def get_store_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    own_store_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取门店维度分析数据
    """
    from market_analysis import analyze_by_own_store_and_product
    
    df = analyze_by_own_store_and_product(db, start_date, end_date, own_store_name)
    
    # 转换为JSON返回
    return {
        "success": True,
        "data": df.to_dict(orient='records'),
        "total": len(df)
    }


@app.get("/api/analysis/category")
def get_category_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取商品分类维度分析数据
    """
    from market_analysis import analyze_by_category_and_brand
    
    df = analyze_by_category_and_brand(db, start_date, end_date)
    
    return {
        "success": True,
        "data": df.to_dict(orient='records'),
        "total": len(df)
    }


@app.get("/api/analysis/export")
def export_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    导出分析结果Excel
    """
    from market_analysis import (
        analyze_by_own_store_and_product,
        analyze_by_category_and_brand,
        export_analysis_to_excel
    )
    import tempfile
    import os
    
    # 生成分析数据
    df_store = analyze_by_own_store_and_product(db, start_date, end_date)
    df_category = analyze_by_category_and_brand(db, start_date, end_date)
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    
    # 导出Excel
    export_analysis_to_excel(df_store, df_category, temp_file.name)
    
    # 返回文件
    from fastapi.responses import FileResponse
    return FileResponse(
        temp_file.name,
        filename=f"市场调研分析_{start_date or 'all'}_{end_date or 'all'}.xlsx",
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
```

### 2.3 前端界面设计

#### 2.3.1 新增菜单项

在 `backend/static/index.html` 导航菜单中新增：

```html
<div class="nav-item" data-page="market-analysis">
    <span class="nav-icon">📊</span>
    <span>市场分析</span>
</div>
```

#### 2.3.2 分析页面结构

```javascript
function renderMarketAnalysisPage() {
    return `
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 市场调研结果分析</span>
                <button class="btn btn-success" onclick="exportAnalysis()">📥 导出Excel</button>
            </div>
            <div class="card-body">
                <!-- 筛选栏 -->
                <div class="search-bar">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <label>日期范围：</label>
                        <input type="date" class="search-input" id="analysisStartDate">
                        <span>至</span>
                        <input type="date" class="search-input" id="analysisEndDate">
                    </div>
                    <select class="search-input" id="analysisStoreFilter">
                        <option value="">所有门店</option>
                    </select>
                    <button class="btn btn-primary" onclick="loadAnalysis()">分析</button>
                </div>
                
                <!-- 统计卡片 -->
                <div class="stats-row" style="grid-template-columns: repeat(4, 1fr); margin: 20px 0;">
                    <div class="stat-card">
                        <div class="stat-icon blue">🏪</div>
                        <div class="stat-info">
                            <h3>分析门店数</h3>
                            <div class="value" id="analysisStoreCount">0</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green">📦</div>
                        <div class="stat-info">
                            <h3>分析商品数</h3>
                            <div class="value" id="analysisProductCount">0</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon orange">📈</div>
                        <div class="stat-info">
                            <h3>平均价格指数</h3>
                            <div class="value" id="analysisPriceIndex">0%</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon red">⚠️</div>
                        <div class="stat-info">
                            <h3>高价预警数</h3>
                            <div class="value" id="analysisWarningCount">0</div>
                        </div>
                    </div>
                </div>
                
                <!-- 分析结果表格 -->
                <div class="card" style="margin-top: 24px;">
                    <div class="card-header">
                        <span class="card-title">🏪 门店维度分析</span>
                    </div>
                    <div class="table-container" id="storeAnalysisTable">
                        <!-- 动态加载 -->
                    </div>
                </div>
                
                <div class="card" style="margin-top: 24px;">
                    <div class="card-header">
                        <span class="card-title">📂 商品分类维度分析</span>
                    </div>
                    <div class="table-container" id="categoryAnalysisTable">
                        <!-- 动态加载 -->
                    </div>
                </div>
            </div>
        </div>
    `;
}
```

#### 2.3.3 关键前端逻辑

```javascript
async function loadAnalysis() {
    const startDate = document.getElementById('analysisStartDate').value;
    const endDate = document.getElementById('analysisEndDate').value;
    const store = document.getElementById('analysisStoreFilter').value;
    
    try {
        // 加载门店分析
        const storeRes = await fetch(`${API_BASE}/api/analysis/store?start_date=${startDate}&end_date=${endDate}&own_store_name=${store}`);
        const storeData = await storeRes.json();
        
        renderStoreAnalysisTable(storeData.data);
        updateAnalysisStats(storeData.data);
        
        // 加载分类分析
        const catRes = await fetch(`${API_BASE}/api/analysis/category?start_date=${startDate}&end_date=${endDate}`);
        const catData = await catRes.json();
        
        renderCategoryAnalysisTable(catData.data);
    } catch (e) {
        showToast('加载分析数据失败', 'error');
    }
}

function renderStoreAnalysisTable(data) {
    // 渲染表格，价格指数>0.95的行标红
    const html = data.map((row, i) => {
        const warningClass = row['价格指数(平均)'] > 0.95 ? 'style="background: rgba(255,0,0,0.1);"' : '';
        return `
            <tr ${warningClass}>
                <td>${row['自己门店']}</td>
                <td>${row['商品分类']}</td>
                <td>¥${row['本店售价'].toFixed(2)}</td>
                <td>¥${row['调整后售价'].toFixed(2)}</td>
                <td>¥${row['竞争店售价(平均)'].toFixed(2)}</td>
                <td>${(row['价格指数(平均)'] * 100).toFixed(2)}%</td>
                <td>${(row['调前毛利率'] * 100).toFixed(2)}%</td>
                <td>${(row['调后毛利率'] * 100).toFixed(2)}%</td>
                <td>${row['市调单品数']}</td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('storeAnalysisTable').innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>自己门店</th>
                    <th>商品分类</th>
                    <th>本店售价</th>
                    <th>调整后售价</th>
                    <th>竞争店售价(平均)</th>
                    <th>价格指数</th>
                    <th>调前毛利率</th>
                    <th>调后毛利率</th>
                    <th>市调单品数</th>
                </tr>
            </thead>
            <tbody>${html}</tbody>
        </table>
    `;
}

function exportAnalysis() {
    const startDate = document.getElementById('analysisStartDate').value;
    const endDate = document.getElementById('analysisEndDate').value;
    
    window.open(`${API_BASE}/api/analysis/export?start_date=${startDate}&end_date=${endDate}`);
}
```

---

## 三、实施步骤

### Phase 1: 数据库迁移（1天）
1. 修改 `models.py`，给 Product 表添加 `product_attribute` 字段
2. 创建数据库迁移脚本（或自动重建）
3. 为现有商品设置默认属性值

### Phase 2: 后端开发（2-3天）
1. 创建 `backend/market_analysis.py` 分析模块
2. 在 `main.py` 中添加分析API端点
3. 测试API返回数据正确性

### Phase 3: 前端开发（2天）
1. 在 `index.html` 中添加市场分析页面
2. 实现数据表格渲染
3. 实现导出功能
4. 联调测试

### Phase 4: 数据迁移（1天）
1. 从旧Excel中导入商品属性数据
2. 验证分析结果与原系统一致

---

## 四、与原系统的关键差异处理

| 原系统(BusinessAnalysis) | 新系统(retail-survey-tool) | 处理方式 |
|-------------------------|---------------------------|---------|
| 三级表头Excel输入 | 数据库存储 | 直接从DB查询，无需解析Excel |
| 按"区域+部门"分析 | 按"自己门店+商品分类"分析 | 调整分组维度 |
| 按"采购+商品分类3"分析 | 按"商品分类+品牌"分析 | 调整分组维度 |
| 商品属性决定调价系数 | 商品属性存储在Product表 | 直接读取product_attribute字段 |
| 促销价、会员价单独列 | 促销信息存储在promotion_info | 解析promotion_info提取促销价 |

---

## 五、预期效果

### 5.1 后台可直接查看
- 按门店汇总的竞争分析数据
- 价格指数和毛利率对比
- 高价预警（价格指数>0.95标红）
- 支持日期范围筛选

### 5.2 导出功能
- 导出格式化Excel（与原系统格式一致）
- 包含门店分析和分类分析两个Sheet
- 自动标红预警数据

---

## 六、需要确认的问题

1. **商品属性数据来源**：现有Product表是否已有商品属性字段？如果没有，如何批量导入？

2. **促销价提取逻辑**：SurveyRecord的promotion_info字段存储格式是什么？如何从中提取促销价？

3. **"自己门店"字段**：own_store_name字段是否已在使用？数据完整性如何？

4. **分析维度确认**：
   - 门店分析维度：自己门店 + 商品分类（三级分类？）
   - 分类分析维度：商品分类（四级分类？）+ 品牌

5. **历史数据处理**：是否只分析新系统的调研记录？还是需要导入旧Excel数据？

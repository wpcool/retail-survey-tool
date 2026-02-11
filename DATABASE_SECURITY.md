# 🔒 数据库安全操作指南

## 安全机制概述

本系统已启用数据库保护机制，所有危险操作都需要**双重确认**才能执行。

## ⚠️ 危险操作清单

以下操作被视为危险操作，需要特别确认：

| 操作 | 风险等级 | 确认方式 |
|-----|---------|---------|
| 删除数据库文件 | 🔴 极高 | 输入 `DELETE` + `DATABASE` |
| 清空数据表 | 🔴 极高 | 输入 `DELETE` + `DATABASE` |
| 删除调研人员 | 🟠 高 | 输入确认码 `DELETE_SURVEYOR_ID` |
| 删除调研记录 | 🟡 中 | 输入确认码 `DELETE_RECORD_ID` |
| 重新导入商品数据 | 🟡 中 | 输入 `DELETE` + `DATABASE` |

## 🚀 安全启动

使用安全启动脚本：

```bash
./safe_start.sh
```

此脚本会：
- 检查数据库文件状态
- 显示各表记录数
- 启动后端服务

## 🛡️ 后端API删除保护

### 删除调研人员
```bash
# ❌ 错误 - 会提示需要确认码
DELETE /api/surveyors/1

# ✅ 正确 - 传入确认码
DELETE /api/surveyors/1?confirm=DELETE_SURVEYOR_1
```

### 删除调研记录
```bash
# ❌ 错误 - 会提示需要确认码
DELETE /api/records/28

# ✅ 正确 - 传入确认码
DELETE /api/records/28?confirm=DELETE_RECORD_28
```

## 📦 商品数据导入保护

运行导入脚本时需要**双重确认**：

```bash
cd backend
python import_products.py

# 提示：
# 1. 输入 'DELETE' 确认
# 2. 输入 'DATABASE' 最终确认
```

**如需跳过确认**（仅用于自动化脚本）：
```bash
export DB_GUARD_SKIP=1
python import_products.py
```

## 🔧 安全添加字段（推荐操作）

如需添加新字段，使用 `ALTER TABLE`，**绝不删除表**：

```python
# ✅ 正确 - 添加字段
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///data/survey.db')
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE products ADD COLUMN purchaser VARCHAR(50)'))
    conn.commit()
```

```python
# ❌ 错误 - 会丢失所有数据！
# DROP TABLE products
# 或删除 survey.db 文件
```

## 📋 数据库备份

### 手动备份
```bash
# 备份数据库文件
cp backend/data/survey.db "backend/data/survey.db.backup.$(date +%Y%m%d)"

# 备份照片
tar -czf "photos.backup.$(date +%Y%m%d).tar.gz" backend/static/photos/
```

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp backend/data/survey.db "backups/survey.db.$DATE"
# 保留最近10个备份
ls -t backups/survey.db.* | tail -n +11 | xargs rm -f
echo "备份完成: $DATE"
```

## 🚨 紧急情况

### 误删除恢复
如果误删了数据库文件，尝试从git恢复：
```bash
# 查看最新提交的数据库文件
git log --oneline -- backend/data/survey.db

# 恢复到指定版本
git checkout <commit_id> -- backend/data/survey.db
```

### 数据损坏修复
```bash
# SQLite 数据库修复
sqlite3 backend/data/survey.db ".dump" > backup.sql
sqlite3 new.db < backup.sql
mv new.db backend/data/survey.db
```

## 📞 联系支持

如遇数据库问题，请：
1. **立即停止操作**，避免进一步损坏
2. 备份当前数据库文件
3. 联系技术支持

---

**⚠️ 再次提醒：删除数据库前请务必确认已备份重要数据！**

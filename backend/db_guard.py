"""
数据库安全保护机制
危险操作需要用户确认
"""
import os
import sys

# 危险操作白名单（如果需要自动化执行，可以设置环境变量跳过确认）
DB_GUARD_SKIP = os.environ.get('DB_GUARD_SKIP', '').lower() in ('1', 'true', 'yes')

# 危险操作关键词
DANGEROUS_OPERATIONS = [
    'delete from',
    'drop table',
    'drop database',
    'truncate table',
    'remove file',
    'rm -rf',
    'del survey.db',
    '清空',
    '删除',
]


def confirm_dangerous_operation(operation_name: str, details: str = "") -> bool:
    """
    危险操作确认
    返回 True 表示用户确认执行，False 表示取消
    """
    # 检查是否通过环境变量跳过确认（仅用于CI/CD自动化）
    if DB_GUARD_SKIP:
        print(f"⚠️  [DB_GUARD] 跳过确认（环境变量 DB_GUARD_SKIP={DB_GUARD_SKIP}）: {operation_name}")
        return True
    
    print("\n" + "=" * 60)
    print("🔴 危险操作警告 - DATABASE GUARD")
    print("=" * 60)
    print(f"操作类型: {operation_name}")
    if details:
        print(f"操作详情: {details}")
    print("-" * 60)
    print("⚠️  此操作可能导致数据丢失！")
    print("⚠️  请确保您已备份重要数据！")
    print("=" * 60)
    
    # 双重确认
    confirm1 = input(f"\n输入 'DELETE' 确认执行 [{operation_name}]: ").strip()
    if confirm1 != 'DELETE':
        print("❌ 操作已取消（第一次确认未通过）")
        return False
    
    confirm2 = input("再次输入 'DATABASE' 最终确认: ").strip()
    if confirm2 != 'DATABASE':
        print("❌ 操作已取消（第二次确认未通过）")
        return False
    
    print(f"✅ 危险操作已确认: {operation_name}")
    return True


def guard_delete_file(filepath: str) -> bool:
    """保护删除文件操作"""
    if not os.path.exists(filepath):
        return True  # 文件不存在，无需删除
    
    filename = os.path.basename(filepath)
    details = f"文件路径: {filepath}\n文件大小: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB"
    
    return confirm_dangerous_operation(f"删除数据库文件 [{filename}]", details)


def guard_truncate_table(table_name: str, record_count: int = None) -> bool:
    """保护清空表操作"""
    details = f"表名: {table_name}"
    if record_count is not None:
        details += f"\n记录数: {record_count} 条"
    
    return confirm_dangerous_operation(f"清空数据表 [{table_name}]", details)


def check_dangerous_sql(sql: str) -> bool:
    """检查SQL语句是否包含危险操作"""
    sql_lower = sql.lower().strip()
    
    for keyword in DANGEROUS_OPERATIONS:
        if keyword.lower() in sql_lower:
            return confirm_dangerous_operation(
                f"执行危险SQL",
                f"SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}"
            )
    
    return True


# 装饰器模式保护函数
def protected(func):
    """装饰器：保护函数执行危险操作"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # 检查是否是危险操作函数
        dangerous_funcs = ['clear_old_products', 'delete', 'drop', 'truncate']
        if any(d in func_name.lower() for d in dangerous_funcs):
            if not confirm_dangerous_operation(f"执行函数 [{func_name}]"):
                print(f"❌ 函数 {func_name} 已被取消")
                return None
        
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    # 测试
    print("测试数据库保护机制...")
    result = confirm_dangerous_operation("测试操作", "这是一条测试")
    print(f"测试结果: {'通过' if result else '取消'}")

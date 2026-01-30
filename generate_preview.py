#!/usr/bin/env python3
"""
生成移动端App界面预览图
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 颜色配置
COLORS = {
    'primary': '#1976D2',      # 主色 - 蓝色
    'primary_dark': '#1565C0', # 深色主色
    'accent': '#FF5722',       # 强调色
    'background': '#F5F5F5',   # 背景色
    'white': '#FFFFFF',
    'text': '#333333',
    'text_secondary': '#666666',
    'text_hint': '#999999',
    'divider': '#E0E0E0',
    'success': '#4CAF50',      # 绿色 - 已完成
    'card_bg': '#FFFFFF',
}

# 手机屏幕尺寸 (iPhone 14 Pro 比例)
PHONE_WIDTH = 400
PHONE_HEIGHT = 850


def create_font(size, bold=False):
    """创建字体"""
    try:
        # 尝试使用系统字体
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size)
        return ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def draw_phone_frame(draw):
    """绘制手机外框"""
    # 外框
    draw.rounded_rectangle([10, 10, PHONE_WIDTH-10, PHONE_HEIGHT-10], radius=40, 
                          outline='#333333', width=8, fill='#1a1a1a')
    # 屏幕区域
    draw.rounded_rectangle([25, 25, PHONE_WIDTH-25, PHONE_HEIGHT-25], radius=30, 
                          fill=COLORS['background'])
    # 灵动岛/刘海
    draw.rounded_rectangle([PHONE_WIDTH//2-60, 30, PHONE_WIDTH//2+60, 55], radius=15, fill='#1a1a1a')


def create_login_screen():
    """创建登录页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    # 手机外框
    draw_phone_frame(draw)
    
    # 内容区域（避开刘海）
    content_top = 80
    
    # 应用标题
    title_font = create_font(32, bold=True)
    draw.text((PHONE_WIDTH//2, content_top + 60), "零售调研工具", 
              fill=COLORS['primary'], font=title_font, anchor='mm')
    
    # 副标题
    subtitle_font = create_font(18)
    draw.text((PHONE_WIDTH//2, content_top + 110), "调研人员登录", 
              fill=COLORS['text_secondary'], font=subtitle_font, anchor='mm')
    
    # 用户名输入框
    input_y = content_top + 200
    draw_rounded_rect(draw, [50, input_y, PHONE_WIDTH-50, input_y+55], 8, COLORS['white'], COLORS['divider'])
    draw.text((70, input_y+28), "👤  用户名", fill=COLORS['text_secondary'], font=create_font(16), anchor='lm')
    
    # 密码输入框
    input_y2 = input_y + 80
    draw_rounded_rect(draw, [50, input_y2, PHONE_WIDTH-50, input_y2+55], 8, COLORS['white'], COLORS['divider'])
    draw.text((70, input_y2+28), "🔒  密码", fill=COLORS['text_secondary'], font=create_font(16), anchor='lm')
    draw.text((PHONE_WIDTH-80, input_y2+28), "••••••", fill=COLORS['text'], font=create_font(16), anchor='lm')
    
    # 登录按钮
    btn_y = input_y2 + 100
    draw_rounded_rect(draw, [50, btn_y, PHONE_WIDTH-50, btn_y+55], 8, COLORS['primary'])
    draw.text((PHONE_WIDTH//2, btn_y+28), "登 录", fill=COLORS['white'], font=create_font(18, bold=True), anchor='mm')
    
    # 提示信息
    hint_font = create_font(14)
    draw.text((PHONE_WIDTH//2, PHONE_HEIGHT-150), "测试账号: test / 123456", 
              fill=COLORS['text_hint'], font=hint_font, anchor='mm')
    
    return img


def create_task_screen():
    """创建任务列表页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    # 手机外框
    draw_phone_frame(draw)
    
    # 顶部状态栏
    draw.rectangle([25, 25, PHONE_WIDTH-25, 85], fill=COLORS['primary'])
    
    # 标题栏
    title_font = create_font(20, bold=True)
    draw.text((PHONE_WIDTH//2, 55), "今日调研任务", fill=COLORS['white'], font=title_font, anchor='mm')
    draw.text((PHONE_WIDTH-50, 55), "🔄", fill=COLORS['white'], font=create_font(20), anchor='mm')
    
    # 任务信息卡片
    card_y = 100
    draw_rounded_rect(draw, [35, card_y, PHONE_WIDTH-35, card_y+100], 12, COLORS['white'])
    
    # 任务标题
    draw.text((50, card_y+25), "2024-01-30 生鲜品类调研", fill=COLORS['text'], font=create_font(17, bold=True))
    draw.text((50, card_y+50), "调研附近超市的生鲜品类价格", fill=COLORS['text_secondary'], font=create_font(14))
    draw.text((50, card_y+78), "进度: 3/8  已完成 38%", fill=COLORS['primary'], font=create_font(14))
    
    # 品类列表
    category_y = card_y + 120
    
    # 类别标题 - 蔬菜
    draw.text((40, category_y), "▶ 蔬菜", fill=COLORS['text'], font=create_font(16, bold=True))
    
    # 蔬菜品类
    items = [
        ("西红柿", "500g", False),
        ("黄瓜", "500g", True),
        ("大白菜", "每颗", False),
    ]
    
    item_y = category_y + 35
    for name, spec, completed in items:
        # 卡片背景
        bg_color = '#E8F5E9' if completed else COLORS['white']  # 完成用浅绿色
        draw_rounded_rect(draw, [40, item_y, PHONE_WIDTH-40, item_y+70], 10, bg_color)
        
        # 商品名称
        draw.text((55, item_y+20), name, fill=COLORS['text'], font=create_font(17, bold=True))
        
        # 规格和状态
        status = "  ✓ 已完成" if completed else ""
        draw.text((55, item_y+45), f"蔬菜  |  {spec}{status}", 
                  fill=COLORS['success'] if completed else COLORS['text_secondary'], 
                  font=create_font(14))
        
        item_y += 80
    
    # 类别标题 - 肉类
    item_y += 10
    draw.text((40, item_y), "▶ 肉类", fill=COLORS['text'], font=create_font(16, bold=True))
    
    meat_items = [
        ("猪五花肉", "500g", False),
        ("鸡胸肉", "500g", False),
    ]
    
    item_y += 35
    for name, spec, completed in meat_items:
        bg_color = '#E8F5E9' if completed else COLORS['white']
        draw_rounded_rect(draw, [40, item_y, PHONE_WIDTH-40, item_y+70], 10, bg_color)
        draw.text((55, item_y+20), name, fill=COLORS['text'], font=create_font(17, bold=True))
        draw.text((55, item_y+45), f"肉类  |  {spec}", fill=COLORS['text_secondary'], font=create_font(14))
        item_y += 80
    
    # 类别标题 - 水果
    item_y += 10
    draw.text((40, item_y), "▶ 水果", fill=COLORS['text'], font=create_font(16, bold=True))
    
    return img


def create_survey_screen():
    """创建调研填写页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    # 手机外框
    draw_phone_frame(draw)
    
    # 顶部状态栏
    draw.rectangle([25, 25, PHONE_WIDTH-25, 85], fill=COLORS['primary'])
    
    # 标题栏
    draw.text((50, 55), "◀", fill=COLORS['white'], font=create_font(24), anchor='lm')
    draw.text((PHONE_WIDTH//2, 55), "填写调研数据", fill=COLORS['white'], font=create_font(18, bold=True), anchor='mm')
    
    content_y = 100
    
    # 商品信息卡片
    draw_rounded_rect(draw, [35, content_y, PHONE_WIDTH-35, content_y+90], 12, COLORS['white'])
    draw.text((50, content_y+25), "黄瓜", fill=COLORS['text'], font=create_font(22, bold=True))
    draw.text((50, content_y+60), "蔬菜  |  500g", fill=COLORS['text_secondary'], font=create_font(15))
    
    content_y += 110
    
    # 表单区域
    # 超市名称
    draw.text((45, content_y), "超市名称 *", fill=COLORS['text'], font=create_font(15))
    draw_rounded_rect(draw, [40, content_y+25, PHONE_WIDTH-40, content_y+70], 8, COLORS['white'], COLORS['divider'])
    draw.text((55, content_y+48), "永辉超市（中关村店）", fill=COLORS['text'], font=create_font(15))
    
    content_y += 90
    
    # 超市地址
    draw.text((45, content_y), "超市地址", fill=COLORS['text'], font=create_font(15))
    draw_rounded_rect(draw, [40, content_y+25, PHONE_WIDTH-40, content_y+70], 8, COLORS['white'], COLORS['divider'])
    draw.text((55, content_y+48), "中关村大街1号", fill=COLORS['text_secondary'], font=create_font(15))
    
    content_y += 90
    
    # 单价
    draw.text((45, content_y), "单价（元） *", fill=COLORS['text'], font=create_font(15))
    draw_rounded_rect(draw, [40, content_y+25, PHONE_WIDTH-40, content_y+70], 8, COLORS['white'], COLORS['divider'])
    draw.text((55, content_y+48), "3.50", fill=COLORS['text'], font=create_font(15))
    
    content_y += 90
    
    # 促销信息
    draw.text((45, content_y), "促销信息", fill=COLORS['text'], font=create_font(15))
    draw_rounded_rect(draw, [40, content_y+25, PHONE_WIDTH-40, content_y+70], 8, COLORS['white'], COLORS['divider'])
    draw.text((55, content_y+48), "买一送一", fill=COLORS['text_secondary'], font=create_font(15))
    
    content_y += 95
    
    # 照片区域
    draw.text((45, content_y), "商品照片", fill=COLORS['text'], font=create_font(15))
    content_y += 30
    
    # 照片预览框
    draw_rounded_rect(draw, [40, content_y, 140, content_y+100], 8, '#E8E8E8')
    draw.text((90, content_y+50), "📷", fill=COLORS['text_secondary'], font=create_font(40), anchor='mm')
    
    # 拍照按钮
    draw_rounded_rect(draw, [160, content_y+10, 280, content_y+50], 6, COLORS['primary'])
    draw.text((220, content_y+30), "📷 拍照", fill=COLORS['white'], font=create_font(14), anchor='mm')
    
    draw_rounded_rect(draw, [160, content_y+60, 280, content_y+95], 6, COLORS['white'], COLORS['divider'])
    draw.text((220, content_y+78), "🖼 选择照片", fill=COLORS['text_secondary'], font=create_font(14), anchor='mm')
    
    content_y += 130
    
    # 提交按钮
    draw_rounded_rect(draw, [40, content_y, PHONE_WIDTH-40, content_y+55], 8, COLORS['primary'])
    draw.text((PHONE_WIDTH//2, content_y+28), "提交调研数据", fill=COLORS['white'], font=create_font(17, bold=True), anchor='mm')
    
    return img


def main():
    """生成所有预览图"""
    output_dir = "preview_images"
    os.makedirs(output_dir, exist_ok=True)
    
    print("正在生成移动端界面预览图...")
    
    # 生成登录页面
    login_img = create_login_screen()
    login_img.save(f"{output_dir}/01_login_screen.png")
    print("✓ 登录页面已生成")
    
    # 生成任务列表页面
    task_img = create_task_screen()
    task_img.save(f"{output_dir}/02_task_list_screen.png")
    print("✓ 任务列表页面已生成")
    
    # 生成调研填写页面
    survey_img = create_survey_screen()
    survey_img.save(f"{output_dir}/03_survey_form_screen.png")
    print("✓ 调研填写页面已生成")
    
    print(f"\n所有预览图已保存到 {output_dir}/ 目录")


if __name__ == "__main__":
    main()

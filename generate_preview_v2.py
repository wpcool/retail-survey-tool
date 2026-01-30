#!/usr/bin/env python3
"""
生成移动端App界面预览图 - 优化版
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 颜色配置
COLORS = {
    'primary': '#1976D2',
    'primary_dark': '#1565C0',
    'accent': '#FF5722',
    'background': '#F5F5F5',
    'white': '#FFFFFF',
    'text': '#333333',
    'text_secondary': '#666666',
    'text_hint': '#999999',
    'divider': '#E0E0E0',
    'success': '#4CAF50',
    'success_bg': '#E8F5E9',
    'card_bg': '#FFFFFF',
}

PHONE_WIDTH = 400
PHONE_HEIGHT = 850


def get_font(size, bold=False):
    """获取字体 - 尝试多种方式"""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    return ImageFont.load_default()


def draw_phone_shell(draw):
    """绘制手机外壳"""
    # 外框
    draw.rounded_rectangle([8, 8, PHONE_WIDTH-8, PHONE_HEIGHT-8], radius=45, 
                          outline='#2a2a2a', width=10, fill='#1a1a1a')
    # 屏幕
    draw.rounded_rectangle([25, 25, PHONE_WIDTH-25, PHONE_HEIGHT-25], radius=35, 
                          fill=COLORS['background'])
    # 灵动岛
    draw.rounded_rectangle([PHONE_WIDTH//2-65, 32, PHONE_WIDTH//2+65, 58], radius=16, fill='#1a1a1a')


def create_login():
    """登录页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    draw_phone_shell(draw)
    
    top = 90
    
    # 图标
    draw.rounded_rectangle([PHONE_WIDTH//2-40, top, PHONE_WIDTH//2+40, top+80], radius=20, fill=COLORS['primary'])
    draw.text((PHONE_WIDTH//2, top+45), "R", fill=COLORS['white'], font=get_font(40, True), anchor='mm')
    
    # 标题
    draw.text((PHONE_WIDTH//2, top+110), "Retail Survey", fill=COLORS['primary'], font=get_font(28, True), anchor='mm')
    draw.text((PHONE_WIDTH//2, top+145), "Staff Login", fill=COLORS['text_secondary'], font=get_font(16), anchor='mm')
    
    # 输入框
    y = top + 220
    # 用户名
    draw_rounded_rect(draw, [45, y, PHONE_WIDTH-45, y+55], 10, COLORS['white'], COLORS['divider'])
    draw.text((60, y+28), "[User Icon]  Username", fill=COLORS['text_secondary'], font=get_font(15), anchor='lm')
    
    # 密码
    y2 = y + 75
    draw_rounded_rect(draw, [45, y2, PHONE_WIDTH-45, y2+55], 10, COLORS['white'], COLORS['divider'])
    draw.text((60, y2+28), "[Lock Icon]  Password", fill=COLORS['text_secondary'], font=get_font(15), anchor='lm')
    draw.text((PHONE_WIDTH-70, y2+28), "******", fill=COLORS['text'], font=get_font(15), anchor='lm')
    
    # 登录按钮
    btn_y = y2 + 90
    draw_rounded_rect(draw, [45, btn_y, PHONE_WIDTH-45, btn_y+55], 10, COLORS['primary'])
    draw.text((PHONE_WIDTH//2, btn_y+28), "LOGIN", fill=COLORS['white'], font=get_font(18, True), anchor='mm')
    
    # 提示
    draw.text((PHONE_WIDTH//2, PHONE_HEIGHT-140), "Test: test / 123456", 
              fill=COLORS['text_hint'], font=get_font(14), anchor='mm')
    
    return img


def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    """绘制圆角矩形"""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def create_task_list():
    """任务列表页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_phone_shell(draw)
    
    # 顶部栏
    draw.rectangle([25, 25, PHONE_WIDTH-25, 88], fill=COLORS['primary'])
    draw.text((PHONE_WIDTH//2, 57), "Today's Tasks", fill=COLORS['white'], font=get_font(18, True), anchor='mm')
    draw.text((PHONE_WIDTH-55, 57), "[R]", fill=COLORS['white'], font=get_font(18), anchor='mm')
    
    # 任务卡片
    card_y = 105
    draw_rounded_rect(draw, [38, card_y, PHONE_WIDTH-38, card_y+105], 14, COLORS['white'])
    
    draw.text((55, card_y+22), "2024-01-30 Fresh Produce Survey", fill=COLORS['text'], font=get_font(15, True))
    draw.text((55, card_y+50), "Survey prices at nearby supermarkets", fill=COLORS['text_secondary'], font=get_font(13))
    
    # 进度
    draw.text((55, card_y+80), "Progress: 3/8  38% Complete", fill=COLORS['primary'], font=get_font(14, True))
    
    # 类别 - Vegetables
    y = card_y + 125
    draw.text((42, y), "[Category] Vegetables", fill=COLORS['text'], font=get_font(15, True))
    
    items = [
        ("Tomato", "500g", "Vegetables", False),
        ("Cucumber", "500g", "Vegetables", True),
        ("Chinese Cabbage", "Each", "Vegetables", False),
    ]
    
    item_y = y + 35
    for name, spec, cat, done in items:
        bg = COLORS['success_bg'] if done else COLORS['white']
        draw_rounded_rect(draw, [42, item_y, PHONE_WIDTH-42, item_y+75], 12, bg)
        
        draw.text((57, item_y+18), name, fill=COLORS['text'], font=get_font(16, True))
        
        status = "  [Done]" if done else ""
        color = COLORS['success'] if done else COLORS['text_secondary']
        draw.text((57, item_y+48), f"{cat}  |  {spec}{status}", fill=color, font=get_font(13))
        
        item_y += 85
    
    # 类别 - Meat
    item_y += 5
    draw.text((42, item_y), "[Category] Meat", fill=COLORS['text'], font=get_font(15, True))
    
    meat_items = [("Pork Belly", "500g", "Meat"), ("Chicken Breast", "500g", "Meat")]
    item_y += 35
    for name, spec, cat in meat_items:
        draw_rounded_rect(draw, [42, item_y, PHONE_WIDTH-42, item_y+75], 12, COLORS['white'])
        draw.text((57, item_y+18), name, fill=COLORS['text'], font=get_font(16, True))
        draw.text((57, item_y+48), f"{cat}  |  {spec}", fill=COLORS['text_secondary'], font=get_font(13))
        item_y += 85
    
    # 类别 - Fruit
    item_y += 5
    draw.text((42, item_y), "[Category] Fruit", fill=COLORS['text'], font=get_font(15, True))
    
    return img


def create_survey_form():
    """调研填写页面"""
    img = Image.new('RGB', (PHONE_WIDTH, PHONE_HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    draw_phone_shell(draw)
    
    # 顶部栏
    draw.rectangle([25, 25, PHONE_WIDTH-25, 88], fill=COLORS['primary'])
    draw.text((50, 57), "<", fill=COLORS['white'], font=get_font(28), anchor='lm')
    draw.text((PHONE_WIDTH//2, 57), "Enter Survey Data", fill=COLORS['white'], font=get_font(17, True), anchor='mm')
    
    y = 105
    
    # 商品卡片
    draw_rounded_rect(draw, [38, y, PHONE_WIDTH-38, y+95], 14, COLORS['white'])
    draw.text((53, y+22), "Cucumber", fill=COLORS['text'], font=get_font(22, True))
    draw.text((53, y+60), "Vegetables  |  500g", fill=COLORS['text_secondary'], font=get_font(15))
    
    y += 115
    
    # 表单字段
    fields = [
        ("Supermarket Name *", "Yonghui Supermarket (Zhongguancun)"),
        ("Address", "No.1 Zhongguancun Street"),
        ("Price (CNY) *", "3.50"),
        ("Promotion Info", "Buy 1 Get 1 Free"),
    ]
    
    for label, value in fields:
        draw.text((45, y), label, fill=COLORS['text'], font=get_font(14))
        draw_rounded_rect(draw, [40, y+25, PHONE_WIDTH-40, y+72], 10, COLORS['white'], COLORS['divider'])
        color = COLORS['text'] if value else COLORS['text_hint']
        draw.text((55, y+49), value or "Optional", fill=color, font=get_font(15))
        y += 95
    
    # 照片区域
    draw.text((45, y), "Product Photo", fill=COLORS['text'], font=get_font(14))
    y += 30
    
    # 照片预览框
    draw_rounded_rect(draw, [40, y, 150, y+110], 12, '#EEEEEE')
    draw.text((95, y+55), "[Camera Icon]", fill=COLORS['text_hint'], font=get_font(14), anchor='mm')
    
    # 按钮
    draw_rounded_rect(draw, [170, y+10, 330, y+55], 8, COLORS['primary'])
    draw.text((250, y+33), "[Cam] Take Photo", fill=COLORS['white'], font=get_font(14), anchor='mm')
    
    draw_rounded_rect(draw, [170, y+65, 330, y+105], 8, COLORS['white'], COLORS['divider'])
    draw.text((250, y+85), "[Img] Gallery", fill=COLORS['text_secondary'], font=get_font(14), anchor='mm')
    
    y += 140
    
    # 提交按钮
    draw_rounded_rect(draw, [40, y, PHONE_WIDTH-40, y+58], 10, COLORS['primary'])
    draw.text((PHONE_WIDTH//2, y+30), "Submit Survey Data", fill=COLORS['white'], font=get_font(17, True), anchor='mm')
    
    return img


def main():
    out_dir = "preview_images"
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating preview images...")
    
    create_login().save(f"{out_dir}/01_login.png")
    print(" Login screen")
    
    create_task_list().save(f"{out_dir}/02_task_list.png")
    print(" Task list screen")
    
    create_survey_form().save(f"{out_dir}/03_survey_form.png")
    print(" Survey form screen")
    
    print(f"\nSaved to {out_dir}/")


if __name__ == "__main__":
    main()

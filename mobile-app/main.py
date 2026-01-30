"""
零售市场调研工具 - Kivy移动应用 (简化版，支持中文)
使用原生Kivy组件，字体支持更可靠
"""
import os
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle

import json
from datetime import datetime

from config import APP_NAME, DATA_DIR
from api_client import api

# 注册中文字体
chinese_fonts = [
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
]

CHINESE_FONT = None
for font_path in chinese_fonts:
    if os.path.exists(font_path):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=font_path)
            CHINESE_FONT = 'ChineseFont'
            print(f"成功加载字体: {font_path}")
            break
        except Exception as e:
            print(f"字体加载失败 {font_path}: {e}")

if not CHINESE_FONT:
    CHINESE_FONT = 'Arial'  # 备用字体

# 设置窗口大小
Window.size = (400, 700)
os.makedirs(DATA_DIR, exist_ok=True)


class StyledLabel(Label):
    """带中文字体的标签"""
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', CHINESE_FONT)
        kwargs.setdefault('color', (0.2, 0.2, 0.2, 1))
        super().__init__(**kwargs)


class StyledButton(Button):
    """带中文字体的按钮"""
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', CHINESE_FONT)
        kwargs.setdefault('background_color', (0.1, 0.46, 0.82, 1))  # 蓝色
        kwargs.setdefault('color', (1, 1, 1, 1))
        super().__init__(**kwargs)


class StyledTextInput(TextInput):
    """带中文字体的输入框"""
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', CHINESE_FONT)
        super().__init__(**kwargs)


class LoginScreen(Screen):
    """登录页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # 标题
        title = StyledLabel(
            text=APP_NAME,
            font_size='24sp',
            size_hint_y=0.3,
            bold=True,
            color=(0.1, 0.46, 0.82, 1)
        )
        layout.add_widget(title)
        
        subtitle = StyledLabel(
            text="调研人员登录",
            font_size='16sp',
            size_hint_y=0.1,
            color=(0.4, 0.4, 0.4, 1)
        )
        layout.add_widget(subtitle)
        
        # 表单区域
        form_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.4)
        
        self.username_input = StyledTextInput(
            hint_text='用户名',
            multiline=False,
            size_hint_y=None,
            height=50,
            padding=[10, 10]
        )
        form_layout.add_widget(self.username_input)
        
        self.password_input = StyledTextInput(
            hint_text='密码',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50,
            padding=[10, 10]
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # 登录按钮
        login_btn = StyledButton(
            text='登录',
            size_hint=(1, None),
            height=50,
            on_press=self.do_login
        )
        layout.add_widget(login_btn)
        
        # 提示
        hint = StyledLabel(
            text="测试账号: test / 123456",
            font_size='12sp',
            size_hint_y=0.1,
            color=(0.6, 0.6, 0.6, 1)
        )
        layout.add_widget(hint)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_popup("错误", "请输入用户名和密码")
            return
        
        # 调试信息
        print(f"正在登录: {username}")
        print(f"API地址: {api.base_url}")
        
        result = api.login(username, password)
        
        # 打印完整响应
        print(f"登录响应: {result}")
        
        if result.get("success"):
            app = App.get_running_app()
            app.user_id = result.get("user_id")
            app.user_name = result.get("name")
            self.save_user_info(app.user_id, app.user_name)
            self.show_popup("成功", f"欢迎，{app.user_name}！")
            self.manager.current = 'task'
        else:
            error_msg = result.get("message", "登录失败")
            print(f"登录错误: {error_msg}")
            self.show_popup("错误", error_msg)
    
    def save_user_info(self, user_id, user_name):
        data = {
            "user_id": user_id,
            "user_name": user_name,
            "login_time": datetime.now().isoformat()
        }
        with open(f"{DATA_DIR}/user.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=StyledLabel(text=message),
            size_hint=(None, None),
            size=(300, 200),
            title_font=CHINESE_FONT
        )
        popup.open()


class TaskScreen(Screen):
    """任务列表页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_data = None
        self.completed_items = []
        self.build_ui()
    
    def build_ui(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # 顶部栏
        header = BoxLayout(size_hint_y=None, height=60, padding=10)
        with header.canvas.before:
            Color(0.1, 0.46, 0.82, 1)
            Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header_bg, size=self.update_header_bg)
        
        title = StyledLabel(
            text="今日调研任务",
            font_size='18sp',
            color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(title)
        
        self.layout.add_widget(header)
        
        # 任务信息
        self.info_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=15)
        self.task_title = StyledLabel(text="加载中...", font_size='16sp', bold=True)
        self.task_desc = StyledLabel(text="", font_size='13sp', color=(0.5, 0.5, 0.5, 1))
        self.progress_label = StyledLabel(text="", font_size='13sp', color=(0.1, 0.46, 0.82, 1))
        
        self.info_layout.add_widget(self.task_title)
        self.info_layout.add_widget(self.task_desc)
        self.info_layout.add_widget(self.progress_label)
        self.layout.add_widget(self.info_layout)
        
        # 任务列表
        self.scroll_view = ScrollView()
        self.items_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.items_list.bind(minimum_height=self.items_list.setter('height'))
        self.scroll_view.add_widget(self.items_list)
        self.layout.add_widget(self.scroll_view)
        
        # 刷新按钮
        refresh_btn = StyledButton(
            text='刷新任务',
            size_hint=(1, None),
            height=50,
            on_press=self.refresh_task
        )
        self.layout.add_widget(refresh_btn)
        
        self.add_widget(self.layout)
    
    def update_header_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.1, 0.46, 0.82, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def on_enter(self):
        self.load_task()
    
    def load_task(self):
        app = App.get_running_app()
        if not app.user_id:
            self.manager.current = 'login'
            return
        
        self.task_title.text = "加载中..."
        self.items_list.clear_widgets()
        
        task = api.get_today_task(app.user_id)
        
        if "error" in task:
            self.task_title.text = "获取任务失败"
            self.task_desc.text = task.get("error", "请检查网络连接")
            return
        
        if "id" not in task:
            self.task_title.text = "今日暂无调研任务"
            self.task_desc.text = "请稍后再试或联系管理员"
            return
        
        self.task_data = task
        self.task_title.text = task.get("title", "")
        self.task_desc.text = task.get("description", "") or "请点击下方品类进行调研"
        
        records = api.get_today_records(app.user_id)
        self.completed_items = records.get("completed_item_ids", [])
        
        total = len(task.get("items", []))
        completed = len(self.completed_items)
        self.progress_label.text = f"进度: {completed}/{total}  已完成 {completed/total*100:.0f}%" if total > 0 else ""
        
        # 按类别分组
        current_category = None
        for item in sorted(task.get("items", []), key=lambda x: (x.get("category", ""), x.get("sort_order", 0))):
            category = item.get("category", "未分类")
            
            if category != current_category:
                current_category = category
                cat_label = StyledLabel(
                    text=f"▶ {category}",
                    font_size='15sp',
                    bold=True,
                    size_hint_y=None,
                    height=40,
                    color=(0.1, 0.46, 0.82, 1)
                )
                self.items_list.add_widget(cat_label)
            
            is_completed = item.get("id") in self.completed_items
            btn_color = (0.85, 0.95, 0.85, 1) if is_completed else (1, 1, 1, 1)
            status_text = "  ✓ 已完成" if is_completed else ""
            
            item_btn = Button(
                text=f"{item.get('product_name', '')}\n{item.get('category', '')}  |  {item.get('product_spec', '')}{status_text}",
                font_name=CHINESE_FONT,
                font_size='14sp',
                size_hint_y=None,
                height=70,
                background_color=btn_color,
                color=(0.2, 0.6, 0.2, 1) if is_completed else (0.2, 0.2, 0.2, 1),
                halign='left',
                valign='middle',
                padding_x=10
            )
            item_btn.bind(on_press=lambda btn, i=item: self.on_item_click(i))
            self.items_list.add_widget(item_btn)
    
    def on_item_click(self, item_data):
        app = App.get_running_app()
        app.current_item = item_data
        
        survey_screen = self.manager.get_screen('survey')
        survey_screen.set_item(item_data)
        self.manager.current = 'survey'
    
    def refresh_task(self, instance):
        self.load_task()
        self.show_popup("提示", "任务已刷新")
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=StyledLabel(text=message),
            size_hint=(None, None),
            size=(300, 200),
            title_font=CHINESE_FONT
        )
        popup.open()


class SurveyScreen(Screen):
    """调研填写页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.photo_path = None
        self.build_ui()
    
    def build_ui(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # 顶部栏
        header = BoxLayout(size_hint_y=None, height=60, padding=10)
        with header.canvas.before:
            Color(0.1, 0.46, 0.82, 1)
            Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self.update_header_bg, size=self.update_header_bg)
        
        back_btn = StyledButton(
            text='< 返回',
            size_hint=(None, 1),
            width=80,
            background_color=(0, 0, 0, 0),
            on_press=self.go_back
        )
        header.add_widget(back_btn)
        
        title = StyledLabel(
            text="填写调研数据",
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        self.layout.add_widget(header)
        
        # 滚动区域
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 商品信息卡片
        self.info_card = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=15)
        with self.info_card.canvas.before:
            Color(1, 1, 1, 1)
        self.info_card.bind(pos=self.update_card_bg, size=self.update_card_bg)
        
        self.product_name = StyledLabel(text="", font_size='18sp', bold=True)
        self.product_info = StyledLabel(text="", font_size='13sp', color=(0.5, 0.5, 0.5, 1))
        self.info_card.add_widget(self.product_name)
        self.info_card.add_widget(self.product_info)
        form_layout.add_widget(self.info_card)
        
        # 表单字段
        form_layout.add_widget(StyledLabel(text="超市名称 *", font_size='14sp', size_hint_y=None, height=25))
        self.store_input = StyledTextInput(hint_text='请输入超市名称', multiline=False, size_hint_y=None, height=45)
        form_layout.add_widget(self.store_input)
        
        form_layout.add_widget(StyledLabel(text="超市地址", font_size='14sp', size_hint_y=None, height=25))
        self.address_input = StyledTextInput(hint_text='选填', multiline=False, size_hint_y=None, height=45)
        form_layout.add_widget(self.address_input)
        
        form_layout.add_widget(StyledLabel(text="单价（元）*", font_size='14sp', size_hint_y=None, height=25))
        self.price_input = StyledTextInput(hint_text='0.00', multiline=False, input_filter='float', size_hint_y=None, height=45)
        form_layout.add_widget(self.price_input)
        
        form_layout.add_widget(StyledLabel(text="促销信息", font_size='14sp', size_hint_y=None, height=25))
        self.promo_input = StyledTextInput(hint_text='选填，如：买一送一', multiline=False, size_hint_y=None, height=45)
        form_layout.add_widget(self.promo_input)
        
        form_layout.add_widget(StyledLabel(text="备注", font_size='14sp', size_hint_y=None, height=25))
        self.remark_input = StyledTextInput(hint_text='选填', multiline=True, size_hint_y=None, height=80)
        form_layout.add_widget(self.remark_input)
        
        # 照片区域
        form_layout.add_widget(StyledLabel(text="商品照片", font_size='14sp', size_hint_y=None, height=25))
        
        photo_layout = BoxLayout(size_hint_y=None, height=120, spacing=10)
        self.photo_preview = Image(source='', size_hint=(None, 1), width=120, allow_stretch=True)
        photo_layout.add_widget(self.photo_preview)
        
        photo_btns = BoxLayout(orientation='vertical', spacing=10)
        photo_btns.add_widget(StyledButton(text='拍照', on_press=self.take_photo))
        photo_btns.add_widget(StyledButton(text='选择照片', background_color=(0.7, 0.7, 0.7, 1), on_press=self.select_photo))
        photo_layout.add_widget(photo_btns)
        
        form_layout.add_widget(photo_layout)
        
        # 提交按钮
        form_layout.add_widget(StyledButton(
            text='提交调研数据',
            size_hint=(1, None),
            height=50,
            on_press=self.submit_data
        ))
        
        scroll.add_widget(form_layout)
        self.layout.add_widget(scroll)
        
        self.add_widget(self.layout)
    
    def update_header_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.1, 0.46, 0.82, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def set_item(self, item_data):
        self.item_data = item_data
        self.product_name.text = item_data.get('product_name', '')
        self.product_info.text = f"{item_data.get('category', '')}  |  {item_data.get('product_spec', '')}"
        
        self.store_input.text = ""
        self.address_input.text = ""
        self.price_input.text = ""
        self.promo_input.text = ""
        self.remark_input.text = ""
        self.photo_path = None
        self.photo_preview.source = ""
    
    def go_back(self, instance):
        self.manager.current = 'task'
    
    def take_photo(self, instance):
        self.show_popup("提示", "请在下方输入照片路径")
    
    def select_photo(self, instance):
        self.show_popup("提示", "请在下方输入照片路径")
    
    def submit_data(self, instance):
        app = App.get_running_app()
        
        store_name = self.store_input.text.strip()
        price_text = self.price_input.text.strip()
        
        if not store_name:
            self.show_popup("错误", "请输入超市名称")
            return
        
        if not price_text:
            self.show_popup("错误", "请输入单价")
            return
        
        try:
            price = float(price_text)
        except ValueError:
            self.show_popup("错误", "单价格式不正确")
            return
        
        data = {
            "item_id": self.item_data.get("id"),
            "surveyor_id": app.user_id,
            "store_name": store_name,
            "store_address": self.address_input.text.strip(),
            "price": price,
            "promotion_info": self.promo_input.text.strip(),
            "remark": self.remark_input.text.strip(),
            "latitude": None,
            "longitude": None
        }
        
        result = api.submit_record(data, self.photo_path)
        
        if result.get("success"):
            self.show_popup("成功", "提交成功！")
            self.go_back(None)
        else:
            self.show_popup("错误", f"提交失败: {result.get('message', '未知错误')}")
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=StyledLabel(text=message),
            size_hint=(None, None),
            size=(300, 200),
            title_font=CHINESE_FONT
        )
        popup.open()


class MainApp(App):
    """应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None
        self.user_name = None
        self.current_item = None
    
    def build(self):
        self.load_user_info()
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(SurveyScreen(name='survey'))
        
        if self.user_id:
            sm.current = 'task'
        
        return sm
    
    def load_user_info(self):
        try:
            with open(f"{DATA_DIR}/user.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_id = data.get("user_id")
                self.user_name = data.get("user_name")
        except:
            pass


if __name__ == '__main__':
    MainApp().run()

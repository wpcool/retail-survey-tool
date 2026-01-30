"""
零售市场调研工具 - Kivy移动应用
"""
import os
os.environ['KIVY_NO_FILELOG'] = '1'

# ========== 1. 首先配置中文字体（必须在导入kivymd组件之前） ==========
from kivy.core.text import LabelBase

# 尝试注册macOS自带的中文字体
chinese_fonts = [
    '/System/Library/Fonts/PingFang.ttc',  # 苹方字体
    '/System/Library/Fonts/STHeiti Light.ttc',  # 黑体
    '/System/Library/Fonts/Hiragino Sans GB.ttc',  # 冬青黑体
    '/System/Library/Fonts/Arial.ttf',  # 备用
]

font_path = None
for f in chinese_fonts:
    if os.path.exists(f):
        font_path = f
        break

if font_path:
    LabelBase.register(name='ChineseFont', fn_regular=font_path)
    print(f"已加载中文字体: {font_path}")
else:
    print("警告：未找到中文字体，将使用默认字体")

# ========== 2. 应用字体补丁（在导入kivymd组件前） ==========
if font_path:
    # 先导入需要用到的类
    from kivymd.uix.label import MDLabel
    from kivymd.uix.textfield import MDTextField  
    from kivymd.uix.button import BaseButton, MDRaisedButton, MDFlatButton
    
    # 保存原始方法
    _original_label_init = MDLabel.__init__
    _original_textfield_init = MDTextField.__init__
    _original_button_init = BaseButton.__init__
    _original_raised_init = MDRaisedButton.__init__
    _original_flat_init = MDFlatButton.__init__
    
    # 定义新方法来设置默认字体
    def _new_label_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', 'ChineseFont')
        _original_label_init(self, *args, **kwargs)
    
    def _new_textfield_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', 'ChineseFont')
        _original_textfield_init(self, *args, **kwargs)
    
    def _new_button_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', 'ChineseFont')
        _original_button_init(self, *args, **kwargs)
    
    def _new_raised_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', 'ChineseFont')
        _original_raised_init(self, *args, **kwargs)
    
    def _new_flat_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', 'ChineseFont')
        _original_flat_init(self, *args, **kwargs)
    
    # 应用猴子补丁
    MDLabel.__init__ = _new_label_init
    MDTextField.__init__ = _new_textfield_init
    BaseButton.__init__ = _new_button_init
    MDRaisedButton.__init__ = _new_raised_init
    MDFlatButton.__init__ = _new_flat_init

# ========== 3. 导入其他组件 ==========
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
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

import json
from datetime import datetime

from config import APP_NAME, DATA_DIR
from api_client import api

# 设置窗口大小（开发时使用）
Window.size = (400, 700)

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


class LoginScreen(MDScreen):
    """登录页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # 标题
        layout.add_widget(MDLabel(
            text=APP_NAME,
            halign='center',
            font_style='H4',
            size_hint_y=0.3
        ))
        
        layout.add_widget(MDLabel(
            text="调研人员登录",
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=0.1
        ))
        
        # 表单区域
        form_layout = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=0.4)
        
        self.username_input = MDTextField(
            hint_text='用户名',
            icon_right='account',
            mode='rectangle'
        )
        form_layout.add_widget(self.username_input)
        
        self.password_input = MDTextField(
            hint_text='密码',
            icon_right='lock',
            password=True,
            mode='rectangle'
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # 登录按钮
        layout.add_widget(MDRaisedButton(
            text='登录',
            size_hint=(1, None),
            height=50,
            on_release=self.do_login
        ))
        
        # 版本信息
        layout.add_widget(MDLabel(
            text="测试账号: test / 123456",
            halign='center',
            theme_text_color='Hint',
            size_hint_y=0.1
        ))
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_error("请输入用户名和密码")
            return
        
        # 调用登录API
        result = api.login(username, password)
        
        if result.get("success"):
            # 保存用户信息
            app = MDApp.get_running_app()
            app.user_id = result.get("user_id")
            app.user_name = result.get("name")
            
            # 保存到本地
            self.save_user_info(app.user_id, app.user_name)
            
            self.show_success(f"欢迎，{app.user_name}！")
            self.manager.current = 'task'
        else:
            self.show_error(result.get("message", "登录失败"))
    
    def save_user_info(self, user_id, user_name):
        """保存用户信息到本地"""
        data = {
            "user_id": user_id,
            "user_name": user_name,
            "login_time": datetime.now().isoformat()
        }
        with open(f"{DATA_DIR}/user.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
    
    def show_error(self, message):
        Snackbar(text=message, bg_color=(0.8, 0.2, 0.2, 1)).open()
    
    def show_success(self, message):
        Snackbar(text=message, bg_color=(0.2, 0.8, 0.2, 1)).open()


class TaskItemCard(MDCard):
    """任务项卡片"""
    
    def __init__(self, item_data, is_completed=False, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.item_data = item_data
        self.on_click_callback = on_click
        self.is_completed = is_completed
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 5
        self.elevation = 2
        
        # 根据完成状态设置颜色
        if is_completed:
            self.md_bg_color = (0.85, 0.95, 0.85, 1)  # 浅绿色
        else:
            self.md_bg_color = (1, 1, 1, 1)
        
        # 商品名称
        self.add_widget(MDLabel(
            text=item_data.get('product_name', ''),
            font_style='H6',
            size_hint_y=0.5
        ))
        
        # 类别和规格
        info_text = f"{item_data.get('category', '')}  |  {item_data.get('product_spec', '')}"
        if is_completed:
            info_text += "  ✓ 已完成"
        
        self.add_widget(MDLabel(
            text=info_text,
            theme_text_color='Secondary',
            size_hint_y=0.5
        ))
        
        self.bind(on_release=self.on_card_click)
    
    def on_card_click(self, instance):
        if self.on_click_callback:
            self.on_click_callback(self.item_data, self.is_completed)


class TaskScreen(MDScreen):
    """任务列表页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_data = None
        self.completed_items = []
        self.build_ui()
    
    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical')
        
        # 顶部工具栏
        self.toolbar = MDTopAppBar(
            title="今日调研任务",
            elevation=10,
            right_action_items=[['refresh', self.refresh_task]]
        )
        self.layout.add_widget(self.toolbar)
        
        # 任务信息区域
        self.info_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            padding=15
        )
        self.task_title = MDLabel(
            text="加载中...",
            font_style='H6'
        )
        self.task_desc = MDLabel(
            text="",
            theme_text_color='Secondary'
        )
        self.progress_label = MDLabel(
            text="",
            theme_text_color='Primary'
        )
        
        self.info_layout.add_widget(self.task_title)
        self.info_layout.add_widget(self.task_desc)
        self.info_layout.add_widget(self.progress_label)
        self.layout.add_widget(self.info_layout)
        
        # 任务列表
        self.scroll_view = ScrollView()
        self.items_list = MDList()
        self.scroll_view.add_widget(self.items_list)
        self.layout.add_widget(self.scroll_view)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """进入页面时加载任务"""
        self.load_task()
    
    def load_task(self):
        """加载今日任务"""
        app = MDApp.get_running_app()
        if not app.user_id:
            self.manager.current = 'login'
            return
        
        self.task_title.text = "加载中..."
        self.items_list.clear_widgets()
        
        # 获取今日任务
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
        
        # 获取已完成的项目
        records = api.get_today_records(app.user_id)
        self.completed_items = records.get("completed_item_ids", [])
        
        # 更新进度
        total = len(task.get("items", []))
        completed = len(self.completed_items)
        self.progress_label.text = f"进度: {completed}/{total}  已完成 {completed/total*100:.0f}%" if total > 0 else ""
        
        # 按类别分组显示
        current_category = None
        for item in sorted(task.get("items", []), key=lambda x: (x.get("category", ""), x.get("sort_order", 0))):
            category = item.get("category", "未分类")
            
            # 显示类别标题
            if category != current_category:
                current_category = category
                category_label = MDLabel(
                    text=f"▶ {category}",
                    font_style='Subtitle1',
                    size_hint_y=None,
                    height=40,
                    theme_text_color='Primary',
                    bold=True
                )
                self.items_list.add_widget(category_label)
            
            # 添加任务项卡片
            is_completed = item.get("id") in self.completed_items
            card = TaskItemCard(
                item_data=item,
                is_completed=is_completed,
                on_click=self.on_item_click
            )
            self.items_list.add_widget(card)
    
    def on_item_click(self, item_data, is_completed):
        """点击任务项"""
        app = MDApp.get_running_app()
        app.current_item = item_data
        
        # 跳转到填写页面
        survey_screen = self.manager.get_screen('survey')
        survey_screen.set_item(item_data, is_completed)
        self.manager.current = 'survey'
    
    def refresh_task(self, instance):
        """刷新任务"""
        self.load_task()
        Snackbar(text="任务已刷新").open()


class SurveyScreen(MDScreen):
    """调研填写页面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.photo_path = None
        self.build_ui()
    
    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical')
        
        # 顶部工具栏
        self.toolbar = MDTopAppBar(
            title="填写调研数据",
            elevation=10,
            left_action_items=[['arrow-left', self.go_back]]
        )
        self.layout.add_widget(self.toolbar)
        
        # 滚动区域
        scroll = ScrollView()
        form_layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 商品信息卡片
        self.info_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            elevation=2
        )
        self.product_name = MDLabel(text="", font_style='H5')
        self.product_info = MDLabel(text="", theme_text_color='Secondary')
        self.info_card.add_widget(self.product_name)
        self.info_card.add_widget(self.product_info)
        form_layout.add_widget(self.info_card)
        
        # 超市名称
        self.store_input = MDTextField(
            hint_text='超市名称 *',
            mode='rectangle',
            required=True
        )
        form_layout.add_widget(self.store_input)
        
        # 超市地址
        self.address_input = MDTextField(
            hint_text='超市地址（选填）',
            mode='rectangle',
            multiline=True
        )
        form_layout.add_widget(self.address_input)
        
        # 价格
        self.price_input = MDTextField(
            hint_text='单价（元） *',
            mode='rectangle',
            input_filter='float',
            required=True
        )
        form_layout.add_widget(self.price_input)
        
        # 促销信息
        self.promo_input = MDTextField(
            hint_text='促销信息（选填）',
            mode='rectangle'
        )
        form_layout.add_widget(self.promo_input)
        
        # 备注
        self.remark_input = MDTextField(
            hint_text='备注（选填）',
            mode='rectangle',
            multiline=True
        )
        form_layout.add_widget(self.remark_input)
        
        # 照片区域
        form_layout.add_widget(MDLabel(text="商品照片", font_style='Subtitle1'))
        
        self.photo_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=150)
        self.photo_preview = Image(
            source='',
            size_hint=(None, 1),
            width=150,
            allow_stretch=True
        )
        self.photo_layout.add_widget(self.photo_preview)
        
        photo_btn_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        photo_btn_layout.add_widget(MDRaisedButton(
            text='拍照',
            on_release=self.take_photo
        ))
        photo_btn_layout.add_widget(MDFlatButton(
            text='选择照片',
            on_release=self.select_photo
        ))
        self.photo_layout.add_widget(photo_btn_layout)
        
        form_layout.add_widget(self.photo_layout)
        
        # 提交按钮
        form_layout.add_widget(MDRaisedButton(
            text='提交调研数据',
            size_hint=(1, None),
            height=50,
            on_release=self.submit_data
        ))
        
        scroll.add_widget(form_layout)
        self.layout.add_widget(scroll)
        
        self.add_widget(self.layout)
    
    def set_item(self, item_data, is_completed):
        """设置当前调研项"""
        self.item_data = item_data
        self.is_completed = is_completed
        
        self.product_name.text = item_data.get('product_name', '')
        self.product_info.text = f"{item_data.get('category', '')}  |  {item_data.get('product_spec', '')}"
        
        # 如果已完成，显示提示
        if is_completed:
            self.toolbar.title = "修改调研数据"
        else:
            self.toolbar.title = "填写调研数据"
        
        # 清空表单
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
        """拍照（使用相机）"""
        # 注意：在Android上需要使用plyer库调用原生相机
        # 这里简化处理，使用文件选择器
        self.select_photo(instance)
    
    def select_photo(self, instance):
        """选择照片"""
        # 简化版本：提示用户
        Snackbar(text="请在下方输入照片路径，或使用相机拍照").open()
    
    def submit_data(self, instance):
        """提交数据"""
        app = MDApp.get_running_app()
        
        # 验证必填项
        store_name = self.store_input.text.strip()
        price_text = self.price_input.text.strip()
        
        if not store_name:
            Snackbar(text="请输入超市名称", bg_color=(0.8, 0.2, 0.2, 1)).open()
            return
        
        if not price_text:
            Snackbar(text="请输入单价", bg_color=(0.8, 0.2, 0.2, 1)).open()
            return
        
        try:
            price = float(price_text)
        except ValueError:
            Snackbar(text="单价格式不正确", bg_color=(0.8, 0.2, 0.2, 1)).open()
            return
        
        # 准备数据
        data = {
            "item_id": self.item_data.get("id"),
            "surveyor_id": app.user_id,
            "store_name": store_name,
            "store_address": self.address_input.text.strip(),
            "price": price,
            "promotion_info": self.promo_input.text.strip(),
            "remark": self.remark_input.text.strip(),
            "latitude": None,  # 可以集成GPS获取
            "longitude": None
        }
        
        # 提交到服务器
        result = api.submit_record(data, self.photo_path)
        
        if result.get("success"):
            Snackbar(text="提交成功！", bg_color=(0.2, 0.8, 0.2, 1)).open()
            self.go_back(None)
        else:
            Snackbar(text=f"提交失败: {result.get('message', '未知错误')}", 
                    bg_color=(0.8, 0.2, 0.2, 1)).open()


class MainApp(MDApp):
    """应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None
        self.user_name = None
        self.current_item = None
        self.theme_cls.primary_palette = 'Blue'
    
    def build(self):
        # 加载已保存的用户信息
        self.load_user_info()
        
        # 创建屏幕管理器
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(SurveyScreen(name='survey'))
        
        # 如果已登录，直接跳转到任务页面
        if self.user_id:
            sm.current = 'task'
        
        return sm
    
    def load_user_info(self):
        """加载本地保存的用户信息"""
        try:
            with open(f"{DATA_DIR}/user.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_id = data.get("user_id")
                self.user_name = data.get("user_name")
        except:
            pass


if __name__ == '__main__':
    MainApp().run()

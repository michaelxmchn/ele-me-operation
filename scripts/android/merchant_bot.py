#!/usr/bin/env python3
"""
饿了么商家版自动化操作
自动接单、自动回复、自动调价
"""

from .ele_me_adb import ElemeADB
import time
import json
from datetime import datetime

# 配置
ELEME_PACKAGE = "me.ele.merchant"  # 饿了么商家版包名
TAOBAO_PACKAGE = "com.taobao.taobao"  # 淘宝商家版（可能用这个）

class ElemeMerchantBot:
    """饿了么商家版自动机器人"""
    
    def __init__(self):
        self.adb = ElemeADB()
        self.orders = []
        
    def connect(self):
        """连接设备"""
        return self.adb.connect()
    
    def open_eleme(self):
        """打开饿了么商家版"""
        # 尝试多个包名
        for package in [ELEME_PACKAGE, TAOBAO_PACKAGE]:
            self.adb.open_app(package)
            time.sleep(3)
            
            # 检查是否打开成功
            screenshot = self.adb.screenshot("/tmp/check_eleme.png")
            # 这里可以添加图片识别判断是否在订单页面
            
            return True
        return False
    
    def accept_order(self, order_info: dict = None):
        """接单"""
        print("📦 接单...")
        
        # 1. 点击接单按钮 (假设在屏幕中央偏下)
        self.adb.tap(540, 1800)  # 根据实际调整
        
        time.sleep(1)
        
        # 2. 确认接单
        self.adb.tap(540, 1900)
        
        print("✅ 接单成功")
        return True
    
    def reply_customer(self, order_id: str, message: str = "马上出餐，感谢您的支持！"):
        """回复顾客"""
        print(f"💬 回复订单 {order_id}: {message}")
        
        # 点击输入框
        self.adb.tap(540, 1700)
        
        # 输入回复
        self.adb.input_text(message)
        
        # 点击发送
        self.adb.tap(900, 800)
        
        return True
    
    def adjust_price(self, item_name: str, new_price: float):
        """调价（需要先打开商品管理页面）"""
        print(f"💰 调价: {item_name} -> ¥{new_price}")
        
        # 进入商品管理
        self.adb.tap(180, 200)  # 假设商品tab位置
        
        time.sleep(2)
        
        # 搜索商品
        self.adb.tap(540, 150)  # 搜索框
        self.adb.input_text(item_name)
        
        time.sleep(2)
        
        # 点击第一个商品
        self.adb.tap(540, 300)
        
        time.sleep(2)
        
        # 点击价格编辑
        self.adb.tap(540, 500)
        
        time.sleep(1)
        
        # 输入新价格
        self.adb.tap(540, 600)  # 清空旧价格
        self.adb.input_text(str(new_price))
        
        # 保存
        self.adb.tap(900, 800)
        
        print("✅ 调价完成")
        return True
    
    def get_orders(self) -> list:
        """获取订单列表"""
        print("📋 获取订单...")
        
        # 截图分析订单
        self.adb.screenshot("/tmp/orders.png")
        
        # 这里可以添加OCR识别订单
        # 暂时返回空列表
        return []
    
    def run_auto_mode(self):
        """自动模式：持续监控并自动处理"""
        print("🚀 启动自动模式...")
        print("每30秒检查一次订单...")
        
        while True:
            orders = self.get_orders()
            
            for order in orders:
                self.accept_order(order)
                time.sleep(2)
                self.reply_customer(order['id'])
            
            time.sleep(30)


def main():
    """主函数"""
    bot = ElemeMerchantBot()
    
    print("=== 饿了么商家版自动机器人 ===")
    
    if not bot.connect():
        return
    
    print("\n选择模式:")
    print("1. 手动操作")
    print("2. 自动接单")
    print("3. 自动回复")
    print("4. 调价测试")
    
    choice = input("> ").strip()
    
    if choice == "1":
        bot.adb.open_eleme()
        print("已打开饿了么商家版，请手动操作")
    elif choice == "2":
        bot.run_auto_mode()
    elif choice == "3":
        bot.reply_customer("测试订单", "已收到订单，马上为您准备！")
    elif choice == "4":
        bot.adb.open_eleme()
        time.sleep(3)
        bot.adb.screenshot("/tmp/price_test.png")
        print("截图已保存，请手动调价测试")


if __name__ == "__main__":
    main()

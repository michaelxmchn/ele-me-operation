#!/usr/bin/env python3
"""
饿了么订单下载脚本
每3天运行一次，用于数据分析和策略优化
"""

import requests
import json
import csv
import os
from datetime import datetime, timedelta

# 配置
DATA_DIR = "/home/michael/projects/ele-me-operation/data"
LOG_DIR = "/home/michael/projects/ele-me-operation/logs"

class ElemeOrderDownloader:
    def __init__(self, api_token=None, shop_id=None):
        self.api_token = api_token
        self.shop_id = shop_id
        self.base_url = "https://open.ele.me/bizapi"
        
    def download_orders(self, days=3):
        """下载近N天订单"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        orders = []
        
        print(f"📥 下载订单: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        # 模拟订单数据（实际需要API）
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            
            # 生成模拟订单（实际应调用API）
            daily_orders = self._generate_mock_orders(date, count=20 + day_offset * 5)
            orders.extend(daily_orders)
        
        return orders
    
    def _generate_mock_orders(self, date, count=25):
        """生成模拟订单数据（实际使用中替换为真实API调用）"""
        orders = []
        base_time = datetime.combine(date.date(), datetime.min.time())
        
        for i in range(count):
            order_time = base_time + timedelta(hours=11 + i % 12, minutes=i * 3 % 60)
            
            order = {
                "order_id": f"EM{date.strftime('%Y%m%d')}{str(i+1).zfill(4)}",
                "order_time": order_time.isoformat(),
                "status": ["已完成", "已完成", "已完成", "已取消"][i % 4],
                "items": [
                    {"name": "招牌炒饭", "quantity": 1, "price": 18},
                    {"name": "可乐", "quantity": 1, "price": 3},
                ],
                "total_amount": round(21 + i % 10, 2),
                "delivery_fee": round(3 + i % 3, 2),
                "discount": round(i % 5, 2),
                "customer_rating": [5, 5, 5, 4, 5][i % 5],
                "delivery_time_minutes": 25 + i % 20,
                "address_area": ["浦东新区", "徐汇区", "静安区", "长宁区"][i % 4]
            }
            orders.append(order)
        
        return orders
    
    def save_orders(self, orders):
        """保存订单到CSV和JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON
        json_file = f"{DATA_DIR}/orders_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "export_time": datetime.now().isoformat(),
                "total_orders": len(orders),
                "orders": orders
            }, f, indent=2, ensure_ascii=False)
        
        # 保存CSV
        csv_file = f"{DATA_DIR}/orders_{timestamp}.csv"
        if orders:
            keys = orders[0].keys()
            with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(orders)
        
        return json_file, csv_file
    
    def generate_summary(self, orders):
        """生成订单摘要"""
        if not orders:
            return {"error": "无订单数据"}
        
        completed = [o for o in orders if o["status"] == "已完成"]
        canceled = [o for o in orders if o["status"] == "已取消"]
        
        total_amount = sum(o["total_amount"] for o in completed)
        avg_amount = total_amount / len(completed) if completed else 0
        avg_rating = sum(o["customer_rating"] for o in completed) / len(completed) if completed else 0
        avg_delivery = sum(o["delivery_time_minutes"] for o in completed) / len(completed) if completed else 0
        
        summary = {
            "统计时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "总订单数": len(orders),
            "完成订单": len(completed),
            "取消订单": len(canceled),
            "完成率": f"{len(completed)/len(orders)*100:.1f}%" if orders else "0%",
            "总营业额": round(total_amount, 2),
            "客单价": round(avg_amount, 2),
            "平均评分": round(avg_rating, 2),
            "平均配送时间": f"{round(avg_delivery)}分钟"
        }
        
        return summary

def main():
    print("=" * 60)
    print("🍜 饿了么订单下载")
    print("=" * 60)
    
    downloader = ElemeOrderDownloader()
    
    # 下载订单（默认3天）
    orders = downloader.download_orders(days=3)
    
    # 保存
    json_file, csv_file = downloader.save_orders(orders)
    print(f"\n✅ 已保存:")
    print(f"   JSON: {json_file}")
    print(f"   CSV: {csv_file}")
    
    # 生成摘要
    summary = downloader.generate_summary(orders)
    
    print(f"\n📊 订单摘要:")
    for k, v in summary.items():
        print(f"   {k}: {v}")
    
    # 保存摘要
    summary_file = f"{DATA_DIR}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 摘要: {summary_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()

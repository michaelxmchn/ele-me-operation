#!/usr/bin/env python3
"""
饿了么数据分析脚本
用于优化运营策略
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = "/home/michael/projects/ele-me-operation/data"

class ElemeAnalyzer:
    def __init__(self):
        self.data_dir = DATA_DIR
        
    def load_latest_orders(self):
        """加载最新订单数据"""
        files = [f for f in os.listdir(self.data_dir) if f.startswith("orders_") and f.endswith(".json")]
        if not files:
            return None
        
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(self.data_dir, x)))
        
        with open(os.path.join(self.data_dir, latest_file), "r", encoding="utf-8") as f:
            return json.load(f)
    
    def analyze_by_time(self, orders):
        """按时段分析订单"""
        time_analysis = defaultdict(lambda: {"count": 0, "amount": 0})
        
        for order in orders:
            if order["status"] != "已完成":
                continue
            
            hour = datetime.fromisoformat(order["order_time"]).hour
            
            if 7 <= hour < 9:
                period = "早餐(07-09)"
            elif 11 <= hour < 13:
                period = "午餐(11-13)"
            elif 17 <= hour < 19:
                period = "晚餐(17-19)"
            elif 21 <= hour < 23:
                period = "夜宵(21-23)"
            else:
                period = "其他时段"
            
            time_analysis[period]["count"] += 1
            time_analysis[period]["amount"] += order["total_amount"]
        
        return time_analysis
    
    def analyze_by_area(self, orders):
        """按区域分析订单"""
        area_analysis = defaultdict(lambda: {"count": 0, "amount": 0})
        
        for order in orders:
            if order["status"] != "已完成":
                continue
            
            area = order.get("address_area", "未知")
            area_analysis[area]["count"] += 1
            area_analysis[area]["amount"] += order["total_amount"]
        
        return area_analysis
    
    def calculate_metrics(self, orders):
        """计算关键指标"""
        completed = [o for o in orders if o["status"] == "已完成"]
        
        if not completed:
            return {"error": "无完成订单"}
        
        total_revenue = sum(o["total_amount"] for o in completed)
        avg_order_value = total_revenue / len(completed)
        avg_rating = sum(o["customer_rating"] for o in completed) / len(completed)
        avg_delivery = sum(o["delivery_time_minutes"] for o in completed) / len(completed)
        
        # 按时段统计
        time_stats = self.analyze_by_time(completed)
        peak_period = max(time_stats.items(), key=lambda x: x[1]["count"])
        
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed),
            "cancellation_rate": f"{(len(orders)-len(completed))/len(orders)*100:.1f}%",
            "total_revenue": round(total_revenue, 2),
            "avg_order_value": round(avg_order_value, 2),
            "avg_rating": round(avg_rating, 2),
            "avg_delivery_time": f"{round(avg_delivery)}分钟",
            "peak_period": f"{peak_period[0]} ({peak_period[1]['count']}单)",
        }
    
    def generate_recommendations(self, metrics, time_analysis, area_analysis):
        """生成优化建议"""
        recommendations = []
        
        # 基于评分建议
        if metrics.get("avg_rating", 5) < 4.5:
            recommendations.append("⚠️ 平均评分低于4.5，需关注菜品质量和包装")
        
        # 基于配送时间建议
        if "分钟" in str(metrics.get("avg_delivery_time", "")):
            delivery_mins = int(metrics["avg_delivery_time"].replace("分钟", ""))
            if delivery_mins > 35:
                recommendations.append("⚠️ 配送时间过长，建议优化备餐流程")
        
        # 基于高峰时段建议
        if time_analysis:
            peak = max(time_analysis.items(), key=lambda x: x[1]["count"])
            recommendations.append(f"📈 高峰时段: {peak[0]}，建议提前备货")
        
        # 基于区域建议
        if area_analysis:
            top_area = max(area_analysis.items(), key=lambda x: x[1]["count"])
            recommendations.append(f"📍 订单最多区域: {top_area[0]}，可针对性推广")
        
        return recommendations
    
    def generate_report(self):
        """生成完整分析报告"""
        data = self.load_latest_orders()
        if not data:
            print("❌ 无订单数据")
            return
        
        orders = data.get("orders", [])
        
        print("=" * 60)
        print("📊 饿了么运营数据分析报告")
        print("=" * 60)
        
        # 关键指标
        metrics = self.calculate_metrics(orders)
        print("\n📈 关键指标:")
        for k, v in metrics.items():
            print(f"   {k}: {v}")
        
        # 时段分析
        time_analysis = self.analyze_by_time([o for o in orders if o["status"] == "已完成"])
        print(f"\n⏰ 时段分析:")
        for period, stats in sorted(time_analysis.items()):
            avg = stats["amount"] / stats["count"] if stats["count"] > 0 else 0
            print(f"   {period}: {stats['count']}单, ¥{round(stats['amount'], 2)}, 客单¥{round(avg, 2)}")
        
        # 区域分析
        area_analysis = self.analyze_by_area([o for o in orders if o["status"] == "已完成"])
        print(f"\n📍 区域分析:")
        for area, stats in sorted(area_analysis.items(), key=lambda x: x[1]["count"], reverse=True):
            avg = stats["amount"] / stats["count"] if stats["count"] > 0 else 0
            print(f"   {area}: {stats['count']}单, ¥{round(stats['amount'], 2)}")
        
        # 优化建议
        recommendations = self.generate_recommendations(metrics, time_analysis, area_analysis)
        print(f"\n💡 优化建议:")
        for rec in recommendations:
            print(f"   {rec}")
        
        print("=" * 60)
        
        # 保存报告
        report = {
            "report_time": datetime.now().isoformat(),
            "data_source": data.get("export_time", ""),
            "metrics": metrics,
            "time_analysis": dict(time_analysis),
            "area_analysis": dict(area_analysis),
            "recommendations": recommendations
        }
        
        report_file = f"{DATA_DIR}/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存: {report_file}")

def main():
    analyzer = ElemeAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()

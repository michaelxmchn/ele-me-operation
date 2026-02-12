#!/usr/bin/env python3
"""
饿了么推广自动调整脚本
根据时段自动调整推广出价和预算
"""

import json
import os
from datetime import datetime, time
from enum import Enum

# 配置
CONFIG_FILE = "/home/michael/projects/ele-me-operation/CORE_STRATEGY.json"
LOG_DIR = "/home/michael/projects/ele-me-operation/logs"

class TimePeriod(Enum):
    MORNING = "早餐"      # 07:00-09:00
    LUNCH = "午餐"        # 11:00-13:00
    AFTERNOON = "下午"    # 14:00-16:00
    DINNER = "晚餐"       # 17:00-19:00
    NIGHT = "夜宵"        # 21:00-23:00
    OFF_PEAK = "深夜"     # 23:00-07:00

class PromotionAutoManager:
    def __init__(self):
        self.load_strategy()
        
    def load_strategy(self):
        """加载策略配置"""
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            self.strategy = json.load(f)
        
        self.promotion = self.strategy.get("推广策略", {})
        self.limits = self.strategy.get("防限制规则", {})
        
    def get_current_period(self):
        """获取当前时段"""
        now = datetime.now().time()
        
        if time(7, 0) <= now < time(9, 0):
            return TimePeriod.MORNING
        elif time(11, 0) <= now < time(13, 0):
            return TimePeriod.LUNCH
        elif time(14, 0) <= now < time(16, 0):
            return TimePeriod.AFTERNOON
        elif time(17, 0) <= now < time(19, 0):
            return TimePeriod.DINNER
        elif time(21, 0) <= now < time(23, 0):
            return TimePeriod.NIGHT
        else:
            return TimePeriod.OFF_PEAK
    
    def get_bid_config(self, period):
        """获取出价配置"""
        bidding = self.promotion.get("竞价推广", {})
        point = self.promotion.get("点金推广", {})
        
        base_bid = bidding.get("出价范围", "1元").replace("元/点击", "")
        base_bid = float(base_bid.split("-")[0]) if "-" in base_bid else 1.0
        
        configs = {
            TimePeriod.MORNING: {
                "bid_multiplier": 1.2,
                "budget_multiplier": 1.2,
                "action": "开启推广",
                "reason": "早餐高峰，提高出价20%"
            },
            TimePeriod.LUNCH: {
                "bid_multiplier": 1.5,
                "budget_multiplier": 1.5,
                "action": "高峰模式",
                "reason": "午餐高峰，提高出价50%"
            },
            TimePeriod.AFTERNOON: {
                "bid_multiplier": 0.7,
                "budget_multiplier": 0.7,
                "action": "降低出价",
                "reason": "非高峰，降低出价30%"
            },
            TimePeriod.DINNER: {
                "bid_multiplier": 1.5,
                "budget_multiplier": 1.5,
                "action": "高峰模式",
                "reason": "晚餐高峰，提高出价50%"
            },
            TimePeriod.NIGHT: {
                "bid_multiplier": 1.0,
                "budget_multiplier": 1.0,
                "action": "正常推广",
                "reason": "夜宵，维持正常出价"
            },
            TimePeriod.OFF_PEAK: {
                "bid_multiplier": 0,
                "budget_multiplier": 0,
                "action": "暂停推广",
                "reason": "深夜时段，暂停节省预算"
            }
        }
        
        return configs.get(period, configs[TimePeriod.OFF_PEAK])
    
    def calculate_budget(self, target_orders=30, avg_order_value=25):
        """计算日预算"""
        formula = self.promotion.get("预算控制", {}).get("日预算公式", "")
        base_budget = target_orders * avg_order_value * 0.1
        return round(base_budget, 2)
    
    def simulate_api_call(self, bid_config, period):
        """模拟API调用（实际需对接饿了么API）"""
        period_name = period.value
        
        if bid_config["bid_multiplier"] == 0:
            return {
                "action": "PAUSE",
                "message": f"[{period_name}] 推广已暂停",
                "bid": 0,
                "budget": 0
            }
        
        base_bid = 1.0
        new_bid = round(base_bid * bid_config["bid_multiplier"], 2)
        budget = round(75 * bid_config["budget_multiplier"], 2)
        
        return {
            "action": bid_config["action"],
            "message": f"[{period_name}] {bid_config['reason']}",
            "bid": new_bid,
            "budget": budget,
            "period": period_name
        }
    
    def adjust_promotion(self):
        """执行推广调整"""
        period = self.get_current_period()
        bid_config = self.get_bid_config(period)
        result = self.simulate_api_call(bid_config, period)
        
        # 记录日志
        self.log_adjustment(result)
        
        return result
    
    def log_adjustment(self, result):
        """记录调整日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            **result
        }
        
        log_file = f"{LOG_DIR}/promotion_adjustments.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        return log_entry
    
    def get_daily_summary(self):
        """获取今日推广调整摘要"""
        log_file = f"{LOG_DIR}/promotion_adjustments.jsonl"
        
        if not os.path.exists(log_file):
            return {"message": "暂无调整记录"}
        
        adjustments = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["timestamp"].startswith(today):
                    adjustments.append(entry)
        
        if not adjustments:
            return {"message": "今日暂无调整"}
        
        return {
            "date": today,
            "total_adjustments": len(adjustments),
            "last_action": adjustments[-1].get("action", ""),
            "current_bid": adjustments[-1].get("bid", 0),
            "history": adjustments[-5:]  # 最近5条
        }

def main():
    print("=" * 60)
    print("📢 饿了么推广自动调整")
    print("=" * 60)
    
    manager = PromotionAutoManager()
    
    # 执行调整
    result = manager.adjust_promotion()
    
    print(f"\n⏰ 当前时段: {result.get('period', '未知')}")
    print(f"📢 操作: {result.get('action', 'N/A')}")
    print(f"💰 原因: {result.get('message', 'N/A')}")
    print(f"💵 建议出价: {result.get('bid', 0)}元")
    print(f"📊 建议预算: {result.get('budget', 0)}元")
    
    # 今日摘要
    summary = manager.get_daily_summary()
    print(f"\n📊 今日调整:")
    print(f"   调整次数: {summary.get('total_adjustments', 0)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

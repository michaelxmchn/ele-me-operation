#!/usr/bin/env python3
"""
饿了么运营智能分析 - DeepSeek AI 版
学习分析订单数据，生成优化建议
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# 配置
DATA_DIR = "/home/michael/projects/ele-me-operation/data"
LOG_DIR = "/home/michael/projects/ele-me-operation/logs"
CONFIG_FILE = "/home/michael/projects/ele-me-operation/CORE_STRATEGY.json"

# DeepSeek API
DEEPSEEK_API = "sk-f04a00d9f3d54cc2861552fd46e8ed76"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

class ElemeDeepSeekAnalyzer:
    def __init__(self):
        self.api_key = DEEPSEEK_API
        self.api_url = DEEPSEEK_URL
        self.model = "deepseek-chat"
        
    def load_latest_orders(self) -> Dict[str, Any]:
        """加载最新订单数据"""
        files = [f for f in os.listdir(DATA_DIR) if f.startswith("orders_") and f.endswith(".json")]
        if not files:
            return None
        
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)))
        
        with open(os.path.join(DATA_DIR, latest_file), "r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_strategy(self) -> Dict[str, Any]:
        """加载运营策略"""
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def calculate_metrics(self, orders: List[Dict]) -> Dict[str, Any]:
        """计算关键指标"""
        completed = [o for o in orders if o["status"] == "已完成"]
        
        if not completed:
            return {"error": "无完成订单"}
        
        # 按小时统计
        hourly_stats = {}
        for o in completed:
            hour = datetime.fromisoformat(o["order_time"]).hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {"count": 0, "amount": 0}
            hourly_stats[hour]["count"] += 1
            hourly_stats[hour]["amount"] += o["total_amount"]
        
        # 计算指标
        total_revenue = sum(o["total_amount"] for o in completed)
        
        metrics = {
            "total_orders": len(orders),
            "completed_orders": len(completed),
            "cancellation_rate": round((len(orders) - len(completed)) / len(orders) * 100, 1),
            "total_revenue": round(total_revenue, 2),
            "avg_order_value": round(total_revenue / len(completed), 2),
            "avg_rating": round(sum(o["customer_rating"] for o in completed) / len(completed), 2),
            "avg_delivery_time": round(sum(o["delivery_time_minutes"] for o in completed) / len(completed), 1),
            "peak_hour": max(hourly_stats.items(), key=lambda x: x[1]["count"])[0] if hourly_stats else None,
            "hourly_distribution": {str(k): v for k, v in hourly_stats.items()}
        }
        
        return metrics
    
    def prepare_analysis_data(self, data: Dict[str, Any], strategy: Dict) -> str:
        """准备发送给 DeepSeek 分析的数据"""
        orders = data.get("orders", [])
        metrics = self.calculate_metrics(orders)
        promotion = strategy.get("推广策略", {})
        limits = strategy.get("防限制规则", {})
        
        # 构建分析提示
        analysis_prompt = f"""
请分析以下饿了么外卖店铺的运营数据，并提供详细的优化建议：

## 一、核心指标
- 总订单数: {metrics.get('total_orders', 0)}
- 完成订单: {metrics.get('completed_orders', 0)}
- 取消率: {metrics.get('cancellation_rate', 0)}%
- 总营业额: ¥{metrics.get('total_revenue', 0)}
- 客单价: ¥{metrics.get('avg_order_value', 0)}
- 平均评分: {metrics.get('avg_rating', 0)}⭐
- 平均配送时间: {metrics.get('avg_delivery_time', 0)}分钟
- 高峰时段: {metrics.get('peak_hour', 'N/A')}:00

## 二、时段分布
"""
        
        hourly = metrics.get("hourly_distribution", {})
        for hour in sorted(hourly.keys()):
            stats = hourly[hour]
            period = self._get_period_name(int(hour))
            analysis_prompt += f"- {hour}:00 ({period}): {stats['count']}单, ¥{round(stats['amount'], 2)}\n"
        
        analysis_prompt += f"""
## 三、当前策略配置
### 目标
- 目标订单: {strategy.get('运营目标', {}).get('secondary', 'N/A')}
- 目标评分: {limits.get('最低评分', 'N/A')}⭐

### 价格策略
- 起送价: {strategy.get('价格策略', {}).get('起送价优化', 'N/A')}
- 满减: {strategy.get('价格策略', {}).get('满减设置', 'N/A')}

### 推广预算
- 日预算公式: {promotion.get('预算控制', {}).get('日预算公式', 'N/A')}
- ROI目标: ≥{promotion.get('ROI指标', {}).get('ROI阈值', 'N/A')}

### 防限制规则
- 价格修改上限: {limits.get('价格修改频率', 'N/A')}
- 推广调整上限: {limits.get('推广调整频率', 'N/A')}

## 四、分析要求
请从以下维度分析并提供建议：
1. **问题诊断**: 识别当前数据中的主要问题（如取消率过高、高峰单量不足等）
2. **优化建议**: 
   - 价格优化（起送价、满减设置）
   - 时段策略调整
   - 推广出价优化
   - 出餐流程改进
3. **风险提示**: 可能违反防限制规则的操作
4. **具体行动计划**: 下3天可以立即执行的具体措施

请用JSON格式返回分析结果，包含以下字段：
{{
    "summary": "一句话总结",
    "problems": ["问题1", "问题2"],
    "recommendations": {{
        "price": ["建议1", "建议2"],
        "timing": ["建议1", "建议2"],
        "promotion": ["建议1", "建议2"],
        "operations": ["建议1", "建议2"]
    }},
    "action_plan": ["行动1", "行动2", "行动3"],
    "risk_warnings": ["警告1", "警告2"],
    "confidence": "高/中/低"
}}
"""
        
        return analysis_prompt
    
    def _get_period_name(self, hour: int) -> str:
        """获取时段名称"""
        if 7 <= hour < 9:
            return "早餐"
        elif 11 <= hour < 13:
            return "午餐"
        elif 17 <= hour < 19:
            return "晚餐"
        elif 21 <= hour < 23:
            return "夜宵"
        else:
            return "其他"
    
    def analyze_with_deepseek(self, prompt: str) -> Dict[str, Any]:
        """调用 DeepSeek AI 进行分析"""
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的外卖运营顾问，擅长分析订单数据并提供优化建议。请始终返回JSON格式的分析结果。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 解析JSON
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    return json.loads(content[start:end])
                else:
                    return {"error": "无法解析AI返回结果", "raw": content}
            else:
                return {"error": f"API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def run_analysis(self) -> Dict[str, Any]:
        """执行完整分析"""
        print("=" * 70)
        print("🧠 DeepSeek AI 智能分析")
        print("=" * 70)
        
        # 加载数据
        data = self.load_latest_orders()
        if not data:
            print("❌ 无订单数据可分析")
            return {"error": "无订单数据"}
        
        strategy = self.load_strategy()
        
        # 准备分析数据
        prompt = self.prepare_analysis_data(data, strategy)
        print("\n📊 正在调用 DeepSeek AI 分析...")
        
        # AI 分析
        analysis = self.analyze_with_deepseek(prompt)
        
        if "error" in analysis:
            print(f"❌ 分析失败: {analysis['error']}")
            return analysis
        
        # 打印结果
        print("\n" + "=" * 70)
        print("📋 AI 分析报告")
        print("=" * 70)
        
        print(f"\n🔍 总结: {analysis.get('summary', 'N/A')}")
        
        problems = analysis.get("problems", [])
        if problems:
            print(f"\n⚠️ 发现问题:")
            for i, p in enumerate(problems, 1):
                print(f"   {i}. {p}")
        
        recommendations = analysis.get("recommendations", {})
        if recommendations:
            print(f"\n💡 优化建议:")
            for category, items in recommendations.items():
                if items:
                    print(f"\n   【{category.upper()}】")
                    for item in items:
                        print(f"   • {item}")
        
        action_plan = analysis.get("action_plan", [])
        if action_plan:
            print(f"\n🎯 行动计划:")
            for i, action in enumerate(action_plan, 1):
                print(f"   {i}. {action}")
        
        risk_warnings = analysis.get("risk_warnings", [])
        if risk_warnings:
            print(f"\n⚠️ 风险提示:")
            for warning in risk_warnings:
                print(f"   • {warning}")
        
        print(f"\n📊 AI置信度: {analysis.get('confidence', 'N/A')}")
        print("=" * 70)
        
        # 保存分析结果
        result = {
            "analysis_time": datetime.now().isoformat(),
            "data_source": data.get("export_time", ""),
            "ai_analysis": analysis,
            "raw_prompt": prompt[:500]  # 保存前500字符
        }
        
        result_file = f"{DATA_DIR}/deepseek_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 分析结果已保存: {result_file}")
        
        return result
    
    def get_comparison_report(self, days: int = 7) -> Dict[str, Any]:
        """生成对比分析报告（多日数据）"""
        analysis_files = [f for f in os.listdir(DATA_DIR) if f.startswith("deepseek_analysis")]
        analysis_files.sort()
        
        if len(analysis_files) < 2:
            return {"message": "历史分析数据不足"}
        
        # 取最近N天的分析
        recent = analysis_files[-3:]  # 最近3次
        
        comparisons = []
        for f in recent:
            with open(os.path.join(DATA_DIR, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                comparisons.append(data)
        
        # 构建对比提示
        comparison_prompt = f"""
请对比分析以下近期的AI运营分析报告，找出趋势变化和优化效果：

"""
        
        for i, c in enumerate(comparisons):
            analysis_time = c.get("analysis_time", "")
            ai = c.get("ai_analysis", {})
            summary = ai.get("summary", "")
            comparison_prompt += f"## 报告{i+1} ({analysis_time[:10]})\n{summary}\n\n"
        
        comparison_prompt += """
请生成对比分析报告，包括：
1. 整体趋势判断（上升/下降/稳定）
2. 持续存在的问题
3. 已改善的指标
4. 下一步重点优化方向

请返回JSON格式:
{
    "trend": "上升/下降/稳定",
    "persistent_problems": ["问题1", "问题2"],
    "improved_metrics": ["指标1", "指标2"],
    "next_focus": ["重点1", "重点2"],
    "overall_assessment": "整体评估"
}
"""
        
        # 调用AI
        return self.analyze_with_deepseek(comparison_prompt)


def main():
    analyzer = ElemeDeepSeekAnalyzer()
    
    print("\n" + "=" * 70)
    print("🍜 饿了么运营智能分析 - DeepSeek AI 版")
    print("=" * 70)
    
    # 选择模式
    print("\n请选择分析模式:")
    print("1. 单次分析（推荐）")
    print("2. 对比分析（需多次数据）")
    
    choice = input("请输入选项 (1/2): ").strip()
    
    if choice == "2":
        result = analyzer.get_comparison_report()
    else:
        result = analyzer.run_analysis()
    
    if "error" in result:
        print(f"\n❌ 分析失败: {result['error']}")
    else:
        print("\n✅ 分析完成！")


if __name__ == "__main__":
    main()

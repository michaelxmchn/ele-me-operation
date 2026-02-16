#!/usr/bin/env python3
"""
AI模型对比分析脚本
支持多个AI模型的分析调用

使用方法:
    python3 model_analyst.py --model deepseek "分析内容"
    python3 model_analyst.py --model minimax "分析内容"
    python3 model_analyst.py --all "分析内容"  # 对比所有模型
"""

import os
import json
import argparse
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

# ==================== 配置 ====================

# API配置
CONFIG = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": os.environ.get("DEEPSEEK_API_KEY", "sk-96c514b15b454651b7d6ededda68fd6f"),
        "model": "deepseek-chat",
        "max_tokens": 2048,
    },
    "minimax": {
        "base_url": "https://api.minimaxi.com/v1",
        "api_key": os.environ.get("MINIMAX_API_KEY", "your-api-key"),
        "model": "abab6.5s-chat",
        "max_tokens": 2048,
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": os.environ.get("OPENAI_API_KEY", "your-api-key"),
        "model": "gpt-4o-mini",
        "max_tokens": 2048,
    },
    "claude": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key": os.environ.get("ANTHROPIC_API_KEY", "your-api-key"),
        "model": "claude-3-haiku-20240307",
        "max_tokens": 2048,
    }
}

# ==================== 模型调用类 ====================

class ModelAnalyst:
    """AI模型分析器"""
    
    def __init__(self, model_name: str = "deepseek"):
        self.model_name = model_name.lower()
        self.config = CONFIG.get(self.model_name)
        
        if not self.config:
            raise ValueError(f"不支持的模型: {model_name}")
    
    def analyze(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """调用AI模型进行分析"""
        import requests
        
        headers = {
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            if self.model_name == "deepseek":
                headers["Authorization"] = f"Bearer {self.config['api_key']}"
                response = requests.post(
                    f"{self.config['base_url']}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.config["model"],
                        "messages": messages,
                        "max_tokens": self.config["max_tokens"]
                    },
                    timeout=30
                )
                result = response.json()
                
                return {
                    "success": True,
                    "model": self.model_name,
                    "response": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "time": time.time() - start_time
                }
                
            elif self.model_name == "minimax":
                headers["Authorization"] = f"Bearer {self.config['api_key']}"
                response = requests.post(
                    f"{self.config['base_url']}/text/chatcompletion_v2",
                    headers=headers,
                    json={
                        "model": self.config["model"],
                        "messages": messages,
                        "max_tokens": self.config["max_tokens"]
                    },
                    timeout=30
                )
                result = response.json()
                
                return {
                    "success": True,
                    "model": self.model_name,
                    "response": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "time": time.time() - start_start_time
                }
                
            elif self.model_name == "openai":
                headers["Authorization"] = f"Bearer {self.config['api_key']}"
                response = requests.post(
                    f"{self.config['base_url']}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.config["model"],
                        "messages": messages,
                        "max_tokens": self.config["max_tokens"]
                    },
                    timeout=30
                )
                result = response.json()
                
                return {
                    "success": True,
                    "model": self.model_name,
                    "response": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "time": time.time() - start_time
                }
                
            elif self.model_name == "claude":
                headers["x-api-key"] = self.config["api_key"]
                headers["anthropic-version"] = "2023-06-01"
                response = requests.post(
                    f"{self.config['base_url']}/messages",
                    headers=headers,
                    json={
                        "model": self.config["model"],
                        "messages": messages,
                        "max_tokens": self.config["max_tokens"]
                    },
                    timeout=30
                )
                result = response.json()
                
                return {
                    "success": True,
                    "model": self.model_name,
                    "response": result["content"][0]["text"],
                    "usage": result.get("usage", {}),
                    "time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "model": self.model_name,
                "error": str(e),
                "time": time.time() - start_time
            }
    
    def compare(self, prompt: str, models: List[str] = None) -> Dict[str, Any]:
        """对比多个模型的分析结果"""
        if models is None:
            models = list(CONFIG.keys())
        
        results = {}
        
        for model in models:
            try:
                analyst = ModelAnalyst(model)
                result = analyst.analyze(prompt)
                results[model] = result
            except Exception as e:
                results[model] = {"success": False, "error": str(e)}
        
        return results


# ==================== 分析器 ====================

class ContentAnalyzer:
    """内容分析器 - 针对不同场景的分析"""
    
    @staticmethod
    def analyze_business(prompt: str) -> str:
        """商业分析system prompt"""
        return """你是一个专业的商业分析师。你的分析应该包括:
1. 市场机会评估
2. 竞争优势分析
3. 潜在风险识别
4. 建议的行动计划
请用清晰的结构化方式输出。"""
    
    @staticmethod
    def analyze_technical(prompt: str) -> str:
        """技术分析system prompt"""
        return """你是一个资深技术专家。你的分析应该包括:
1. 技术可行性评估
2. 技术架构建议
3. 潜在技术风险
4. 实施建议
请用清晰的结构化方式输出。"""
    
    @staticmethod
    def analyze_strategy(prompt: str) -> str:
        """战略分析system prompt"""
        return """你是一个战略顾问。你的分析应该包括:
1. 战略机会分析
2. 竞争格局评估
3. 资源需求分析
4. 战略建议
请用清晰的结构化方式输出。"""


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description="AI模型对比分析工具")
    parser.add_argument("--prompt", "-p", type=str, help="要分析的内容")
    parser.add_argument("--model", "-m", type=str, default="deepseek", 
                       choices=list(CONFIG.keys()),
                       help="使用的模型")
    parser.add_argument("--all", "-a", action="store_true",
                       help="对比所有模型")
    parser.add_argument("--type", "-t", type=str, 
                       choices=["business", "technical", "strategy", "general"],
                       default="general",
                       help="分析类型")
    parser.add_argument("--output", "-o", type=str,
                       help="输出文件路径")
    
    args = parser.parse_args()
    
    # 获取分析内容
    if args.prompt:
        prompt = args.prompt
    else:
        print("请输入要分析的内容:")
        prompt = input("> ")
    
    # 获取system prompt
    system_prompts = {
        "business": ContentAnalyzer.analyze_business(prompt),
        "technical": ContentAnalyzer.analyze_technical(prompt),
        "strategy": ContentAnalyzer.analyze_strategy(prompt),
        "general": "你是一个AI助手，请用专业、清晰的方式回答用户问题。"
    }
    system_prompt = system_prompts.get(args.type, system_prompts["general"])
    
    # 执行分析
    print(f"\n{'='*50}")
    print(f"📊 AI模型分析工具")
    print(f"{'='*50}")
    print(f"分析类型: {args.type}")
    print(f"输入内容: {prompt[:50]}...")
    print(f"{'='*50}\n")
    
    if args.all:
        # 对比所有模型
        analyst = ModelAnalyst("deepseek")
        results = analyst.compare(prompt)
        
        for model, result in results.items():
            print(f"\n{'='*40}")
            print(f"🤖 模型: {model.upper()}")
            print(f"{'='*40}")
            
            if result.get("success"):
                print(f"⏱️ 耗时: {result.get('time', 0):.2f}秒")
                print(f"\n📝 分析结果:")
                print(result.get("response", ""))
                
                usage = result.get("usage", {})
                if usage:
                    print(f"\n📊 Token使用:")
                    print(f"   输入: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   输出: {usage.get('completion_tokens', 'N/A')}")
            else:
                print(f"❌ 错误: {result.get('error', 'Unknown error')}")
    else:
        # 单模型分析
        analyst = ModelAnalyst(args.model)
        result = analyst.analyze(prompt, system_prompt)
        
        if result.get("success"):
            print(f"✅ 模型: {args.model.upper()}")
            print(f"⏱️ 耗时: {result.get('time', 0):.2f}秒")
            print(f"\n📝 分析结果:")
            print(result.get("response", ""))
            
            usage = result.get("usage", {})
            if usage:
                print(f"\n📊 Token使用:")
                print(f"   输入: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   输出: {usage.get('completion_tokens', 'N/A')}")
        else:
            print(f"❌ 错误: {result.get('error', 'Unknown error')}")
    
    # 保存结果
    if args.output:
        output_data = {
            "prompt": prompt,
            "type": args.type,
            "timestamp": datetime.now().isoformat(),
            "results": results if args.all else result
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到: {args.output}")


if __name__ == "__main__":
    main()

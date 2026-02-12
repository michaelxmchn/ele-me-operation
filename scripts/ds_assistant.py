#!/usr/bin/env python3
"""
DeepSeek 本地辅助系统
专门处理复杂逻辑优化，减少 Token 消耗
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Any, Dict, Optional
from functools import lru_cache

# 配置
CACHE_DIR = "/home/michael/.openclaw/workspace/.ds_cache"
OPTIMIZATION_LOG = "/home/michael/.openclaw/workspace/.ds_optimizations.log"

class DeepSeekAssistant:
    """本地 DeepSeek 辅助系统"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk-f04a00d9f3d54cc2861552fd46e8ed76"
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        self.cache_dir = CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _hash_data(self, data: Any) -> str:
        """生成数据哈希"""
        return hashlib.md5(str(data).encode()).hexdigest()[:16]
    
    def _get_cache_path(self, data_hash: str) -> str:
        """获取缓存路径"""
        return os.path.join(self.cache_dir, f"{data_hash}.json")
    
    def _load_cache(self, data_hash: str) -> Optional[Dict]:
        """加载缓存"""
        path = self._get_cache_path(data_hash)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None
    
    def _save_cache(self, data_hash: str, result: Dict):
        """保存缓存"""
        path = self._get_cache_path(data_hash)
        with open(path, "w") as f:
            json.dump(result, f, indent=2)
    
    def _log_optimization(self, task_type: str, original_tokens: int, optimized_tokens: int):
        """记录优化效果"""
        log = {
            "time": datetime.now().isoformat(),
            "task_type": task_type,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "savings": f"{(1 - optimized_tokens/original_tokens)*100:.0f}%"
        }
        
        with open(OPTIMIZATION_LOG, "a") as f:
            f.write(json.dumps(log) + "\n")
    
    @lru_cache(maxsize=50)
    def optimize_script(self, script_content: str, focus: str = "token") -> Dict:
        """
        优化代码脚本
        
        Args:
            script_content: 脚本内容
            focus: 优化重点 (token/performance/both)
        
        Returns:
            优化建议
        """
        task_type = f"script_optimize_{focus}"
        data_hash = self._hash_data(script_content + focus)
        
        # 检查缓存
        cached = self._load_cache(data_hash)
        if cached:
            print(f"✅ 使用缓存: {task_type}")
            return cached
        
        # 构建优化提示
        prompt = f"""请优化以下 Python 代码，{focus}相关优化：

{self._truncate(script_content, 3000)}

请用 JSON 格式返回：
{{
    "summary": "优化概述",
    "changes": ["改动1", "改动2"],
    "estimated_savings": "预估收益",
    "code_suggestions": [{{"before": "原代码", "after": "优化后", "reason": "原因"}}]
}}
"""
        
        result = self._call_deepseek(prompt, max_tokens=1500)
        
        if result:
            self._save_cache(data_hash, result)
            self._log_optimization(task_type, 3000, len(prompt))
        
        return result
    
    def analyze_logic(self, problem: str, context: str = "") -> Dict:
        """
        分析复杂逻辑问题
        
        Args:
            problem: 问题描述
            context: 上下文信息
        
        Returns:
            分析结果
        """
        task_type = "logic_analysis"
        data_hash = self._hash_data(problem + context)
        
        cached = self._load_cache(data_hash)
        if cached:
            return cached
        
        prompt = f"""请分析以下逻辑问题：

问题：{problem}

上下文：{context}

请用 JSON 格式返回：
{{
    "analysis": "问题分析",
    "approaches": ["方案1", "方案2"],
    "recommendation": "推荐方案",
    "implementation_notes": ["注意1", "注意2"]
}}
"""
        
        result = self._call_deepseek(prompt, max_tokens=800)
        
        if result:
            self._save_cache(data_hash, result)
        
        return result
    
    def generate_code(self, requirement: str, language: str = "python") -> Dict:
        """
        生成代码
        
        Args:
            requirement: 功能需求
            language: 编程语言
        
        Returns:
            生成的代码
        """
        task_type = f"code_generation_{language}"
        data_hash = self._hash_data(requirement)
        
        cached = self._load_cache(data_hash)
        if cached:
            return cached
        
        prompt = f"""请用 {language} 实现以下功能：

{requirement}

请用 JSON 格式返回：
{{
    "code": "代码",
    "explanation": "说明",
    "usage_example": "使用示例"
}}
"""
        
        result = self._call_deepseek(prompt, max_tokens=1200)
        
        if result:
            self._save_cache(data_hash, result)
        
        return result
    
    def optimize_prompt(self, original_prompt: str, goal: str = "reduce_tokens") -> Dict:
        """
        优化提示词
        
        Args:
            original_prompt: 原始提示词
            goal: 优化目标 (reduce_tokens/improve_accuracy/both)
        
        Returns:
            优化后的提示词
        """
        task_type = f"prompt_optimize_{goal}"
        data_hash = self._hash_data(original_prompt)
        
        cached = self._load_cache(data_hash)
        if cached:
            return cached
        
        prompt = f"""请优化以下提示词，目标：{goal}

原始提示词：
{self._truncate(original_prompt, 2000)}

请用 JSON 格式返回：
{{
    "optimized_prompt": "优化后的提示词",
    "changes": ["改动1", "改动2"],
    "estimated_token_reduction": "预估token减少百分比",
    "quality_impact": "对输出质量的影响"
}}
"""
        
        result = self._call_deepseek(prompt, max_tokens=1000)
        
        if result:
            self._save_cache(data_hash, result)
            original_len = len(original_prompt)
            optimized_len = len(result.get("optimized_prompt", ""))
            self._log_optimization(task_type, original_len, optimized_len)
        
        return result
    
    def _call_deepseek(self, prompt: str, max_tokens: int = 1000) -> Optional[Dict]:
        """调用 DeepSeek API"""
        try:
            import requests
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.5,
                    "top_p": 0.9
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                start, end = content.find("{"), content.rfind("}") + 1
                if start != -1 and end != 0:
                    return json.loads(content[start:end])
            
            print(f"❌ API错误: {response.status_code}")
            
        except Exception as e:
            print(f"❌ 调用失败: {e}")
        
        return None
    
    def _truncate(self, text: str, max_len: int) -> str:
        """截断文本"""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "...[截断]"
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        files = os.listdir(self.cache_dir) if os.path.exists(self.cache_dir) else []
        
        return {
            "cache_count": len(files),
            "cache_dir": self.cache_dir
        }
    
    def clear_cache(self):
        """清空缓存"""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir)
            print("✅ 缓存已清空")


# 便捷函数
def quick_optimize(script: str) -> Dict:
    """快速优化脚本（默认 token 优化）"""
    assistant = DeepSeekAssistant()
    return assistant.optimize_script(script, "token")


def analyze_problem(problem: str) -> Dict:
    """分析逻辑问题"""
    assistant = DeepSeekAssistant()
    return assistant.analyze_logic(problem)


def optimize_prompt(prompt: str) -> Dict:
    """优化提示词"""
    assistant = DeepSeekAssistant()
    return assistant.optimize_prompt(prompt, "reduce_tokens")


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 DeepSeek 本地辅助系统")
    print("=" * 60)
    
    assistant = DeepSeekAssistant()
    
    # 显示缓存统计
    stats = assistant.get_cache_stats()
    print(f"\n📦 缓存统计: {stats['cache_count']} 个缓存项")
    
    print("\n可用功能:")
    print("  • optimize_script(script, focus) - 优化代码")
    print("  • analyze_logic(problem, context) - 分析逻辑")
    print("  • generate_code(requirement) - 生成代码")
    print("  • optimize_prompt(prompt) - 优化提示词")
    
    print("\n" + "=" * 60)

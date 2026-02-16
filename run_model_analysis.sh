#!/bin/bash
# AI模型对比分析快捷命令

cd /home/michael/projects/ele-me-operation/scripts

# 显示帮助
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "AI模型对比分析工具"
    echo ""
    echo "用法:"
    echo "  ./run_model_analysis.sh deepseek '分析内容'     # 使用DeepSeek分析"
    echo "  ./run_model_analysis.sh minimax '分析内容'    # 使用MiniMax分析"
    echo "  ./run_model_analysis.sh all '分析内容'       # 对比所有模型"
    echo "  ./run_model_analysis.sh -t business '内容'   # 商业分析"
    echo "  ./run_model_analysis.sh -t technical '内容'   # 技术分析"
    exit 0
fi

# 运行分析
python3 model_analyst.py "$@"

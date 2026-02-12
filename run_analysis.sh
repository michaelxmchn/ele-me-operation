#!/bin/bash
# 饿了么运营分析快捷命令

echo "================================"
echo "🍜 饿了么运营智能分析"
echo "================================"

case "$1" in
    ai|AI)
        python3 /home/michael/.openclaw/workspace/scripts/ele_me_deepseek_analysis.py
        ;;
    order)
        python3 /home/michael/projects/ele-me-operation/scripts/order_download.py
        ;;
    analysis)
        python3 /home/michael/projects/ele-me-operation/scripts/data_analysis.py
        ;;
    promotion)
        python3 /home/michael/projects/ele-me-operation/scripts/promotion_adjust.py
        ;;
    all)
        echo "📥 下载订单..."
        python3 /home/michael/projects/ele-me-operation/scripts/order_download.py
        echo ""
        echo "📊 数据分析..."
        python3 /home/michael/projects/ele-me-operation/scripts/data_analysis.py
        echo ""
        echo "🧠 AI分析..."
        python3 /home/michael/.openclaw/workspace/scripts/ele_me_deepseek_analysis.py
        ;;
    *)
        echo "用法: ./run_analysis.sh <命令>"
        echo ""
        echo "命令:"
        echo "  ai         - DeepSeek AI 智能分析"
        echo "  order      - 下载订单数据"
        echo "  analysis   - 基础数据分析"
        echo "  promotion  - 推广自动调整"
        echo "  all        - 执行全部流程"
        ;;
esac

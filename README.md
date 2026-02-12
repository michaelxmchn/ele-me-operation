# 饿了么外卖运营系统

## 项目目标
**盈利基础上接更多订单**

## 核心策略 v1.2

### 1. 时间策略
| 时段 | 时间 | 策略 |
|------|------|------|
| 早餐高峰 | 07:00-09:00 | 备货+溢价 |
| 午餐高峰 | 11:00-13:00 | 全力出餐 |
| 晚餐高峰 | 17:00-19:00 | 备货+溢价 |
| 夜宵高峰 | 21:00-23:00 | 促销走量 |

### 2. 价格策略
- 高峰期溢价: 10-20%
- 非高峰期折扣: 15-25%
- 起送价: 20-25元
- 满减: 35-5, 50-8, 80-15

### 3. 出餐策略
- 平均出餐时间: 15-20分钟
- 高峰备货: 提前30%库存
- 爆单缓冲: 预留20%

### 4. 活动策略
- 新客立减: 2-3元
- 满减活动: 必开
- 进店领券: 2元门槛

### 5. 推广策略
| 时段 | 操作 | 出价调整 |
|------|------|----------|
| 07:00 | 开启推广 | +20% |
| 11:00 | 高峰模式 | +50% |
| 14:00 | 降低出价 | -30% |
| 17:00 | 高峰模式 | +50% |
| 23:00 | 暂停推广 | 关闭 |

### 6. 🧠 AI学习分析 ⭐新增
- **Provider**: DeepSeek (deepseek-chat)
- **API Key**: 已配置
- **分析维度**: 价格/时段/推广/服务/竞品
- **输出**: JSON结构化报告 + 3条行动计划

**AI 分析示例结果:**
- 取消率24% → 需优化出餐流程
- 订单分散 → 建议高峰满减套餐
- 评分4.82⭐ → 保持并鼓励晒图好评

## 防限制规则
- 价格修改: ≤20次/天
- 菜单更新: ≤10次/小时
- 推广调整: ≤5次/天

## 快速开始

### 使用快捷命令
```bash
cd ~/projects/ele-me-operation

# AI 智能分析
./run_analysis.sh ai

# 下载订单
./run_analysis.sh order

# 数据分析
./run_analysis.sh analysis

# 推广调整
./run_analysis.sh promotion

# 全部流程
./run_analysis.sh all
```

### 手动运行
```bash
# AI 分析
python3 scripts/deepseek_analysis.py

# 下载订单
python3 scripts/order_download.py

# 数据分析
python3 scripts/data_analysis.py

# 推广调整
python3 scripts/promotion_adjust.py
```

## 文件结构
```
ele-me-operation/
├── CORE_STRATEGY.json      # 核心策略 (v1.2)
├── PROJECT_CONFIG.json     # 项目配置
├── README.md               # 文档
├── run_analysis.sh         # 快捷命令 ⭐
├── cron_export_orders.json # 订单导出定时
├── cron_promotion_adjust.json # 推广调整定时
├── scripts/
│   ├── deepseek_analysis.py   # 🧠 AI分析 ⭐
│   ├── order_download.py      # 订单下载
│   ├── data_analysis.py       # 数据分析
│   └── promotion_adjust.py    # 推广调整
├── data/                  # 数据存储
│   ├── orders_*.json/csv   # 订单数据
│   └── ai_analysis_*.json  # AI分析结果 ⭐
└── logs/                  # 日志
```

## 数据流程
```
每3天: 订单下载 → 数据分析 → AI学习分析
      ↓           ↓           ↓
   data/      analysis_*.json  ai_analysis_*.json
```

## 下一步
1. 连接手机测试ADB
2. 安装饿了么商家版
3. 对接商家API（如有）

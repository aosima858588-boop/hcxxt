# hcxxt - 数据导入与退款查询系统

包含：离线统计脚本（Node.js）、后端 API（FastAPI + SQLite）、前端示例组件。

## 快速开始（离线脚本）

1. 放置 data.js 在仓库根目录（已提供）。
2. 运行：
   ```bash
   node scripts/analyze.js
   ```
   或查询某用户：
   ```bash
   node scripts/analyze.js 13392776413
   ```

### 离线脚本功能
- 读取仓库根目录的 data.js（包含 injData / usdt45Data / usdtFinanceData）
- 输出总览统计（总认购额度、已返款总额、到期未返款、未到期总额）
- 按产品汇总统计
- Top 用户列表（按认购总额排序）
- 支持命令行查询单个用户的详细信息

## 快速开始（后端 API）

### 1. 安装依赖

创建虚拟环境并安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

服务将在 http://localhost:8000 启动

### 3. API 端点

#### 导入数据
```bash
POST /api/import-json
Content-Type: application/json

{
  "injData": [...],
  "usdt45Data": [...],
  "usdtFinanceData": [...]
}
```

示例：
```bash
curl -X POST http://localhost:8000/api/import-json \
  -H "Content-Type: application/json" \
  -d @data.json
```

#### 查询概览
```bash
GET /api/overview
```

示例：
```bash
curl http://localhost:8000/api/overview
```

返回：
```json
{
  "total_subscribed": 123456.78,
  "total_refunded": 0.0,
  "due_not_refunded": 12345.67,
  "not_due_total": 111111.11
}
```

#### 查询用户
```bash
GET /api/user?phone=13392776413
```

示例：
```bash
curl http://localhost:8000/api/user?phone=13392776413
```

返回：
```json
{
  "phone": "13392776413",
  "address": "0x...",
  "product_count": 5,
  "total_subscribed": 5000.0,
  "total_refunded": 0.0,
  "due_not_refunded": 1000.0,
  "not_due_total": 4000.0,
  "products": [...]
}
```

## 前端示例

frontend 目录包含 React + Ant Design 示例组件，演示如何调用 API 接口并渲染退款查询界面。

文件：`frontend/src/components/RefundOverview.jsx`

### 功能特性
- 显示总体概览（卡片展示）
- 支持手机号搜索用户
- 展示用户详细信息（产品数量、累计认购、到期未返款等）
- 表格展示用户购买的所有产品

## 数据模型

### User（用户）
- phone: 手机号（唯一索引）
- address: 地址
- name: 姓名
- created_at: 创建时间

### Purchase（购买记录）
- user_id: 用户ID（外键）
- product_name: 产品名称
- amount: 购买金额
- start_date: 开始时间
- end_date: 结束时间
- daily_return: 每日应返
- status: 状态
- extra: 额外信息
- created_at: 创建时间

## 技术栈

### 后端
- FastAPI - 现代高性能 Web 框架
- SQLModel - SQL 数据库的 Python ORM
- SQLite - 轻量级数据库
- Pydantic - 数据验证

### 前端
- React - UI 库
- Ant Design - UI 组件库

### 离线脚本
- Node.js - JavaScript 运行时

## 注意事项

- 脚本会尝试解析多种日期格式（如 "2026/2/2 13:59"、"1月14日"），并默认把没有年份的日期视为 2026 年。
- 目前没有退款明细，`total_refunded` 默认为 0。如有退款数据可以扩展模型来记录。
- 数据库文件 data.db 会在首次启动时自动创建。
- 建议在生产环境使用 PostgreSQL 或 MySQL 替代 SQLite。

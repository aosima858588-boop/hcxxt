# hcxxt - 简单查询系统 (Simple Query System)

一个简单的数据导入和查询系统，支持CSV和JSON格式的数据导入，并提供后台查询功能。

A simple data import and query system that supports CSV and JSON data import with backend query capabilities.

## 功能特点 (Features)

- ✅ 支持CSV和JSON格式数据导入 (CSV and JSON data import)
- ✅ 基于SQLite的轻量级数据存储 (Lightweight SQLite storage)
- ✅ 灵活的查询接口 (Flexible query interface)
- ✅ 命令行工具支持 (CLI tool support)
- ✅ 简单易用的API (Easy-to-use API)

## 安装 (Installation)

确保已安装Python 3.6或更高版本。此项目无需额外依赖，使用Python标准库即可运行。

Make sure Python 3.6+ is installed. No additional dependencies required - uses Python standard library only.

```bash
git clone https://github.com/aosima858588-boop/hcxxt.git
cd hcxxt
```

## 快速开始 (Quick Start)

### 1. 导入数据 (Import Data)

#### 导入CSV文件 (Import CSV):
```bash
python cli.py import example_data.csv employees
```

#### 导入JSON文件 (Import JSON):
```bash
python cli.py import example_products.json products
```

### 2. 查询数据 (Query Data)

#### 查看表中所有数据 (View all data):
```bash
python cli.py query employees
```

#### 限制返回数量 (Limit results):
```bash
python cli.py query employees --limit 5
```

#### 搜索特定内容 (Search for specific content):
```bash
python cli.py search employees department 技术部
```

### 3. 其他操作 (Other Operations)

#### 列出所有表 (List all tables):
```bash
python cli.py list-tables
```

#### 查看表结构 (View table schema):
```bash
python cli.py schema employees
```

#### 执行自定义SQL查询 (Execute custom SQL):
```bash
python cli.py sql "SELECT * FROM employees WHERE age > 25"
```

## API使用示例 (API Usage Example)

```python
from query_system import QuerySystem

# 初始化查询系统 (Initialize query system)
qs = QuerySystem("data.db")

# 导入CSV数据 (Import CSV data)
qs.import_csv("example_data.csv", "employees")

# 查询所有数据 (Query all data)
results = qs.query_table("employees")
print(results)

# 搜索数据 (Search data)
results = qs.search("employees", "city", "北京")
print(results)

# 执行自定义SQL (Execute custom SQL)
results = qs.query("SELECT * FROM employees WHERE age > ?", (25,))
print(results)

# 关闭连接 (Close connection)
qs.close()
```

## 数据格式示例 (Data Format Examples)

### CSV格式 (CSV Format):
```csv
name,age,city,department
张三,25,北京,技术部
李四,30,上海,销售部
```

### JSON格式 (JSON Format):
```json
[
  {
    "product_id": "P001",
    "product_name": "笔记本电脑",
    "price": "5999",
    "stock": "50"
  }
]
```

## 测试 (Testing)

运行测试用例：
Run test cases:

```bash
python test_query_system.py
```

## 命令行选项 (CLI Options)

```
usage: cli.py [-h] {import,query,search,list-tables,schema,sql} ...

Commands:
  import              Import data from CSV or JSON file
  query               Query all data from a table
  search              Search for specific values in a column
  list-tables         List all tables in the database
  schema              Show table schema
  sql                 Execute custom SQL query

Options:
  --db DB             Database file path (default: data.db)
  --limit LIMIT       Limit number of results (for query command)
```

## 项目结构 (Project Structure)

```
hcxxt/
├── query_system.py          # 核心查询系统类 (Core query system)
├── cli.py                   # 命令行界面 (CLI interface)
├── test_query_system.py     # 测试文件 (Test file)
├── example_data.csv         # 示例CSV数据 (Example CSV data)
├── example_products.json    # 示例JSON数据 (Example JSON data)
└── README.md               # 项目文档 (Documentation)
```

## 技术栈 (Technology Stack)

- Python 3.6+
- SQLite3 (内置标准库 / Built-in standard library)

## 许可证 (License)

MIT License - 详见 LICENSE 文件 (See LICENSE file for details)

## 贡献 (Contributing)

欢迎提交问题和拉取请求！

Issues and pull requests are welcome!
from typing import Any
from flask import Flask, request, jsonify
import logging

# 导入项目中的 search 函数（假设 query_system.py 与 app.py 在同一目录）
from query_system import search

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/query", methods=["POST"])
def query_endpoint():
    """
    POST /query
    Body JSON: {"query": "xxx"}
    Returns:
      - 200: 查询结果（如果 search 返回 dict 或 list，则直接返回该 JSON；否则返回 {"result": ...}）
      - 400: 请求不是 JSON，或缺少/空的 query 字段
      - 500: search 执行出错
    """
    # 必须是 JSON 请求
    if not request.is_json:
        return jsonify({"error": "Request must be application/json"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    query_text = data.get("query")
    if query_text is None or not isinstance(query_text, str) or not query_text.strip():
        return jsonify({"error": 'Field "query" is required and must be a non-empty string'}), 400

    try:
        result = search(query_text)
    except Exception as e:
        app.logger.exception("Error while executing search()")
        # 500 并返回简要错误信息（注意：生产环境下可能不希望泄露内部错误信息）
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    # 如果 search 返回 dict 或 list，直接返回 JSON；
    # 否则把它包入 result 字段返回（确保总是有效的 JSON）
    if isinstance(result, (dict, list)):
        return jsonify(result), 200
    else:
        return jsonify({"result": result}), 200


if __name__ == "__main__":
    # 在开发环境可以使用 debug=True，生产请使用 WSGI 服务器（gunicorn/uwsgi 等）
    app.run(host="0.0.0.0", port=5000, debug=True)

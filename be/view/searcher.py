import json

from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.searcher import Searcher

bp_searcher = Blueprint("searcher", __name__, url_prefix="/searcher")


@bp_searcher.route("/search", methods=["POST"])
def search():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    keyword: str = request.json.get("keyword")
    va: bool = request.json.get("variable")

    se = Searcher()
    #print(se.search(user_id, store_id, keyword))
    if va:
        code, message, pagenum, row, show = se.search(user_id, store_id, keyword)
        #print(code)
        data1 = []
        for item in row:
            data1.append(list(item))
        data2 = []
        for item in show:
            data2.append(list(item))
        return json.dumps({"pagenum": pagenum, "row": data1, "show": data2}), code
    else:
        code, message = se.search(user_id, store_id, keyword)
        return jsonify({"message": message}), code

@bp_searcher.route("/show_pages", methods=["POST"])
def show_pages():
    user_id: str = request.json.get("user_id")
    page: int = request.json.get("page")
    content: str = request.json.get("content")
    va: bool = request.json.get("variable")
    print(va)
    se = Searcher()
    if va:
        code, message, show, row = se.show_pages(user_id, page, content)
        data1 = []
        for item in row:
            data1.append(list(item))
        data2 = []
        for item in show:
            data2.append(list(item))
        return jsonify({"show": data2, "row": data1}), code
    else:
        code, message = se.search(user_id, page, content)
        return jsonify({"message": message}), code

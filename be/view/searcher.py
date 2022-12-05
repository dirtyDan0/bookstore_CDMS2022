from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.searcher import Searcher

bp_searcher = Blueprint("searcher", __name__, url_prefix="/searcher")


@bp_searcher.route("/search", methods=["POST"])
def search():
    print("333333333333")
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    keyword: str = request.json.get("keyword")
    se = Searcher()
    code, pagenum, row, show = se.search(user_id, store_id, keyword)
    return jsonify({"pagenum": pagenum, "row": row, "show": show}), code


@bp_searcher.route("/show_pages", methods=["POST"])
def show_pages():
    user_id: str = request.json.get("user_id")
    page: int = request.json.get("page")
    content: str = request.json.get("content")

    se = Searcher()
    code, show, content1 = se.show_pages(user_id, page, content)
    return jsonify({"show": show, "content": content1}), code

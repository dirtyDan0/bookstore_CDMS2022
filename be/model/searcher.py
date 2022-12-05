from be.model import error
from be.model import db_conn
from be.model.orm_models import Store as Store_model
from be.model.orm_models import Book as book_model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_


class Searcher(db_conn.CheckExist):

    # 题目，作者，标签，简介，目录(title, author, tags, book_intro, content)
    def search(self, user_id: str, store_id: str, keyword: str):
        try:
            # 全站搜索
            if store_id == None:
                if not self.user_id_exist(user_id):
                    return error.error_non_exist_user_id(user_id)

                with self.get_session() as session:
                    row = session.query(book_model.title, book_model.author, book_model.publisher,
                                        book_model.translator,
                                        book_model.pub_year, book_model.pages, book_model.price,
                                        book_model.author_intro,
                                        book_model.book_intro, book_model.tags, book_model.picture) \
                        .join(Store_model, Store_model.book_id == book_model.id) \
                        .filter(Store_model.stock_level > 0, or_(
                        (book_model.title__icontains, keyword), (book_model.author__icontains, keyword),
                        (book_model.tags__icontains, keyword),
                        (book_model.book_intro__icontains, keyword), (book_model.content__icontains, keyword)
                    )).all()

                    if row == None:
                        return error.error_non_exist_search()
                    else:
                        pagenum = len(row) // 5
                        if pagenum == 0:
                            show = row
                        else:
                            page = len(row) % 5
                            if page == 0:
                                pagenum = pagenum
                            else:
                                pagenum += 1
                            show = row.limit(5)
                        # return 200, "ok", pagenum, row, show
            # 店铺搜索
            else:
                if not self.user_id_exist(user_id):
                    return error.error_non_exist_user_id(user_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)

                with self.get_session() as session:
                    row = session.query(book_model.title, book_model.author, book_model.publisher,
                                        book_model.translator,
                                        book_model.pub_year, book_model.pages, book_model.price,
                                        book_model.author_intro,
                                        book_model.book_intro, book_model.tags, book_model.picture) \
                        .join(Store_model, Store_model.book_id == book_model.id) \
                        .filter(Store_model.store_id == store_id, Store_model.stock_level > 0, or_(
                        (book_model.title__icontains, keyword), (book_model.author__icontains, keyword),
                        (book_model.tags__icontains, keyword),
                        (book_model.book_intro__icontains, keyword), (book_model.content__icontains, keyword)
                    )).all()

                    if row == None:
                        return error.error_non_exist_search()
                    else:
                        pagenum = len(row) // 5
                        if pagenum == 0:
                            show = row
                        else:
                            page = len(row) % 5
                            if page == 0:
                                pagenum = pagenum
                            else:
                                pagenum += 1
                            show = row.limit(5)
                        #print(pagenum, row, show)
                        # return 200, "ok", pagenum, row, show

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok", pagenum, row, show

    def show_pages(self, user_id, page, content):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            off = page * 5
            remain = content - off
            if remain > 5:
                show = content.offset(off).limit(5)
            else:
                show = content.offset(off)
            # return 200, "ok", show, content

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok", show, content
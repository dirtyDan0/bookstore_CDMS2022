from be.model import error
from be.model import db_conn
from be.model.orm_models import Store as Store_model,UserStore as UserStore_model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_,or_

class Seller(db_conn.CheckExist):

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            with self.get_session() as session:

                new_store = Store_model(store_id = store_id, book_id=book_id,book_info=book_json_str,stock_level=stock_level)
                session.add(new_store)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            

            with self.get_session() as session:
                store = session.query(Store_model).filter(and_(Store_model.store_id==store_id ,Store_model.book_id == book_id)).one()
                store.stock_level = store.stock_level+add_stock_level
            
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
            with self.get_session() as session:
                new_userstore = UserStore_model(store_id=store_id,user_id=user_id)
                session.add(new_userstore)
                
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

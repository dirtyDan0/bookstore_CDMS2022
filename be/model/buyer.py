import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model.orm_models import Store as Store_model, NewOrderDetail as NewOrderDetail_model, NewOrder as NewOrder_model,User as User_model
from be.model.orm_models import UserStore as UserStore_model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_,or_


class Buyer(db_conn.CheckExist):

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            #new_order 和 new_order_detail 应该在一个session内，这样出错了就能一起rollback
            with self.get_session() as session:

                for book_id, count in id_and_count:                    
                        
                    row = session.query(Store_model.book_id,
                                            Store_model.stock_level,
                                            Store_model.book_info
                                        ).filter(and_(Store_model.store_id == store_id, Store_model.book_id == book_id)).all()

                    if len(row) != 1 :
                        return error.error_non_exist_book_id(book_id) + (order_id, )
                        
                    row = row[0]

                    stock_level = row.stock_level
                    book_info = row.book_info
                    book_info_json = json.loads(book_info)
                    price = book_info_json.get("price")

                    if stock_level < count:
                        return error.error_stock_level_low(book_id) + (order_id,)
                        
                    row = session.query(Store_model).filter(and_(
                        Store_model.store_id==store_id,
                        Store_model.book_id==book_id,
                        Store_model.stock_level>=count)).all()

                        
                    if len(row) != 1:
                        return error.error_stock_level_low(book_id) + (order_id, )

                    row = row[0]
                    row.stock_level = row.stock_level - count

                    session.add(row)

                    new_order_detail = NewOrderDetail_model(order_id=uid, book_id=book_id, count=count, price=price)
                        
                    session.add(new_order_detail)

            
                new_order = NewOrder_model(order_id = uid, store_id = store_id, user_id = user_id)
                session.add(new_order)
                             
                        
            order_id = uid
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):

        try:
            row = None
            with self.get_session() as session:
                row = session.query(NewOrder_model.order_id,NewOrder_model.user_id,
                NewOrder_model.store_id).filter(NewOrder_model.order_id==order_id).all()
                
                if len(row) != 1:
                    return error.error_invalid_order_id(order_id)  
                
            row = row[0]
            order_id = row.order_id
            buyer_id = row.user_id
            store_id = row.store_id
            
            if buyer_id != user_id:
                return error.error_authorization_fail()
                

            with self.get_session() as session:
                row = session.query(User_model.balance,User_model.password).filter(User_model.user_id == buyer_id).all()
                if len(row) != 1:
                    return error.error_non_exist_user_id(buyer_id)
            

            row = row[0]
            balance = row.balance
            

            if password != row.password:
                return error.error_authorization_fail()
            
            
            with self.get_session() as session:
                row = session.query(UserStore_model.store_id,UserStore_model.user_id).filter(UserStore_model.store_id==store_id).all()

                if len(row) !=1:
                    return error.error_non_exist_store_id(store_id)
            
            row = row[0]
            seller_id = row.user_id
            
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            
            rows = None
            with self.get_session() as session:
                rows = session.query(NewOrderDetail_model.book_id,NewOrderDetail_model.count,NewOrderDetail_model.price).filter(NewOrderDetail_model.order_id==order_id).all()

            total_price = 0
            for row in rows:
                count = row.count
                price = row.price
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            #卖家买家的余额变动、删除new_order(detail)必须在一个session里，这样可以出错了rollback
            with self.get_session() as session:
                buyer = session.query(User_model).filter(and_(User_model.user_id==buyer_id,User_model.balance>=total_price)).all()
                if len(buyer) !=1:
                    return error.error_not_sufficient_funds(order_id)
            
                buyer = buyer[0]
                buyer.balance = buyer.balance-total_price
                session.add(buyer)

                seller = session.query(User_model).filter(User_model.user_id == seller_id).all()
                if len(seller) !=1:
                    return error.error_non_exist_user_id(seller_id)
                
                seller = seller[0]
                seller.balance = seller.balance+total_price
                session.add(seller)
            
            
                new_order = session.query(NewOrder_model).filter(NewOrder_model.order_id==order_id).all()
                if len(new_order) !=1:
                    return error.error_invalid_order_id(order_id)
                session.query(NewOrder_model).filter(NewOrder_model.order_id==order_id).delete()

            
                new_order = session.query(NewOrderDetail_model).filter(NewOrderDetail_model.order_id==order_id).all()
                if len(new_order) ==0:
                    return error.error_invalid_order_id(order_id)
                session.query(NewOrderDetail_model).filter(NewOrderDetail_model.order_id==order_id).delete()
            

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            row = None
            with self.get_session() as session:
                row = session.query(User_model).filter(User_model.user_id == user_id).all()
                
                if len(row) ==0:
                    return error.error_authorization_fail()
                user = row[0]
                if user.password != password:
                    return error.error_authorization_fail()

                
                if len(row) != 1:
                    return error.error_non_exist_user_id(user_id) 
                
                row = row[0]
                row.balance = row.balance + add_value
                
                session.add(row)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

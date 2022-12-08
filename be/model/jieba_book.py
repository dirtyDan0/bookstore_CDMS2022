import jieba
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from be.model.orm_models import Book as book_model

engine = create_engine(
    "postgresql+psycopg2://stu10205501460:Stu10205501460@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10205501460",
    max_overflow=0,
    # 链接池大小
    pool_size=10,
    # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
    pool_timeout=5,
    # 多久之后对链接池中的链接进行一次回收
    pool_recycle=5,
    # 查看原生语句（未格式化）
    echo=True
    )

DBSession = sessionmaker(bind=engine)
session = DBSession()

res = session.query(book_model.id, book_model.title, book_model.author, book_model.tags, book_model.book_intro).all()
c_t = []
c_a = []
c_ta = []
c_b = []
c_i = []
for i in range(0,len(res)):
    c_i.append(res[i][0])
    #分词
    str_t = str(res[i][1])
    c_t.append(' '.join(jieba.cut(str_t, cut_all=False)))
    str_a = str(res[i][2])
    c_a.append(' '.join(jieba.cut(str_a, cut_all=False)))
    str_ta = str(res[i][3])
    c_ta.append(' '.join(jieba.cut(str_ta, cut_all=False)))
    str_b = str(res[i][4])
    c_b.append(' '.join(jieba.cut(str_b, cut_all=False)))

#建gin索引
sql = "UPDATE bookstore_book  \
      SET token = setweight(to_tsvector('simple', %s), 'A') || setweight(to_tsvector('simple', %s), 'B') || setweight(to_tsvector('simple', %s), 'C') || setweight(to_tsvector('simple', %s), 'D') \
       WHERE id = %s"
for i in range(0, len(res)):
    engine.execute(sql, [c_t[i], c_ta[i], c_b[i], c_a[i], c_i[i]])

to = session.query(book_model.token).all()
print(to)

session.close()






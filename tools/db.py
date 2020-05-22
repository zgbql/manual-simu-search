from sqlalchemy import create_engine, Column, Integer, String, DATE, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect


Base = declarative_base()

def init_db():
    Base.metadata.create_all(engine)

def to_dict(self):
    """
    model 对象转 字典
    model_obj.to_dict()
    """
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


Base.to_dict = to_dict

DB_CONNECT_STRING = 'mysql+pymysql://usr_video:Kbxx@2019Vdo@103.205.5.50:3306/dbv_search?charset=utf8'
engine = create_engine(DB_CONNECT_STRING, echo=True)
DB_Session = sessionmaker(bind=engine)
session = DB_Session()

init_db()
class SearchResult(Base):
    """ Site table """
    __tablename__ = "web_searchspider_results"
    __table_args__ = (
        UniqueConstraint('videoUrl'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    platform = Column(String(20), nullable=False)
    keyword = Column(String(50), nullable=False)
    targetUrl = Column(String(500))
    coverUrl = Column(String(500))
    videoUrl = Column(String(500), unique=True, nullable=False)
    targetTitle = Column(String(500))
    createDate = Column(DATE(), nullable=False)
    status = Column(Integer, nullable=True, default=0)
    classify = Column(String(10), nullable=True, default='视频平台')
    timeSpan = Column(Integer)
    publishDate = Column(DATE())
    author = Column(String(50))
    authorId = Column(String(100))
    lookCount = Column(Integer)
    searchTaskId = Column(Integer)

class AppResult(Base):
    __tablename__ = "app_searchspider_results"
    __table_args__ = (
        UniqueConstraint('videoUrl'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column(String(20), nullable=False)
    platform = Column(String(20), nullable=False)
    keyword = Column(String(50), nullable=False)
    targetUrl = Column(String(500))
    coverUrl = Column(String(500))
    videoUrl = Column(String(500), unique=True, nullable=False)
    targetTitle = Column(String(500))
    createDate = Column(DATE(), nullable=False)
    status = Column(Integer, default=0)
    timeSpan = Column(Integer)
    publishDate = Column(DATE())
    author = Column(String(50))
    authorId = Column(String(100))
    lookCount = Column(Integer)
    searchTaskId = Column(Integer)
    tortStatus = Column(Integer)

class AppHuoShanAuthor(Base):
    __tablename__ = "app_huoshan_author"
    __table_args__ = (
        UniqueConstraint('authorId'),
    )
    id = Column(String(50), primary_key=True, nullable=False)
    authorId = Column(String(255), nullable=False)
    keyword = Column(String(50), nullable=False)


class AppAuthor(Base):
    __tablename__ = "app_author2019"
    __table_args__ = (
        UniqueConstraint('authorId'),
    )
    id = Column(String(50), primary_key=True, nullable=False)
    authorId = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    keyword = Column(String(50), nullable=False)
    status = Column(Integer)
class ShortVideoState(Base):
    """ Site table """
    __tablename__ = "short_video_crawl_state"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    keyword = Column(String(200), nullable=False)
    sId = Column(String(200), nullable=False, default=0)
    platform = Column(String(20), nullable=False)
    status = Column(Integer, nullable=False)
    json = Column(String(2000), nullable=False)


    @staticmethod
    def update(id, platform):
        result = ShortVideoState.query.filter(ShortVideoState.id == id and ShortVideoState.platform == platform).first()
        if result is not None:
            result.finishNum = 1
            session.commit()

    def get_crawl_lists(**params):
        status = params["status"]
        platform = params["platform"]

        condition = [
        ]
        if platform:
            condition.append(ShortVideoState.platform == platform)
        if status:
            condition.append(ShortVideoState.status == status)
        try:
            rows = session.query(ShortVideoState.id, ShortVideoState.keyword, ShortVideoState.json).filter(*condition).limit(100).all()
            session.commit()
            return rows
        except Exception as e:
            session.rollback()
            raise e

    def edit_status(id, data):

        return edit(ShortVideoState, id, data)
class State(Base):
    """ Site table """
    __tablename__ = "movie_crawl_state"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    keyword = Column(String(200), nullable=False)
    sId = Column(String(200), nullable=False, default=0)
    main = Column(Integer, nullable=False, default=1)
    platform = Column(String(20), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(Integer, nullable=False)
    json = Column(String(2000), nullable=False)
    finishNum = Column(Integer)

    @staticmethod
    def update(id, platform):
        result = State.query.filter(State.id == id and State.platform == platform).first()
        if result is not None:
            result.finishNum = 1
            session.commit()

    def get_crawl_lists(**params):
        status = params["status"]
        platform = params["platform"]

        condition = [
        ]
        if platform:
            condition.append(State.platform == platform)
        if status:
            condition.append(State.status == status)
        try:
            rows = session.query(State.id, State.keyword, State.json).filter(*condition).distinct()
            session.commit()
            return rows
        except Exception as e:
            session.rollback()
            raise e

    def edit_status(id, data):

        return edit(State, id, data)

def insert_rows(model_name, data_list):
    """
    批量插入数据（遇到主键/唯一索引重复，忽略报错，继续执行下一条插入任务）
    注意：
    Warning: Duplicate entry
    警告有可能会提示：
    UnicodeEncodeError: 'ascii' codec can't encode characters in position 17-20: ordinal not in range(128)
    处理：
    import sys

    reload(sys)
    sys.setdefaultencoding('utf8')

    sql 语句大小限制
    show VARIABLES like '%max_allowed_packet%';
    参考：http://dev.mysql.com/doc/refman/5.7/en/packet-too-large.html

    :param model_name:
    :param data_list:
    :return:
    """
    try:
        result = session.execute(model_name.__table__.insert().prefix_with('IGNORE'), data_list)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise e

def edit(model_name, pk_id, data):
    """
    修改信息
    :param model_name:
    :param pk_id:
    :param data:
    :return: Number of affected rows (Example: 0/1)
    """
    model_pk = inspect(model_name).primary_key[0]
    try:
        model_obj = session.query(model_name).filter(model_pk == pk_id)
        result = model_obj.update(data)
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e
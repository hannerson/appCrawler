from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,BigInteger,SmallInteger,String,ForeignKey,DateTime,UniqueConstraint,Text,Boolean,Time,Float
from sqlalchemy.orm import relationship,sessionmaker
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import insert

settings = get_project_settings()
#print (settings.get("MYSQL_USER"),settings.get("MYSQL_PORT"))
#engine = create_engine("mysql+pymysql://cpmin:4K538rL3xrYn8Y@10.0.77.12:3306/cpinfo_monitor?charset=utf8", pool_size=5, pool_timeout=30)
engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"), settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"), settings.get("MYSQL_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)

Base = declarative_base()

@compiles(insert)
def append_string(insert, compiler, **kw):
	s = compiler.visit_insert(insert, **kw)
	if 'append_string' in insert.kwargs:
		return s + " " + insert.kwargs['append_string']
	return s

class cpmKeywords(Base):
	__tablename__ = "cpm_keywords"
	id = Column(BigInteger,primary_key=True)
	keyword = Column(String)
	creator = Column(String)

class cpmKeywordsGrab(Base):
	__tablename__ = "cpm_keywords_grab"
	id = Column(Integer,primary_key=True)
	keyword_id = Column(BigInteger)
	keyword = Column(String)
	creator = Column(String)
	source_id = Column(String)
	name = Column(String)
	artist = Column(String)
	source_name = Column(String)
	play_num = Column(BigInteger)
	sub_num = Column(BigInteger)
	fans_num = Column(BigInteger)
	fav_num = Column(BigInteger)
	comment_num = Column(BigInteger)
	finished = Column(Integer)
	fee_type = Column(Integer)
	intro = Column(Text)
	created_at = Column(DateTime)
	UniqueConstraint('keyword_id', 'source_id', 'source_name', name='keyword_source')

SQLSession = sessionmaker(bind=engine)

#session = scoped_session(SQLSession)
#print (session.query(cpmKeywords.id,cpmKeywords.keyword).all()[0][0])

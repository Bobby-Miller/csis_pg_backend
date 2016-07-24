from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import pyodbc
import warnings


def connect():
    server = 'ZIRSYSPRO'
    db = 'MAINTDATA'
    return pyodbc.connect('DRIVER={SQL Server};SERVER=' + server +
                          ';DATABASE=' + db + ';Trusted_Connection=yes')

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    engine = create_engine('mssql://', creator=connect)
connection = engine.connect()

Base = declarative_base()

class CSISCurrent(Base):
    __tablename__ = 'csis_current'

    id = Column(Integer, primary_key=True)
    batch_id = Column(String(50))
    total = Column(Integer)
    passed = Column(Integer)
    failed = Column(Integer)
    failed_od = Column(Integer)
    backwards = Column(Integer)
    n_a = Column(Integer)
    lost_homing = Column(Integer)
    batch_homes = Column(Integer)


Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


if __name__ == '__main__':
    print("got through")

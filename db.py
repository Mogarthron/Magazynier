from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime as dt

Base = declarative_base()

class Dostawy_pianek(Base):
    __tablename__ = "Dostawy_pianek"

    nr_dost = Column("nr_dost", String(10), unique=True, primary_key=True)
    data_dost = Column("data_dostawy", String(10))
    # data_wprowadzenia = Column("data_wprowdzenia", DateTime, default=dt.utcnow)
    opis = Column("opis", String(150))
    przyjeta = Column("przyjeta", Boolean, default=0)

    def __init__(self, nr_dost, data_dost, opis, przyjeta=0):
        self.nr_dost = nr_dost
        self.data_dost = data_dost,
        self.opis = opis
        self.przyjeta = przyjeta
    
    def __repr__(self):
        return f"{self.nr_dost}: {self.opis}"

class Magazyn(Base):
    __tablename__ = "Magazyn"

    id_mag = Column("id_mag", Integer, primary_key=True, autoincrement=True)
    nazwa_mag = Column("nazwa_magazynu", String(50))
    opis = Column("opis", String(150))

    def __init__(self, nazwa_mag, opis=None):
        self.nazwa_mag = nazwa_mag
        self.opis = opis

    def __repr__(self):
	    return f"({self.id_mag}), {self.nazwa_mag}, {self.opis}"


class Regal(Base):
    __tablename__ = "Regal"

    id_regal = Column("id_regal", Integer, primary_key=True, autoincrement=True)
    ilosc_rzedow = Column("ilosc_rzedow", Integer)
    ilosc_kolumn = Column("ilosc_kolumn", Integer)
    opis = Column("opis", String(150))
    id_mag = Column("id_mag", Integer)

    def __init__(self, ilosc_r, iloslc_c, opis, id_mag):
        self.ilosc_rzedow = ilosc_r
        self.ilosc_kolumn = iloslc_c
        self.opis = opis
        self.id_mag = id_mag

    def __repr__(self):
        return f"({self.id_mag}), {self.opis}, ilosc półek: {self.ilosc_kolumn*self.ilosc_rzedow}"

engine = create_engine("sqlite:///mydb.db", echo=True)
Base.metadata.create_all(bind=engine)
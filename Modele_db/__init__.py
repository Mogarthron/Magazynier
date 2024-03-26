from sqlalchemy import create_engine, text
from sqlalchemy import update, insert, delete
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from Modele_db import *

import json

with open("linki.json", "r") as f:
  gen_link = json.load(f)["generatory_path"]

engine = create_engine("sqlite:///"+gen_link, echo=False)

Base = declarative_base()


Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

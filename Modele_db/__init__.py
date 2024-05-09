from sqlalchemy import create_engine, text
from sqlalchemy import update, insert, delete

from sqlalchemy.orm import sessionmaker, declarative_base


import json

with open("linki.json", "r") as f:
  gen_link = json.load(f)["generatory_path"]

engine = create_engine("sqlite:///"+gen_link, echo=False)

Base = declarative_base()

#Ty był Base.metadata.create_all(bind=engine)

from Modele_db import *
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

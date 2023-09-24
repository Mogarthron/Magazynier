from sqlalchemy.orm import sessionmaker
from db import Magazyn, Regal, Dostawy_pianek, engine
from datetime import datetime as dt

Session = sessionmaker(bind=engine)
session = Session()

# mag2 = Magazyn("Magazyn 2", "kakakaiia")

session.add(Dostawy_pianek("23/0578", "2023-09-25", "AMA"))
session.add(Dostawy_pianek("23/0878", "2023-10-05", "STO"))
session.add(Dostawy_pianek("23/1578", "2023-10-12", "ELI"))

# session.add(Magazyn("Magazyn 1", "kaka;lskd"))
# session.add(Magazyn("Magazyn 2", "kakakaiia"))
# session.add(Magazyn("Magazyn 3", "kakakaiia"))
# session.add(Magazyn("Magazyn 4", "kakakaiia"))
# session.add(Magazyn("Magazyn 5", "kakakaiia"))
# session.add(Regal(5,15,"regał 1 mag 1", 1))
session.commit()

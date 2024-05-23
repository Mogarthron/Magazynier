from Modele_db.modele_db import session, AKTYWNE_DOSTAWY, ZAM_PIANKI 
from Modele_db import engine
from Pianki.Dostawy_pianek import obietosci_samochodow

from sqlalchemy import text
import pandas as pd


nr_zam = [nzam[0] for nzam in session.query(AKTYWNE_DOSTAWY.nr_zam).filter(AKTYWNE_DOSTAWY.aktywna != 11).all()]

_akt_zam1 = session.query(ZAM_PIANKI.zam1, ZAM_PIANKI.nr_partii, ZAM_PIANKI.nr_samochodu, ZAM_PIANKI.potw_dos1).filter(ZAM_PIANKI.zam1.in_(nr_zam)).all()
_akt_zam2 = session.query(ZAM_PIANKI.zam2, ZAM_PIANKI.nr_partii, ZAM_PIANKI.nr_samochodu, ZAM_PIANKI.potw_dos2).filter(ZAM_PIANKI.zam2.in_(nr_zam)).all()

akt_zam1 = pd.DataFrame([[r[0], r[1], r[2].split(",")[0]] for r in _akt_zam1], columns=["nr_zam", "nr_partii", "nr_samochodu"]).drop_duplicates()
akt_zam2 = pd.DataFrame([[r[0], r[1], r[2].split(",")[-1]] for r in _akt_zam2], columns=["nr_zam", "nr_partii", "nr_samochodu"]).drop_duplicates()

def staus(x):
    st = session.query(AKTYWNE_DOSTAWY.aktywna).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0]
    if st == 0:
        return "NIE POTWIERDZONY"
    elif st == 1:
        return "POTWIERDZONO"
    elif st == 2:
        return "DOSTARCZONY CZĘŚCIOWO"
    elif st == 10:
        return "DOSTARCZONO CAŁKOWICIE"
    
akt_zam1["STATUS"] = akt_zam1.nr_zam.apply(staus)
akt_zam2["STATUS"] = akt_zam2.nr_zam.apply(staus)

akt_zam1["NR_PARTII"] = akt_zam1.nr_samochodu.apply(lambda x: ", ".join(akt_zam1[akt_zam1.nr_samochodu == x]["nr_partii"].values.tolist()))
akt_zam2["NR_PARTII"] = akt_zam2.nr_samochodu.apply(lambda x: ", ".join(akt_zam2[akt_zam2.nr_samochodu == x]["nr_partii"].values.tolist()))


akt_zam1["DATA_ZAMOWIENIA"] = akt_zam1.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.data_zamowienia).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam1["DATA_POTWIERDZENIA"] = akt_zam1.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.data_potwierdzenia_zamowienia).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam1["DATA_DOSTAWY"] = akt_zam1.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.preferowana_data_dostawy).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam1["OCZEKIWANIE_NA_POTWIEDZENIE"] = ""

akt_zam2["DATA_ZAMOWIENIA"] = akt_zam2.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.data_zamowienia).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam2["DATA_POTWIERDZENIA"] = akt_zam2.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.data_potwierdzenia_zamowienia).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam2["DATA_DOSTAWY"] = akt_zam2.nr_zam.apply(lambda x: session.query(AKTYWNE_DOSTAWY.preferowana_data_dostawy).filter(AKTYWNE_DOSTAWY.nr_zam == x).all()[0][0])
akt_zam2["OCZEKIWANIE_NA_POTWIEDZENIE"] = ""

kolumny_do_dostaw_pianek = ["DATA_ZAMOWIENIA", "OCZEKIWANIE_NA_POTWIEDZENIE", "DATA_POTWIERDZENIA", "DATA_DOSTAWY", "NR_PARTII", "nr_samochodu", "STATUS"]

akt_zam1_zam2 = pd.concat([akt_zam1, akt_zam2])[["DATA_ZAMOWIENIA", "OCZEKIWANIE_NA_POTWIEDZENIE", "DATA_POTWIERDZENIA", "DATA_DOSTAWY", "NR_PARTII", "nr_samochodu", "STATUS"]].sort_values("nr_samochodu")


tabelka_dostawy_pianek = [[y for y in x[1:]] for x in akt_zam1_zam2.drop_duplicates("nr_samochodu").itertuples()]

zp_tab = []

for i in tabelka_dostawy_pianek:
    with engine.begin() as conn:
                
        _zp_tab = conn.execute(text(f"""SELECT LP, TYDZIEN, KOD, MODEL, NR_KOMPLETACJI, OPIS,
                                                ILE_ZAMOWIONE, ZNACZNIK_DOSTAWCY, GALANTERIA, SIEDZISKA_HR,
                                                LENIWA, ZAM1, ZAM2, UWAGI, POTW_DATA_DOS_1, POTW_DATA_DOS_2,
                                                nr_SAMOCHODU, nr_PARTII 
                                        FROM ZAM_PIANKI WHERE NR_SAMOCHODU LIKE '%{i[-2]}%' AND NR_PARTII IS NOT NULL""")).all()
            
    zp_tab += _zp_tab

zp_tab = pd.DataFrame(zp_tab, columns="LP,TYDZIEN,KOD,MODEL,NR_KOMPLETACJI,OPIS,ILE_ZAMOWIONE,ZNACZNIK_DOSTAWCY,GALANTERIA,SIEDZISKA_HR,LENIWA,ZAM1,ZAM2,UWAGI,POTW_DATA_DOS_1,POTW_DATA_DOS_2,nr_SAMOCHODU,nr_PARTII".split(",")) 

zp_tab["KOMPLETACJA"] = zp_tab["MODEL"] + " " + zp_tab["NR_KOMPLETACJI"]
zp_tab["nr_SAMOCHODU"].fillna("", inplace=True)
zp_tab.drop_duplicates(inplace=True)

# akt_dos = session.query(AKTYWNE_DOSTAWY.nr_zam, AKTYWNE_DOSTAWY.dostawca, AKTYWNE_DOSTAWY.data_zamowienia, AKTYWNE_DOSTAWY.preferowana_data_dostawy, AKTYWNE_DOSTAWY.aktywna).filter(AKTYWNE_DOSTAWY.aktywna != 11).all()    
akt_dos = session.query(AKTYWNE_DOSTAWY.dostawca).filter(AKTYWNE_DOSTAWY.aktywna != 11).all()    

df = pd.concat([
        obietosci_samochodow(x, zp_tab).groupby(
                ["SAMOCHOD", "KOMPLETACJA"]).sum()[
                    ["OBJ","GAL_OBJ","SHR_OBJ","LEN_OBJ"]].reset_index() for x in {x[0] for x in akt_dos}    
        ]
        ).reset_index(drop=True)



for t in tabelka_dostawy_pianek: 
    t.append(f"{df[df.SAMOCHOD == t[-2]].OBJ.sum():.0f}") 

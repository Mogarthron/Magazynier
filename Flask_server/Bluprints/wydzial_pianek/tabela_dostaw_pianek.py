from Modele_db.modele_db import session, AKTYWNE_DOSTAWY 
from Modele_db import engine
from Pianki.Dostawy_pianek import obietosci_samochodow

from sqlalchemy import text
import pandas as pd



tabelka_dostawy_pianek = [
        #Data zamó[wienia], oczekiwnie na potwierdzenie, data potwierdzenia, data dostawy, nr_partii, nr_samochodu, status, obietosc
        ["2024-04-05", "", "", "2024-05-10", "13/01, 14/01", "PIANPOL 10_24", "DOSTARCZONY CAŁKOWICIE"],
        ["2024-03-27", "", "", "2024-05-17", "13/01", "VITA 08_24", "DOSTARCZONY CAŁKOWICIE"],
        ["2024-05-08", "", "", "2024-06-07", "19/01", "PIANPOL 11_24", "POTWIERDZONY"],
        ["2024-05-08", "", "", "2024-06-07", "19/02", "PIANPOL 12_24", "POTWIERDZONY"],
        ["2024-05-17", "", "", "2024-06-21", "20/01", "PIANPOL 13_24", "NIE POTWIERDZONY"],
    ]

akt_dos = session.query(AKTYWNE_DOSTAWY.nr_zam, AKTYWNE_DOSTAWY.dostawca, AKTYWNE_DOSTAWY.data_zamowienia, AKTYWNE_DOSTAWY.preferowana_data_dostawy).filter(AKTYWNE_DOSTAWY.aktywna != 11).all()
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

    

df = pd.concat([
        obietosci_samochodow(x, zp_tab).groupby(
                ["SAMOCHOD", "KOMPLETACJA"]).sum()[
                    ["OBJ","GAL_OBJ","SHR_OBJ","LEN_OBJ"]].reset_index() for x in {x[1] for x in akt_dos}    
        ]
        ).reset_index(drop=True)



for t in tabelka_dostawy_pianek: 
    t.append(f"{df[df.SAMOCHOD == t[-2]].OBJ.sum():.0f}") 

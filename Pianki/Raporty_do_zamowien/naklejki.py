from Modele_db.modele_db import engine, text

def naklejki_na_paczki_pianek(zam1):
    with engine.begin() as conn:
        zp = conn.execute(text(f"""SELECT MODEL, NR_KOMPLETACJI, OPIS, ILE_ZAMOWIONE,
                        ZAM1, ZAM2, UWAGI from ZAM_PIANKI WHERE ZAM1 in('{zam1}') --AND OPIS NOT LIKE '%AVANT%'"""))
    
    zam_pianki = zp.fetchall()
    zam_pianki

    zam_list = list()
    for r in zam_pianki:
        for i in range(r[3]):
            nr = f"{r[0]}, {r[1]}, {r[2].replace(r[0], '').replace(',','.').strip()}, {r[-1].split(',')[0].replace('nr_partii: ', '')}, {i+1}/{r[3]}\n"
        
            zam_list.append(nr)

    zam_list[-1] = zam_list[-1].replace("\n", "")


    fi = open(f"NAKLEJKI_{zam1.replace('/', '_')}.csv", "w")
    
    fi.writelines(zam_list)
    fi.close()
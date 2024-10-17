from reportlab.pdfgen.canvas import Canvas
# from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab_qrcode import QRCodeImage
from datetime import datetime as dt
from Modele_db.modele_db import session, OWATY, baza_PIANKI, ZAM_PIANKI, KOMPLETY_PIANEK, TRANSPORTY, TRANSPORTY_POZYCJE, INSTRUKCJA_ZAMAWIANIA
from sqlalchemy import func
from sqlalchemy.orm import aliased

import pandas as pd

import os


def kj_paczki(paczki, opis):
    """
    return czas, paczki kj
    
    """
    try:
        czas = session.query(KOMPLETY_PIANEK.preferowany_czas_kj).filter(KOMPLETY_PIANEK.opis == opis).first()[0]
        
        if paczki <= 10:
            return 1 * czas, 1
        elif paczki > 10 and paczki <= 20:
            return 2 * czas, 2
        elif paczki > 21 and paczki <= 30:
            return 3 * czas, 3
        elif paczki > 31 and paczki <= 40:
            return 4 * czas, 4
        elif paczki > 41 and paczki <= 60:
            return 5 * czas, 5
        elif paczki > 61 and paczki <= 80:
            return 6 * czas, 6
        elif paczki > 81 and paczki <= 100:
            return 7 * czas, 7
        elif paczki > 101 and paczki <= 120:
            return 8 *czas, 8
        else:
            return 10 * czas, 10
    except:
        print(paczki, opis)
        return 0, 0
    
def dokladanie_owat_i_pianek(paczki, model, opis):

    memory = ["STONE", "AVANT", "HORIZON", "REVERSO"]

    try:
        czas = session.query(KOMPLETY_PIANEK.preferowany_czas_pakowania).filter(KOMPLETY_PIANEK.opis == opis).first()[0]
    except:
        print(opis, 0)
        czas = 0

    if model not in memory:
        return paczki * czas
    return 0

def dokladanie_owat_pianek_memory(paczki, model, opis):

    memory = ["STONE", "AVANT", "HORIZON", "REVERSO"]

    try:        
        czas = session.query(KOMPLETY_PIANEK.preferowany_czas_pakowania_memory).filter(KOMPLETY_PIANEK.opis == opis).first()[0]
    except:
        print(opis, 0)
        czas = 0
    if model in memory:
        return paczki * czas
    return 0

def wycinanie_owat(paczki, opis):
    
    try:
        return int(session.query(func.sum(OWATY.ZUZYCIE)).filter(OWATY.OPIS == opis).all()[0][0] * paczki * 1.5)
    except:
        print(opis, paczki)
        return 0

def kompletacja_owat(wycinanie, ile_zam):
    if wycinanie == 0:
        return 0
    
    return ile_zam * 1.5

def dane_zam_pianki_czasy(nr_partii:str):
    """
    Zwraca tablekę z policzonymi czasami dla pozycji zamówionych w danym tygodniu

    nr_partii -> numer partii przydzielony do zamowienia
    """
    # TP = aliased(TRANSPORTY)
    # TPP = aliased(TRANSPORTY_POZYCJE)
    ZP = aliased(ZAM_PIANKI)

    dostawa = pd.DataFrame(session.query(
    
        ZP.nr_partii, 
        ZP.nr_kompletacji, 
        ZP.model,
        ZP.opis,     
        ZP.zam1,
        ZP.zam2,
        ZP.ile_zam
    
    ).filter(
        ZP.nr_partii == nr_partii 
          
    ).all(), columns=["NR_PARTII", "NR_KOMPLETACJI", "MODEL", "OPIS", "ZAM1", "ZAM2", "ILE_ZAM"])



    dostawa["KJ"] = dostawa.apply(lambda x: kj_paczki(x.ILE_ZAM, x.OPIS)[0], axis=1)
    dostawa["KJ_PACZKI"] = dostawa.apply(lambda x: kj_paczki(x.ILE_ZAM, x.OPIS)[1], axis=1)
    dostawa["WYCINANIE_OWAT"] = dostawa.apply(lambda x: wycinanie_owat(x.ILE_ZAM, x.OPIS), axis=1)
    dostawa["DOKLADANIE_OWAT_I_PIANEK"] = dostawa.apply(lambda x: dokladanie_owat_i_pianek(x.ILE_ZAM, x.MODEL, x.OPIS), axis=1)
    dostawa["DOKLADANIE_OWAT_PIANEK_I_MEMORY"] = dostawa.apply(lambda x: dokladanie_owat_pianek_memory(x.ILE_ZAM, x.MODEL, x.OPIS), axis=1)
    dostawa["KOMPLETACJA_OWAT"] = dostawa.apply(lambda x: kompletacja_owat(x.WYCINANIE_OWAT, x.ILE_ZAM), axis=1)

    return dostawa

def zlecenie_produkcyjne(cnvs:Canvas, zlecenie_prod, nr_partii, nr_kompl, model, opis, ilosc_paczek, czas_zalozony):
    """
    funkcja rysujaca zlecenie produkcyjne
    """
    # canvas = Canvas("raport_zamówień.pdf")#, pagesize=landscape(letter))
    cnvs.setPageSize((29.7*cm,21*cm))

    cnvs.setFont(psfontname="Helvetica", size=9)
    cnvs.drawString(2*cm, 19*cm, f"ZLECENIE PRODUKCYJNE: {zlecenie_prod}")
    cnvs.drawString(20*cm, 19*cm, f"DZIEN WYDRUKU: {dt.now().strftime('%Y-%m-%d')}")
    
    cnvs.setFont(psfontname="Helvetica-Bold", size=16)
    cnvs.drawString(2*cm, 17*cm, f"NR PARTII: {nr_partii}")
    cnvs.drawString(2*cm, 16*cm, f"NR ZAMOWIENIA: {model} {nr_kompl}")
    cnvs.drawString(2*cm, 15*cm, f"MODEL: {model}")

    
    
    if zlecenie_prod == "KOMPLETACJA OWAT" or zlecenie_prod == "WYDZIAL ROZKROJ OWAT":   
        
        cnvs.setFont(psfontname="Helvetica", size=11)
        cnvs.drawString(16*cm, 16*cm, f"TYP")
        cnvs.drawString(17*cm, 16*cm, f"MB")
        cnvs.drawString(18.5*cm, 16*cm, f"R/K")
        cnvs.drawString(19.5*cm, 16*cm, f"KATER_UKL")

        # cnvs.line(16*cm, 10*cm, 26*cm, 10*cm)
        wysokosc_wiersza = 15.5
        for r in session.query(OWATY.TYP_OWATY, OWATY.ZUZYCIE*ilosc_paczek*1.1, OWATY.RODZAJ_CIECIA, OWATY.NAZWA_UKL).filter(OWATY.OPIS.like(f"%{opis}%")).all():
            cnvs.drawString(16*cm, wysokosc_wiersza*cm, f"{r[0]}")
            cnvs.drawString(17*cm, wysokosc_wiersza*cm, f"{r[1]:.0f}")
            cnvs.drawString(18.5*cm, wysokosc_wiersza*cm, f"{r[2]}")
            cnvs.drawString(19.5*cm, wysokosc_wiersza*cm, f"{r[3]}")  
            wysokosc_wiersza -= 0.5

        qr_msg =f"13\n KOMPLETACJA OWAT NR PARTII {nr_partii}: {opis} - {ilosc_paczek}szt| KOMPLETACJA {nr_kompl}\n {dt.now().strftime('%Y-%m-%d')}\n {czas_zalozony}"        

    if zlecenie_prod == "DOKLADANIE PIANEK I OWAT":
        qr_msg =f"3\n DOKLADANIE OWAT I PIANEK NR PARTII {nr_partii}: {opis} - {ilosc_paczek}szt| KOMPLETACJA {nr_kompl}\n {dt.now().strftime('%Y-%m-%d')}\n {czas_zalozony}"        

    if zlecenie_prod == "DOKLADANIE PIANEK, OWAT I MEMORY":
        cnvs.setFont(psfontname="Helvetica", size=8)

        bryla_gen = session.query(KOMPLETY_PIANEK.bryla_gen).filter(KOMPLETY_PIANEK.opis == opis).all()[0][0]
       
        wysokosc_wiersza = 6
        for r in session.query(baza_PIANKI.NUMER, baza_PIANKI.ilosc, baza_PIANKI.WYMIAR).filter(baza_PIANKI.MODEL == model, baza_PIANKI.BRYLA == bryla_gen, baza_PIANKI.TYP == "G-401").all():
            cnvs.drawString(2*cm, wysokosc_wiersza*cm, ", ".join(map(str, r)))           

            wysokosc_wiersza -= 0.4
        
        qr_msg =f"4\n DOKLADANIE OWAT, PIANEK I MEMORY NR PARTII {nr_partii}: {opis} - {ilosc_paczek}szt| KOMPLETACJA {nr_kompl}\n {dt.now().strftime('%Y-%m-%d')}\n {czas_zalozony}"        

    if zlecenie_prod != "WYDZIAL ROZKROJ OWAT":
        qr = QRCodeImage(qr_msg, size=3.5*cm, border=1)
        qr.drawOn(cnvs, 2*cm, 10.5*cm)

    cnvs.line(2*cm, 10*cm, 26*cm, 10*cm)

    tabelka = [["BRYLA", "ILOSC PACZEK", "CZAS", "CZAS ZALOZONY\n[MIN]"],
               [opis, ilosc_paczek, "", czas_zalozony]]
    
    
    table = Table(tabelka, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))


    table.wrapOn(cnvs, 2*cm, 7*cm)
    table.drawOn(cnvs, 2*cm, 7*cm)

    cnvs.setFont(psfontname="Helvetica", size=10)
    cnvs.drawString(2*cm, 3*cm, "UWAGI:")
    cnvs.drawString(25*cm, 3*cm, "PODPIS DZIEN:")

def raport_kontroli_jakosci(cnvs:Canvas, zlecenie_prod, nr_partii, nr_zam, nr_kompl, model, opis, ilosc_paczek, czas_zalozony):
    
    cnvs.setPageSize((29.7*cm,21*cm))

    cnvs.setFont(psfontname="Helvetica", size=9)

    cnvs.drawString(25*cm, 20*cm, f"NR PARTII: {nr_partii}")
    cnvs.drawString(25*cm, 19.5*cm, f"NR DOS: {nr_zam}")
    cnvs.drawString(25*cm, 15*cm, f"CZAS ZALOZONY: {czas_zalozony}min")

    cnvs.setFont(psfontname="Helvetica-Bold", size=17)
    cnvs.drawString(5*cm, 20*cm, f"KONTROLA JAKOSCI {opis} - {ilosc_paczek}szt")

    qr_msg =f"2\n KONTROLA JAKOSCI {nr_partii}: {opis} - {ilosc_paczek}szt| NR DOS {nr_zam}\n {dt.now().strftime('%Y-%m-%d')}\n {czas_zalozony}"        

    
    qr = QRCodeImage(qr_msg, size=3.5*cm, border=1)
    qr.drawOn(cnvs, 25*cm, 15.5*cm)


    tabelka = [["LP", "TYP", "PRZEZ", "OR", "OZN", "PROFIL", "NUMER", "WYMIAR", "+/-", "ILOSC", "DOSTARCZONO/UWAGI"]]

    tab_kj = session.query(baza_PIANKI.TYP, baza_PIANKI.PRZEZ, baza_PIANKI.OR, 
              baza_PIANKI.OZN, baza_PIANKI.PROFIL, baza_PIANKI.NUMER, baza_PIANKI.WYMIAR, baza_PIANKI.TOLERANCJA, baza_PIANKI.ilosc).filter(
                  baza_PIANKI.MODEL == model.replace("_", "/"), 
                  baza_PIANKI.BRYLA == session.query(KOMPLETY_PIANEK.bryla_gen).filter(KOMPLETY_PIANEK.opis == opis).all()[0][0]).all()

    for lp, r in enumerate(tab_kj):
        tabelka.append([lp+1] + [x for x in r])
    
    table = Table(tabelka, colWidths=[1*cm, 1.5*cm, 1.8*cm, 1.5*cm, 1.8*cm, 1.8*cm, 2*cm, 3*cm, 2*cm, 1.5*cm, 5*cm])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    if len(tabelka) >= 20:
        table.wrapOn(cnvs, 20*cm, 18*cm)
        table.drawOn(cnvs, 1*cm, 1*cm)
    elif len(tabelka) > 13 and len(tabelka) < 20:
        table.wrapOn(cnvs, 20*cm, 18*cm)
        table.drawOn(cnvs, 1*cm, 5*cm)
    else:
        table.wrapOn(cnvs, 20*cm, 18*cm)
        table.drawOn(cnvs, 1*cm, 10*cm)

def drukuj_raporty(nr_partii, zlecenie, pozycje, zam="ZAM1", drukuj_do_folderu=True):
    """
    nazwy zkecen:
        * WYDZIAL ROZKROJ OWAT
        * KOMPLETACJA OWAT
        * DOKLADANIE PIANEK I OWAT
        * DOKLADANIE PIANEK, OWAT I MEMORY
        * KONTROLA JAKOSCI
    """
    print(f"drukuj raporty args: {nr_partii}, {zlecenie}, {zam}")
    print(pozycje.shape)
    canvas = Canvas(f"ZLECENIA_PROD/{zlecenie}/{nr_partii.replace('/', '_')} {zlecenie}.pdf") 

    if not os.path.exists(f"./ZLECENIA_PROD/{zlecenie}"):
        os.makedirs(f"./ZLECENIA_PROD/{zlecenie}")
        print("path:", f"ZLECENIA_PROD/{zlecenie}/{nr_partii.replace('/', '_')} {zlecenie}.pdf")
   
    
    def dodaj_zlecenie(kolumna):
        for r in pozycje.iterrows():
        
            if r[1][kolumna] > 0:
                zlecenie_produkcyjne(canvas, zlecenie, r[1].NR_PARTII, r[1].NR_KOMPLETACJI, r[1].MODEL, r[1].OPIS, r[1].ILE_ZAM, r[1][kolumna])
                canvas.showPage()

    if zlecenie == "WYDZIAL ROZKROJ OWAT":
        dodaj_zlecenie("WYCINANIE_OWAT")
      
    if zlecenie == "KOMPLETACJA OWAT":
        dodaj_zlecenie("KOMPLETACJA_OWAT")        
    
    if zlecenie == "DOKLADANIE PIANEK I OWAT":
        dodaj_zlecenie("DOKLADANIE_OWAT_I_PIANEK")        

    if zlecenie == "DOKLADANIE PIANEK, OWAT I MEMORY":
        dodaj_zlecenie("DOKLADANIE_OWAT_PIANEK_I_MEMORY")

    if zlecenie == "KONTROLA JAKOSCI":        
        for r in pozycje.iterrows():        
            raport_kontroli_jakosci(canvas, zlecenie, r[1].NR_PARTII, r[1].NR_KOMPLETACJI, r[1][zam], r[1].MODEL, r[1].OPIS, r[1].KJ_PACZKI, r[1].KJ)
            canvas.showPage()
        

    canvas.save()



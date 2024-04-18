from Pianki.Analiza_pianek import analiza
import pandas as pd

class Podsumowanie_analizy_pianek():
    
    def __init__(self, instrukcja_zamawiania) -> None:
        
        self.ard = {a.MODEL: a for a in instrukcja_zamawiania}
        
        ar_podsum = pd.DataFrame([x.Raport() for x in instrukcja_zamawiania])

        self.Tabela_podsumowania_analizy = ar_podsum.sort_values(by=["GRUPA", "WSPL_DO_ZAM"], ascending=[True,False])

        podsumowanie_VOL = ar_podsum[["OBJ_CIECH",	"OBJ_VITA",	"OBJ_PIANPOL"]].sum()
        podsumowanie_VOL["RAZEM"] = podsumowanie_VOL.sum()

        self.Podsumowanie_obietosci_pianek = podsumowanie_VOL

    def Optymalizuj_auto(dostawca, objetosc):
        pass

    def __getitem__(self, index):
        return self.ard[index]
    
    def __lt__(self, value):
       
        return self.Tabela_podsumowania_analizy[self.Tabela_podsumowania_analizy.WSPL_DO_ZAM < value]
    
    def __gt__(self, value):
       
        return self.Tabela_podsumowania_analizy[self.Tabela_podsumowania_analizy.WSPL_DO_ZAM > value]

    def __repr__(self):
        
        saldo = analiza.SALDO_obj.sum()
        wolne = analiza.WOLNE_obj.sum()
        zamow = analiza.ZAMOWIONE_obj.sum()+analiza.CZEKA_NA_SPAKOWANIE_obj.sum()+analiza.CZESCIOWO_DOSTARCZONE_obj.sum()
        maks = analiza.MAX_obj.sum()

        return self.Podsumowanie_obietosci_pianek.to_string()+"\n---------\n"#+\
            #   f"SALDO\tWOLNE\tMAX\n"+\
            #   f"{saldo:.0f}\t{wolne:.0f}\t{maks:.0f}\n"+\
            #   f"{saldo/maks*100:.0f}%\t{wolne/maks*100:.0f}%\t{(zamow+wolne)/maks*100:.0f}%"

        
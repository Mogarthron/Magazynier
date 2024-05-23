from ..routes import *

@analiza_pianek.route("/dokumentacja_pianek", defaults={"numer": None})
@analiza_pianek.route("/dokumentacja_pianek/<numer>")
def dokumentacja_pianek_numer(numer):

    if numer:
        dokumentacja = [list(x) for x in session.execute(text(f"SELECT MODEL, BRYLA, TYP, PRZEZ, OZN, PROFIL, NUMER, WYMIAR, TOLERANCJA, ilosc FROM baza_PIANKI where NUMER = '{numer}'")).fetchall()]

        return [list(x) for x in dokumentacja]
    else:
        return "DOKUMENTACJA"
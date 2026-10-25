from utils.vypis import hlavicka, clear, nacti_volbu, tisk_chyba, tisk_ok, vytiskni_volbu
from models.fortress import PEVNOSTNI_BUDOVY


def spravovat_pevnost(hra):
    while True:
        clear()
        pevnost = hra.pevnost
        hlavicka('Rozvoj pevnosti')
        print(f"{pevnost.nazev_sidla} — úroveň {pevnost.uroven} | Zásoby: {pevnost.zasoby} | Zlato: {hra.hrac.gold}")
        for ident, data in PEVNOSTNI_BUDOVY.items():
            uroven = pevnost.budovy.get(ident, 0)
            print(f"{ident}) {data['nazev']} úroveň {uroven} — {pevnost.cena_vylepseni(ident)} zlata")
        cena_sidla = pevnost.cena_rozsireni_sidla()
        pokud_rozsireni, zprava_rozsireni = pevnost.podminky_rozsireni_sidla()
        if cena_sidla:
            popis_rozsireni = (
                f"Rozšířit na {pevnost.uroven + 1}. stupeň "
                f"({cena_sidla['zlato']} zl., {cena_sidla['drevo']} dřeva, "
                f"{cena_sidla['kamen']} kamene, {cena_sidla['zelezo']} železa)"
            )
            if not pokud_rozsireni:
                popis_rozsireni += f" — {zprava_rozsireni}"
            vytiskni_volbu("U", popis_rozsireni)
        else:
            print("Sídlo dosáhlo nejvyššího stupně.")
        volba = nacti_volbu({"0", "u", *PEVNOSTNI_BUDOVY})
        if volba == "0":
            return
        ident = None if volba == "u" else volba
        cena = pevnost.cena_vylepseni(ident)
        if ident is None:
            uspech, zprava = pevnost.rozsir_sidlo(hra.hrac)
            (tisk_ok if uspech else tisk_chyba)(zprava)
        elif cena is None:
            tisk_chyba("Neznámá budova.")
        elif hra.hrac.gold < cena:
            tisk_chyba("Nedostatek zlata.")
        elif pevnost.vylepsi(ident, hra.hrac.gold):
            hra.hrac.gold -= cena
            if hasattr(hra, "achievementy"):
                hra.achievementy.zaznamenej("stavba")
            tisk_ok("Pevnost se rozšířila a bonusy jsou aktivní.")
        input("Enter...")

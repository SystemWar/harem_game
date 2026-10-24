# game/obchod.py — zjednodušený obchod + černý trh
from utils.vypis import (
    clear, nacti_volbu, tisk_ok, tisk_chyba, tisk_info, vytiskni_volbu,
)
from config import GOLD, CYAN, MAGENTA, NC


MESTSKY_OBCHOD = (
    ("1", "Léčivý elixír", 30, "HP +20"),
    ("2", "Stimulant", 40, "sex energie +15"),
    ("3", "Temný katalyzátor", 60, "temná energie +15"),
    ("4", "Balíček léčivých bylin", 55, "HP +35"),
    ("5", "Nápoj výdrže", 70, "sex energie +20, max sex +5"),
    ("6", "Osvěžující sůl", 75, "temná energie +20, max temno +5"),
    ("7", "Amulet vitality", 90, "max HP +15 a plné uzdravení"),
    ("8", "Talisman odvahy", 110, "tělo +1 a max HP +10"),
    ("10", "Vůně věrnosti", 95, "+5 loajalita všem aktivním otrokyním"),
    ("11", "Harmonie v domě", 120, "+6 důvěry všem aktivním otrokyním"),
    ("12", "Zlatá pečeť městských kupců", 150, "+8 reputace města a +10 klidu ve městě"),
    ("13", "Městský zásobní balíček", 170, "+12 zlata denně a +5 max HP pro každou aktivní otrokyni"),
    ("14", "Syntetický bonusový prášek", 190, "+10 max sex energie a +12 sex energie okamžitě"),
    ("15", "Sádrový amulet střízlivosti", 210, "+12 temné energie a +10 max temno"),
    ("16", "Kunový talisman cestovatele", 225, "+8 reputace města a +3 loajalita všem partnerkám"),
)


def _aplikuj_vsechny_otrokynim(hra, atribut, hodnoty, max_hodnota=100):
    if not hasattr(hra, "harem"):
        return
    for otrok in hra.harem.vsechny_aktivni():
        aktualni = getattr(otrok, atribut, 0)
        setattr(otrok, atribut, min(max_hodnota, aktualni + int(hodnoty)))


def obchod(hra):
    clear()
    print(f"{GOLD}--- Obchod ---{NC}\n")
    for ident, nazev, cena, popis in MESTSKY_OBCHOD:
        vytiskni_volbu(ident, f'{nazev} ({cena} zl) — {popis}')
    vytiskni_volbu('99', 'Černý trh')
    vytiskni_volbu('0', 'Zpět')
    povolene = {"0", "99"} | {ident for ident, _, _, _ in MESTSKY_OBCHOD}
    try:
        volba = nacti_volbu(
            povolene,
            chybova_zprava="Neplatná volba. Zadej 0, 99 nebo jednu z nabízených položek.",
        )
    except EOFError:
        return
    if volba == "99":
        cerny_trh(hra)
        return
    if volba == "0":
        return

    hrac = hra.hrac
    item = next((i for i in MESTSKY_OBCHOD if i[0] == volba), None)
    if item is None:
        tisk_chyba("Nelze koupit (volba neexistuje).")
    else:
        _, nazev, cena, _ = item
        if hrac.gold < cena:
            tisk_chyba(f"{nazev} stojí {cena} zl, ale nemáš dostatek zlata.")
        else:
            hrac.gold -= cena
            if volba == "1":
                hrac.hp = min(hrac.max_hp, hrac.hp + 20)
                tisk_ok("Elixír vypit. HP +20.")
            elif volba == "2":
                max_s = getattr(hrac, "max_sex", lambda: 100)()
                hrac.sex_energy = min(max_s, hrac.sex_energy + 15)
                tisk_ok("Stimulant. Sex energie +15.")
            elif volba == "3":
                max_t = getattr(hrac, "max_temno", lambda: 100)()
                hrac.dark_energy = min(max_t, hrac.dark_energy + 15)
                tisk_ok("Temný katalyzátor. Temná energie +15.")
            elif volba == "4":
                hrac.hp = min(hrac.max_hp, hrac.hp + 35)
                tisk_ok("Byliny ti pomohly. HP +35.")
            elif volba == "5":
                max_s = getattr(hrac, "max_sex", lambda: 100)()
                hrac.sex_energy = min(max_s, hrac.sex_energy + 20)
                if hasattr(hrac, "zvys_max_sex"):
                    hrac.zvys_max_sex(5)
                else:
                    hrac.max_sex_energy = getattr(hrac, "max_sex_energy", 100) + 5
                tisk_ok("Nápoj výdrže. Sex energie +20 a max sex +5.")
            elif volba == "6":
                max_t = getattr(hrac, "max_temno", lambda: 100)()
                hrac.dark_energy = min(max_t, hrac.dark_energy + 20)
                if hasattr(hrac, "zvys_max_temno"):
                    hrac.zvys_max_temno(5)
                else:
                    hrac.max_dark_energy = getattr(hrac, "max_dark_energy", 100) + 5
                tisk_ok("Osvěžující sůl. Temná energie +20 a max temno +5.")
            elif volba == "7":
                if hasattr(hrac, "max_hp"):
                    hrac.max_hp += 15
                hrac.hp = hrac.max_hp
                tisk_ok("Amulet vitality ti vrátil plnou sílu. Max HP +15.")
            elif volba == "8":
                if hasattr(hrac, "skill_body"):
                    hrac.skill_body += 1
                if hasattr(hrac, "max_hp"):
                    hrac.max_hp += 10
                hrac.hp = min(hrac.max_hp, hrac.hp + 10)
                tisk_ok("Talisman odvahy. Tělo +1, max HP +10.")
            elif volba == "10":
                _aplikuj_vsechny_otrokynim(hra, "loajalita", 5)
                tisk_ok("Vůně věrnosti zvedla loajalitu harému o +5.")
            elif volba == "11":
                _aplikuj_vsechny_otrokynim(hra, "duvera", 6)
                tisk_ok("Harmonie v domě posílila důvěru všech otrokyň o +6.")
            elif volba == "12":
                hra.hrac.reputace_mesta = min(100, getattr(hra.hrac, "reputace_mesta", 0) + 8)
                tisk_ok("Zlatá pečeť městských kupců zvýšila reputaci města o +8.")
            elif volba == "13":
                for otrok in hra.harem.vsechny_aktivni():
                    if hasattr(otrok, "max_hp"):
                        otrok.max_hp = min(220, getattr(otrok, "max_hp", 100) + 5)
                    otrok.hp = min(getattr(otrok, "max_hp", getattr(otrok, "hp", 0)), getattr(otrok, "hp", 0) + 5)
                if hasattr(hra.hrac, "bonus_denni_prijem"):
                    hra.hrac.bonus_denni_prijem = getattr(hra.hrac, "bonus_denni_prijem", 0) + 12
                tisk_ok("Městský zásobní balíček přidal +12 zlata denně a +5 max HP všem aktivním otrokyním.")
            elif volba == "14":
                max_s = getattr(hrac, "max_sex", lambda: 100)()
                hrac.sex_energy = min(max_s, hrac.sex_energy + 12)
                if hasattr(hrac, "zvys_max_sex"):
                    hrac.zvys_max_sex(10)
                else:
                    hrac.max_sex_energy = getattr(hrac, "max_sex_energy", 100) + 10
                tisk_ok("Syntetický bonusový prášek: +12 sex energie a +10 max sex.")
            elif volba == "15":
                max_t = getattr(hrac, "max_temno", lambda: 100)()
                hrac.dark_energy = min(max_t, hrac.dark_energy + 12)
                if hasattr(hrac, "zvys_max_temno"):
                    hrac.zvys_max_temno(10)
                else:
                    hrac.max_dark_energy = getattr(hrac, "max_dark_energy", 100) + 10
                tisk_ok("Sádrový amulet střízlivosti přidal +12 temné energie a +10 max temno.")
            elif volba == "16":
                hra.hrac.reputace_mesta = min(100, getattr(hra.hrac, "reputace_mesta", 0) + 8)
                for otrok in hra.harem.vsechny_aktivni():
                    if getattr(otrok, "partnerka", False):
                        otrok.loajalita = min(100, getattr(otrok, "loajalita", 0) + 3)
                tisk_ok("Kunový talisman cestovatele zvýšil reputaci města o +8 a loajalitu partnerkám o +3.")
            else:
                tisk_chyba("Nelze koupit (volba není podporovaná).")
    try:
        input("Enter...")
    except EOFError:
        pass


def cerny_trh(hra):
    import random
    from game.kronika import zaznamenej
    from models.otrokyne import Otrokyně

    clear()
    print(f"{MAGENTA}--- Černý trh podsvětí ---{NC}")
    kor = getattr(hra.mafie, "korupce", 0)
    temno = getattr(hra.hrac, "dark_energy", 0)

    if kor < 20 and temno < 40:
        tisk_chyba("Podsvětí ti zatím nevěří (požadováno: korupce mafie ≥ 20% nebo temná energie ≥ 40).")
        try:
            input("Enter...")
        except EOFError:
            pass
        return

    print(f"Zlato: {hra.hrac.gold} 🪙 | Temná energie: {temno} | Korupce: {kor}%\n")
    vytiskni_volbu('1', 'Elixír temnoty (80 zl) — +20 temná energie')
    vytiskni_volbu('2', 'Okovy luxusu (120 zl) — +5 loajalita všem otrokyním')
    vytiskni_volbu('3', 'Sérum zlomené vůle (160 zl) — +25 poslušnost a +15 submisivita vybrané otrokyně')
    vytiskni_volbu('4', 'Inkviziční falešný odpustek (180 zl) — zahlazení stop před církví a inkvizicí')
    vytiskni_volbu('5', 'Pašerácká úmluva (220 zl) — dodávka kontrabandu (+300 🪙 okamžitě, +8 vliv ve městě)')
    vytiskni_volbu('6', 'Krvavý ametyst (350 zl) — krystal podsvětí: trvale +10 k max temné energii')
    vytiskni_volbu('7', 'Tajemná dražba z podsvětí (400 zl) — odkup vzácné exotické otrokyně')
    vytiskni_volbu('8', 'Dýmový koktejl (260 zl) — +15 sexuální energie a +5 touha všem aktivním otrokyním')
    vytiskni_volbu('9', 'Neonový skaner (300 zl) — +10 k vlivu ve městě a +8 reputace u cyberpunkáků')
    vytiskni_volbu('10', 'Věnec z šafránových květů (340 zl) — +15 důvěra, +10 loajalita a +5 touha vybrané otrokyně')
    vytiskni_volbu('11', 'Rituál krycího plamene (380 zl) — +20 korupce, +7 vliv ve městě, +5 reputace kultu krvi')
    vytiskni_volbu('0', 'Zpět')

    try:
        v = nacti_volbu(
            {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"},
            chybova_zprava="Neplatná volba. Zadej číslo od 0 do 11.",
        )
    except EOFError:
        return

    hrac = hra.hrac
    if v == "0":
        return

    if v == "1":
        if hrac.gold >= 80:
            hrac.gold -= 80
            if hasattr(hrac, "pridej_dark_energy"):
                hrac.pridej_dark_energy(20)
            else:
                max_t = hrac.max_temno() if hasattr(hrac, "max_temno") else 120
                hrac.dark_energy = min(max_t, hrac.dark_energy + 20)
            tisk_ok("Elixír temnoty vypit. Temná síla proudí v žilách (+20 temno).")
            zaznamenej(hra, "Černý trh: zakoupen Elixír temnoty.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "2":
        if hrac.gold >= 120:
            hrac.gold -= 120
            aktivni = hra.harem.vsechny_aktivni()
            for o in aktivni:
                o.loajalita = min(100, o.loajalita + 5)
                o.poslusnost = min(100, getattr(o, "poslusnost", 30) + 5)
            tisk_ok(f"Okovy luxusu nasazeny. Harém ({len(aktivni)} dívek) je spoután vděkem i řetězy.")
            zaznamenej(hra, "Černý trh: nasazeny Okovy luxusu harému.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "3":
        if hrac.gold >= 160:
            aktivni = hra.harem.vsechny_aktivni()
            if not aktivni:
                tisk_chyba("V harému nemáš žádné otrokyně.")
            else:
                print("\nVyber otrokyni pro aplikaci séra:")
                for i, o in enumerate(aktivni, 1):
                    print(f"{i}) {o.jmeno} (poslušnost: {o.poslusnost}, submisivita: {o.submisivita})")
                try:
                    vyber = nacti_volbu(
                        {"0", *(str(index) for index in range(1, len(aktivni) + 1))},
                        prompt="Vyber otrokyni (0 = zpět): ",
                        chybova_zprava="Neplatné číslo otrokyně.",
                    )
                    if vyber != "0":
                        vybrana_idx = int(vyber) - 1
                        hrac.gold -= 160
                        cil = aktivni[vybrana_idx]
                        cil.poslusnost = min(100, cil.poslusnost + 25)
                        cil.submisivita = min(100, cil.submisivita + 15)
                        cil.strach = max(0, getattr(cil, "strach", 30) - 10)
                        tisk_ok(f"Sérum aplikováno na {cil.jmeno}. Vůle se podlamuje, poslušnost stoupla na {cil.poslusnost}.")
                        zaznamenej(hra, f"Černý trh: sérum zlomené vůle podáno {cil.jmeno}.")
                except EOFError:
                    return
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "4":
        if hrac.gold >= 180:
            hrac.gold -= 180
            for u in getattr(hra.mafie, "uzemi", []):
                u.riziko_inkvizice = max(0, getattr(u, "riziko_inkvizice", 0) - 5)
            if hasattr(hra.mafie, "korupce"):
                hra.mafie.korupce = min(100, hra.mafie.korupce + 4)
            tisk_ok("Falešný církevní odpustek získán. Riziko inkvizice na územích kleslo, korupce stoupla.")
            zaznamenej(hra, "Černý trh: zakoupen falešný inkviziční odpustek.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "5":
        if hrac.gold >= 220:
            hrac.gold -= 220
            hrac.gold += 300
            hra.mafie.vliv_ve_meste = min(100, getattr(hra.mafie, "vliv_ve_meste", 0) + 8)
            tisk_ok("Pašerácká dohoda uzavřena! Čistý zisk +80 🪙 a vliv mafie ve městě stoupl o +8%.")
            zaznamenej(hra, "Černý trh: uzavřena lukrativní pašerácká úmluva.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "6":
        if hrac.gold >= 350:
            hrac.gold -= 350
            if hasattr(hrac, "zvys_max_temno"):
                hrac.zvys_max_temno(10)
            else:
                hrac.max_dark_energy = getattr(hrac, "max_dark_energy", 100) + 10
            hrac.dark_energy = getattr(hrac, "dark_energy", 0) + 10
            tisk_ok(f"Krvavý ametyst byl vstřebán tvou duší. Max temná energie trvale vzrostla (+10)!")
            zaznamenej(hra, "Černý trh: absorbován Krvavý ametyst (+10 max temno).")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "7":
        if hrac.gold >= 400:
            hrac.gold -= 400
            from data.jmena import vyber_nove_jmeno
            from data.charaktery import vyber_charakter
            jmeno = vyber_nove_jmeno(hra.harem.otrokyne)
            otrok = Otrokyně(
                jmeno=jmeno,
                vek=random.randint(20, 26),
                charakter=vyber_charakter(),
            )
            otrok.faze_zkazenosti = 3
            otrok.poslusnost = 55
            otrok.loajalita = 45
            otrok.touha = 70
            otrok.vlhkost = 65
            hra.harem.pridat(otrok)
            tisk_ok(f"★ Úspěšný příhoz v dražbě! Exotická otrokyně {jmeno} ({otrok.charakter}) byla doručena do tvé pevnosti.")
            zaznamenej(hra, f"Černý trh: z podsvětní dražby získána otrokyně {jmeno}.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "8":
        if hrac.gold >= 260:
            hrac.gold -= 260
            hrac.sex_energy = min(getattr(hrac, "max_sex", lambda: 100)(), getattr(hrac, "sex_energy", 0) + 15)
            for o in hra.harem.vsechny_aktivni():
                o.touha = min(100, getattr(o, "touha", 0) + 5)
            if hasattr(hra.frakce, "frakce") and "nymfomanky" in hra.frakce.frakce:
                hra.frakce.frakce["nymfomanky"].zmenit(4)
            tisk_ok("Dýmový koktejl rozproudil vášeň. +15 sexuální energie a +5 touha všem aktivním otrokyním.")
            zaznamenej(hra, "Černý trh: koupen Dýmový koktejl pro rozproudění vášní.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "9":
        if hrac.gold >= 300:
            hrac.gold -= 300
            hra.mafie.vliv_ve_meste = min(100, getattr(hra.mafie, "vliv_ve_meste", 0) + 10)
            if hasattr(hra.frakce, "frakce") and "cyberpunkaci" in hra.frakce.frakce:
                hra.frakce.frakce["cyberpunkaci"].zmenit(8)
            tisk_ok("Neonový skaner rozšířil tvůj vliv v městě. +10 vliv a reputace cyberpunkáků +8.")
            zaznamenej(hra, "Černý trh: koupen Neonový skaner.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "10":
        if hrac.gold >= 340:
            hrac.gold -= 340
            aktivni = hra.harem.vsechny_aktivni()
            if not aktivni:
                tisk_chyba("V harému nemáš žádné otrokyně.")
            else:
                vybrana = aktivni[0]
                vybrana.duvera = min(100, getattr(vybrana, "duvera", 0) + 15)
                vybrana.loajalita = min(100, getattr(vybrana, "loajalita", 0) + 10)
                vybrana.touha = min(100, getattr(vybrana, "touha", 0) + 5)
                tisk_ok(f"Věnec z šafránových květů přidal +15 důvěry, +10 loajality a +5 touhy {vybrana.jmeno}.")
                zaznamenej(hra, f"Černý trh: věnec pro {vybrana.jmeno}.")
        else:
            tisk_chyba("Nedostatek zlata.")

    elif v == "11":
        if hrac.gold >= 380:
            hrac.gold -= 380
            if hasattr(hra.mafie, "korupce"):
                hra.mafie.korupce = min(100, hra.mafie.korupce + 20)
            if hasattr(hra.frakce, "frakce") and "kult_krve" in hra.frakce.frakce:
                hra.frakce.frakce["kult_krve"].zmenit(5)
            hra.mafie.vliv_ve_meste = min(100, getattr(hra.mafie, "vliv_ve_meste", 0) + 7)
            tisk_ok("Rituál krycího plamene zvýšil korupci o +20 a vliv podsvětí o +7.")
            zaznamenej(hra, "Černý trh: rituál krycího plamene rozšířil vliv a kult krvavého měsíce.")
        else:
            tisk_chyba("Nedostatek zlata.")
    else:
        tisk_chyba("Neplatná volba.")

    try:
        input("Enter...")
    except EOFError:
        pass

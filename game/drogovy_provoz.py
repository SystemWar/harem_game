"""Abstraktní správa fikční laboratoře a pěstírny v herní ekonomice."""

from data.drogy import DROGY
from utils.vypis import clear, tisk_chyba, tisk_info, tisk_ok

KLIC_PROVOZU = "drogovy_provoz"
MAX_UROVEN = 3
NAZVY_ZARIZENI = {
    "laborator": "Drogová laboratoř",
    "pestirna": "Pěstírna konopí",
}
CENY_ZARIZENI = {
    "laborator": (500, 750, 1000),
    "pestirna": (350, 550, 750),
}
RECEPTY = {
    "modry_lotos": {"byliny": 1, "krystaly": 0},
    "serafinsky_prach": {"byliny": 1, "krystaly": 1},
    "temny_elixir": {"byliny": 2, "krystaly": 1},
    "ohnivy_prasek": {"byliny": 1, "krystaly": 1},
    "zlaty_nektar": {"byliny": 2, "krystaly": 1},
    "stinovy_extrakt": {"byliny": 1, "krystaly": 1},
    "krvava_sul": {"byliny": 2, "krystaly": 2},
    "aurora_pryskyric": {"byliny": 1, "krystaly": 1},
    "snova_mlha": {"byliny": 2, "krystaly": 1},
    "demonska_extaze": {"byliny": 2, "krystaly": 2},
    "draci_krev": {"byliny": 2, "krystaly": 2},
}
PRODEJNI_CENA = {
    id_drogy: max(10, int(info["cena"] * 0.75))
    for id_drogy, info in DROGY.items()
}
PRODEJNI_CENA["konopny_kvet"] = 18


def _provoz(hra):
    stav = getattr(hra, KLIC_PROVOZU, None)
    if not isinstance(stav, dict):
        stav = {}
        setattr(hra, KLIC_PROVOZU, stav)

    for zarizeni in NAZVY_ZARIZENI:
        try:
            uroven = int(stav.get(zarizeni, 0))
        except (TypeError, ValueError):
            uroven = 0
        stav[zarizeni] = max(0, min(MAX_UROVEN, uroven))
    sklad = stav.get("sklad")
    if not isinstance(sklad, dict):
        sklad = {}
        stav["sklad"] = sklad
    for polozka in ("byliny", "konopny_kvet", *DROGY):
        try:
            mnozstvi = int(sklad.get(polozka, 0))
        except (TypeError, ValueError):
            mnozstvi = 0
        sklad[polozka] = max(0, mnozstvi)
    for statistika in ("zisk", "vyrobeno", "sklizeno"):
        try:
            stav[statistika] = max(0, int(stav.get(statistika, 0)))
        except (TypeError, ValueError):
            stav[statistika] = 0
    return stav


def investuj_do_zarizeni(hra, zarizeni):
    """Postaví nebo vylepší zařízení; vrátí zaplacenou cenu, jinak False."""
    if zarizeni not in NAZVY_ZARIZENI:
        return False
    stav = _provoz(hra)
    uroven = stav[zarizeni]
    if uroven >= MAX_UROVEN:
        tisk_info(f"{NAZVY_ZARIZENI[zarizeni]} už má maximální úroveň.")
        return False
    cena = CENY_ZARIZENI[zarizeni][uroven]
    if hra.hrac.gold < cena:
        tisk_chyba(f"Na investici chybí {cena - hra.hrac.gold} zlata.")
        return False
    hra.hrac.gold -= cena
    stav[zarizeni] += 1
    tisk_ok(
        f"{NAZVY_ZARIZENI[zarizeni]}: úroveň {stav[zarizeni]} "
        f"(investice {cena} zlata)."
    )
    return cena


def vypestuj_konopi(hra):
    """Vymění abstraktní zásoby za herní suroviny pro obchod a laboratoř."""
    stav = _provoz(hra)
    uroven = stav["pestirna"]
    if uroven == 0:
        tisk_chyba("Nejdřív vybuduj pěstírnu konopí.")
        return False
    naklady = 6 + 2 * uroven
    if hra.pevnost.zasoby < naklady:
        tisk_chyba(f"Sklizeň vyžaduje {naklady} zásob.")
        return False
    hra.pevnost.zasoby -= naklady
    mnozstvi = 2 + uroven
    stav["sklad"]["konopny_kvet"] += mnozstvi
    stav["sklad"]["byliny"] += uroven
    stav["sklizeno"] += mnozstvi
    body = 1
    hra.vyzkum.pridej_body(body)
    tisk_ok(
        f"Sklizeň přidala {mnozstvi} konopných květů a "
        f"{uroven} balíky bylin. Výzkum +{body} bod."
    )
    return mnozstvi


def vyrob_drogu(hra, id_drogy):
    """Vyrobí jednu fikční položku za suroviny a přidá výzkumné body."""
    if id_drogy not in RECEPTY or id_drogy not in DROGY:
        tisk_chyba("Neznámý výrobek.")
        return False
    stav = _provoz(hra)
    if stav["laborator"] == 0:
        tisk_chyba("Nejdřív vybuduj drogovou laboratoř.")
        return False
    recept = RECEPTY[id_drogy]
    if stav["sklad"]["byliny"] < recept["byliny"]:
        tisk_chyba("V laboratoři chybí bylinné zásoby z pěstírny.")
        return False
    if hra.pevnost.krystaly < recept["krystaly"]:
        tisk_chyba("Pevnost nemá dostatek krystalů.")
        return False

    stav["sklad"]["byliny"] -= recept["byliny"]
    hra.pevnost.krystaly -= recept["krystaly"]
    stav["sklad"][id_drogy] += 1
    stav["vyrobeno"] += 1
    body = 1 + (1 if recept["krystaly"] > 0 else 0) + (stav["laborator"] - 1)
    hra.vyzkum.pridej_body(body)
    tisk_ok(
        f"Vyrobeno: {DROGY[id_drogy]['nazev']}. "
        f"Výzkum +{body} bodů."
    )
    return True


def prodej_zasob(hra, id_polozky, mnozstvi=1):
    """Prodá dostupné kusy za herní zlato a vrátí výnos."""
    if id_polozky not in PRODEJNI_CENA:
        tisk_chyba("Neznámá položka.")
        return False
    try:
        mnozstvi = int(mnozstvi)
    except (TypeError, ValueError):
        tisk_chyba("Zadej platný počet kusů.")
        return False
    if mnozstvi <= 0:
        tisk_chyba("Počet kusů musí být kladný.")
        return False
    stav = _provoz(hra)
    if stav["sklad"].get(id_polozky, 0) < mnozstvi:
        tisk_chyba("Ve skladu není dostatek kusů.")
        return False

    stav["sklad"][id_polozky] -= mnozstvi
    vynos = PRODEJNI_CENA[id_polozky] * mnozstvi
    hra.hrac.gold += vynos
    stav["zisk"] += vynos
    tisk_ok(f"Prodej {mnozstvi} kusů přinesl {vynos} zlata.")
    return vynos


def menu_drogoveho_provozu(hra):
    while True:
        clear()
        stav = _provoz(hra)
        print("--- Drogová laboratoř a pěstírna konopí ---")
        print(
            f"Laboratoř {stav['laborator']}/{MAX_UROVEN} | "
            f"Pěstírna {stav['pestirna']}/{MAX_UROVEN}"
        )
        print(
            f"Sklad: konopné květy {stav['sklad']['konopny_kvet']}, "
            f"bylinné zásoby {stav['sklad']['byliny']} | "
            f"výzkum {hra.vyzkum.body} bodů | tržby {stav['zisk']} zlata"
        )
        print("1) Investovat do laboratoře")
        print("2) Investovat do pěstírny")
        print("3) Provést abstraktní sklizeň")
        print("4) Vyrobit fikční výrobek")
        print("5) Prodat sklad")
        print("0) Zpět")
        try:
            volba = input("> ").strip()
        except EOFError:
            return
        if volba == "0":
            return
        if volba == "1":
            investuj_do_zarizeni(hra, "laborator")
        elif volba == "2":
            investuj_do_zarizeni(hra, "pestirna")
        elif volba == "3":
            vypestuj_konopi(hra)
        elif volba == "4":
            print("\nDostupné fikční výrobky:")
            for index, id_drogy in enumerate(DROGY, start=1):
                cena = PRODEJNI_CENA[id_drogy]
                print(f"{index}) {DROGY[id_drogy]['nazev']} — prodej {cena} zlata")
            try:
                vyber = input("Číslo výrobku (0 zpět): ").strip()
                if vyber.isdigit() and 1 <= int(vyber) <= len(DROGY):
                    id_drogy = list(DROGY)[int(vyber) - 1]
                    vyrob_drogu(hra, id_drogy)
                elif vyber != "0":
                    tisk_chyba("Neplatná volba výrobku.")
            except EOFError:
                return
        elif volba == "5":
            polozky = [
                ("konopny_kvet", "Konopný květ"),
                *((id_drogy, info["nazev"]) for id_drogy, info in DROGY.items()),
            ]
            dostupne = [
                (id_polozky, nazev)
                for id_polozky, nazev in polozky
                if stav["sklad"].get(id_polozky, 0) > 0
            ]
            if not dostupne:
                tisk_info("Sklad je prázdný.")
            else:
                print("\nZásoby k prodeji:")
                for index, (id_polozky, nazev) in enumerate(dostupne, start=1):
                    pocet = stav["sklad"][id_polozky]
                    print(
                        f"{index}) {nazev}: {pocet} ks "
                        f"({PRODEJNI_CENA[id_polozky]} zlata/ks)"
                    )
                try:
                    vyber = input("Položka (0 zpět): ").strip()
                    if vyber.isdigit() and 1 <= int(vyber) <= len(dostupne):
                        id_polozky, _ = dostupne[int(vyber) - 1]
                        pocet = input("Počet kusů: ").strip()
                        prodej_zasob(hra, id_polozky, pocet)
                    elif vyber != "0":
                        tisk_chyba("Neplatná volba položky.")
                except EOFError:
                    return
        else:
            tisk_chyba("Neplatná volba.")
        try:
            input("Enter...")
        except EOFError:
            return

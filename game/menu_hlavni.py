"""Zobrazení hlavního herního menu a zpracování jeho textových zkratek."""

import textwrap

from config import (
    RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GOLD, BOLD, NC, DIM,
)
from utils.vypis import ascii_art, banner_lokace, terminalni_obrazek, ukazatel
from game.cile_hry import prehled_cilu
from game.tituly import dalsi_titul, hodnost, zaznamenej_povyseni
from data.mesta import MESTA


POLOZKY_HLAVNIHO_MENU = (
    ("1", "👉 Interakce s otrokyněmi"),
    ("2", "💰 Nájem otrokyně"),
    ("3", "🏢 Mafie / gangy & území"),
    ("4", "📈 Vývoj postavy"),
    ("5", "🤝 Diplomacie & frakce"),
    ("6", "🔬 Výzkum dominia"),
    ("7", "🧠 Subky & domestikace"),
    ("8", "🗺️ Mapa světa & lokace"),
    ("9", "📖 Příběhová kampaň"),
    ("11", "🎯 Lov otrokyň"),
    ("12", "🛌 Odpočinek (nový den)"),
    ("13", "🛒 Obchod města"),
    ("14", "🎲 Questy & úkoly"),
    ("15", "🏛️ Dražba otrokyň"),
    ("16", "🏗️ Budovy dominia"),
    ("17", "📊 Grafy & statistiky"),
    ("18", "⚔️ Souboj & aréna"),
    ("19", "🧪 Alchymie & lektvary"),
    ("20", "📋 Rychlý přehled dne"),
    ("21", "🏛️ Nevěstinec & prodej dívek"),
    ("22", "📜 Deník úkolů"),
    ("23", "🤝 Profily, osobnost, vztahy"),
    ("24", "🛠️ Crafting & předměty"),
    ("25", "⚡ Dobít energii"),
    ("26", "💾 Uložit / načíst hru"),
    ("27", "🧭 Průvodce dominiem"),
    ("28", "💍 Manželství, žárlivost & rodina"),
    ("29", "📖 Kronika dominia"),
    ("30", "📋 Denní rozkazy harému"),
    ("31", "🎭 Veřejný výkon"),
    ("32", "📅 Kalendář a události"),
    ("33", "🏙️ Městské krize & drama"),
    ("34", "💬 Story questy harému"),
    ("35", "🏭 Specializace čtvrtí"),
    ("36", "🏴 Správa městských frakcí"),
    ("37", "🌍 Živý svět, cíle frakcí a NPC"),
    ("38", "👥 Najímání personálu a mise"),
    ("39", "🎲 Kasino — kostky, jednadvacet a sázky"),
)

ZKRATKY_HLAVNIHO_MENU = {
    "s": "26",
    "l": "26",
    "m": "26",
    "q": "26",
    "a": "auto",
    "t": "test",
    "$": "cheat",
    "&": "cheat_suroviny",
    "#": "cheat_dovednosti",
    "*": "cheat_budovy",
    ":": "cheat_loajalita",
}

MAPOVANI_CISEL_MENU = {
    str(nove_cislo): stare_cislo
    for nove_cislo, (stare_cislo, _popis) in enumerate(POLOZKY_HLAVNIHO_MENU, 1)
}

KATEGORIE_HLAVNIHO_MENU = (
    ("👑 HARÉM & VZTAHY", (1, 7, 14, 20, 22, 27, 29, 30)),
    ("🏰 PANSTVÍ & IMPÉRIUM", (2, 3, 5, 6, 12, 15, 38)),
    ("🗺️ SVĚT, FRAKCE & DOBRODRUŽSTVÍ", (8, 9, 10, 13, 21, 26, 28, 31, 32, 33, 34, 35, 36, 37)),
    ("⚙️ POSTAVA & PROVOZ", (4, 11, 16, 17, 18, 19, 23, 24, 25)),
)


def normalizuj_volbu(volba):
    """Převede nové číslování a textové zkratky na interní volby."""
    return ZKRATKY_HLAVNIHO_MENU.get(
        volba, MAPOVANI_CISEL_MENU.get(volba, volba)
    )


def vykresli_prehled_ctvrti(hra):
    """Ukáže postup objevování městských čtvrtí a místní zdroj."""
    from game.svet import AKCE_MESTSKYCH_CTVRTI, LOKACE, NOVE_MESTSKE_LOKACE

    odhalene = [
        lok_id for lok_id in NOVE_MESTSKE_LOKACE
        if lok_id in hra.svet.odhalene_lokace
    ]
    banner_lokace(
        "MĚSTSKÁ SÍŤ",
        f"{len(odhalene)}/{len(NOVE_MESTSKE_LOKACE)} čtvrtí odhaleno",
    )
    if odhalene:
        print(
            "  "
            + "  •  ".join(
                f"{LOKACE[lok_id]['ikona']} {LOKACE[lok_id]['kratky']}"
                for lok_id in odhalene
            )
        )
    else:
        print("  Zatím neznáš žádnou z propojených městských čtvrtí.")

    vychodni_lokace = MESTA["vychodni_brod"]["lokace"]
    vychodni_odhalene = sum(
        lokace in hra.svet.odhalene_lokace for lokace in vychodni_lokace
    )
    stav = getattr(hra, "zivy_svet", None)
    mesto = getattr(stav, "mesta", {}).get("vychodni_brod") if stav else None
    stav_txt = (
        f" | bezpečí {mesto.bezpeci}, prosperita {mesto.prosperita}"
        if mesto else ""
    )
    print(
        f"  🌉 {MESTA['vychodni_brod']['nazev']}: "
        f"{vychodni_odhalene}/{len(vychodni_lokace)} míst odhaleno{stav_txt}"
    )

    lok_id = hra.svet.aktualni_lokace
    zdroj = AKCE_MESTSKYCH_CTVRTI.get(lok_id, {}).get("zdroj")
    if zdroj:
        dostupny = hra.svet.lokacni_odmena_dostupna(
            lok_id, "zdroj", getattr(hra.hrac, "den", 0)
        )
        stav = "dnes dostupný" if dostupny else "dnes již sesbírán"
        print(f"  ⚗️ Místní zdroj: {zdroj['nazev']} ({stav})")
    print()


def vykresli_hlavni_menu(hra):
    ascii_art()
    terminalni_obrazek("menu")
    max_s = hra.hrac.max_sex() if hasattr(hra.hrac, "max_sex") else 100
    max_t = hra.hrac.max_temno() if hasattr(hra.hrac, "max_temno") else 100
    aktivni_harem = hra.harem.vsechny_aktivni()
    pocet_partnerek = sum(1 for o in aktivni_harem if getattr(o, "partnerka", False))
    oblibena = next((o for o in aktivni_harem if getattr(o, "oblibena", False)), None)
    oblib_txt = f" ★{oblibena.jmeno}" if oblibena else ""

    print(f"{GOLD}{BOLD}╔{'═'*76}╗{NC}")
    print(
        f"{GOLD}{BOLD}║{NC} {BOLD}Den {hra.hrac.den:>3}{NC}  "
        f"{GREEN}🪙 {hra.hrac.gold:<6}{NC}  "
        f"{YELLOW}👑 Harém {hra.harem.pocet()} (partnerek {pocet_partnerek}{oblib_txt}){NC}  "
        f"{MAGENTA}🏰 Území {len(hra.mafie.uzemi)}{NC}"
        f"{GOLD}{BOLD}{'':>2}║{NC}"
    )
    bar_s = ukazatel(hra.hrac.sex_energy, max_s, sirka=16)
    bar_t = ukazatel(
        hra.hrac.dark_energy, max_t, sirka=16,
        barva_plno=MAGENTA, barva_malo=RED,
    )
    print(
        f"{GOLD}{BOLD}║{NC} ⚡ Energie {bar_s}  🌑 Temno {bar_t}"
        f"{GOLD}{BOLD}║{NC}"
    )
    print(
        f"{GOLD}{BOLD}║{NC} {RED}☩ Inkvizice {hra.hrac.vliv_inkvizice:<3}{NC}  "
        f"{CYAN}🏰 Pevnost {hra.pevnost.uroven}{NC}  "
        f"📍 {hra.svet.aktualni_lokace} "
        f"{GOLD}{BOLD}║{NC}"
    )
    print(f"{GOLD}{BOLD}╚{'═'*76}╝{NC}")
    zaznamenej_povyseni(hra)
    titul = hodnost(hra)
    dalsi = dalsi_titul(hra)
    dan_txt = f"+{int(titul['dan'] * 100)} % daní" if titul["dan"] else "bez bonusu daní"
    if dalsi:
        print(
            f"{GOLD}👑 {titul['nazev']}{NC} ({dan_txt})  "
            f"{DIM}další: {dalsi['nazev']} — aréna {hra.pevnost.arena_rank}/{dalsi['arena']}, "
            f"pevnost {hra.pevnost.uroven}/{dalsi['pevnost']}, "
            f"reputace {hra.hrac.reputace_mesta}/{dalsi['reputace']}{NC}"
        )
    else:
        print(f"{GOLD}👑 {titul['nazev']}{NC} ({dan_txt}). Nikdo z arény se tě neodváží vyzvat.")
    print()

    cile = prehled_cilu(hra)
    print(f"{GOLD}{BOLD}╔════ 🎯 AKTIVNÍ CÍLE A DOPORUČENÝ KROK ═════════════════════════════════╗{NC}")
    if cile["aktivni"]:
        text_cilu = " • ".join(cile["aktivni"])
        for radek in textwrap.wrap(text_cilu, width=72):
            print(f"{GOLD}║{NC} {YELLOW}{radek}{NC}")
    else:
        print(f"{GOLD}║{NC} {DIM}Nemáš žádný aktivní úkol.{NC}")
    for radek in textwrap.wrap(cile["doporuceni"], width=72):
        print(f"{GOLD}║{NC} {GREEN}➜ {radek}{NC}")
    print(f"{GOLD}{BOLD}╚{'═'*76}╝{NC}")
    print()

    from game.denni_udalosti import prehled_pribehoveho_stavu
    stav_pribehu = prehled_pribehoveho_stavu(hra)
    for radek in stav_pribehu:
        print(f"{MAGENTA}🎭 {radek}{NC}")
    if stav_pribehu:
        print()

    vykresli_prehled_ctvrti(hra)

    popisy = {
        cislo: popis
        for cislo, (_stare_cislo, popis) in enumerate(POLOZKY_HLAVNIHO_MENU, 1)
    }
    popisy[25] = "💾 Uložit / načíst hru (S/L/M)"
    styl = getattr(hra.nastaveni, "styl_menu", "kategorie")
    if styl == "seznam":
        print(f"{GOLD}{BOLD}╔════ 📜 HLAVNÍ MENU — VŠECHNY VOLBY ════╗{NC}")
        for cislo, popis in popisy.items():
            print(
                f"{YELLOW}{cislo:>2}){NC} {popis}"
            )
        print(f"{GOLD}{BOLD}╚═══════════════════════════════════════╝{NC}")
    elif styl == "kompaktni":
        print(f"{CYAN}{BOLD}📜 HLAVNÍ MENU{NC}")
        volby = list(popisy.items())
        for index in range(0, len(volby), 2):
            prvni = f"{volby[index][0]:>2}) {volby[index][1]}"
            druhy = None
            if index + 1 < len(volby):
                druhy = f"{volby[index + 1][0]:>2}) {volby[index + 1][1]}"
            print(
                f"  {YELLOW}{prvni.ljust(58)}{NC} "
                f"{CYAN}{druhy or ''}{NC}"
            )
    elif styl == "sekce":
        barvy_sekci = (GOLD, MAGENTA, CYAN, YELLOW)
        for index, (nazev, cisla) in enumerate(KATEGORIE_HLAVNIHO_MENU):
            barva = barvy_sekci[index]
            print(f"\n{barva}{BOLD}── {nazev} ──{NC}")
            for cislo in cisla:
                print(f"  {YELLOW}{cislo:>2}){NC} {popisy[cislo]}")
    elif styl == "mrizka":
        kratke_podle_interniho = {
            "1": "Interakce s harémem", "2": "Nájem", "3": "Mafie a území",
            "4": "Vývoj postavy", "5": "Diplomacie", "6": "Výzkum",
            "7": "Domestikace", "8": "Mapa a lokace", "9": "Příběhová kampaň",
            "11": "Lov", "12": "Odpočinek", "13": "Obchod",
            "14": "Questy", "15": "Dražba", "16": "Budovy dominia",
            "17": "Grafy a statistiky", "18": "Souboj a aréna",
            "19": "Alchymie", "20": "Přehled dne", "21": "Nevěstinec",
            "22": "Deník úkolů", "23": "Profily a vztahy",
            "24": "Crafting", "25": "Dobít energii", "26": "Uložit / načíst",
            "27": "Průvodce", "28": "Manželství", "29": "Kronika",
            "30": "Denní rozkazy", "31": "Veřejný výkon",
            "32": "Kalendář", "33": "Městské krize",
            "34": "Story questy harému", "35": "Specializace čtvrtí",
            "36": "Správa frakcí", "37": "Živý svět a NPC",
            "38": "Najímání personálu",
            "39": "Kasino a hazard",
        }
        kratke_popisy = {
            cislo: kratke_podle_interniho.get(stare_cislo, popis)
            for cislo, (stare_cislo, popis) in enumerate(
                POLOZKY_HLAVNIHO_MENU, 1
            )
        }
        print(f"{CYAN}{BOLD}╔════ 📜 HLAVNÍ MENU — MŘÍŽKA ═══════════════════════════════════════════════╗{NC}")
        cisla = list(kratke_popisy)
        for index in range(0, len(cisla), 3):
            bunky = [
                f"{cislo:>2}) {kratke_popisy[cislo]}"
                for cislo in cisla[index:index + 3]
            ]
            bunky.extend([""] * (3 - len(bunky)))
            print(
                f"{CYAN}║{NC} "
                + f"  {CYAN}│{NC} ".join(f"{YELLOW}{bunka:<26}{NC}" for bunka in bunky)
                + f"{CYAN}║{NC}"
            )
        print(f"{CYAN}{BOLD}╚═══════════════════════════════════════════════════════════════════════════╝{NC}")
    elif styl == "jednosloupcovy":
        print(f"{CYAN}{BOLD}📜 HLAVNÍ MENU — JEDEN SLOUPEC{NC}")
        for cislo, popis in popisy.items():
            print(f"  {YELLOW}{cislo:>2}){NC} {popis}")
    else:
        sirka_okna = 47
        okna = []
        for nazev, cisla in KATEGORIE_HLAVNIHO_MENU:
            radky = [nazev]
            radky.extend(f"{cislo:>2}) {popisy[cislo]}" for cislo in cisla)
            okna.append(radky)

        for indeks in range(0, len(okna), 2):
            para = okna[indeks:indeks + 2]
            max_radku = max(len(okno) for okno in para)
            print(
                f"{GOLD}{BOLD}╔{'═' * (sirka_okna + 2)}╗   "
                f"╔{'═' * (sirka_okna + 2)}╗{NC}"
            )
            for radka in range(max_radku):
                bunky = [
                    okno[radka] if radka < len(okno) else ""
                    for okno in para
                ]
                bunky = [bunka[:sirka_okna].ljust(sirka_okna) for bunka in bunky]
                barva = f"{BOLD}{GOLD if radka == 0 else YELLOW}"
                print(
                    f"{barva}║{NC} {bunky[0]} "
                    f"{barva}║{NC}   "
                    f"{barva}║{NC} {bunky[1]} "
                    f"{barva}║{NC}"
                )
            print(
                f"{GOLD}{BOLD}╚{'═' * (sirka_okna + 2)}╝   "
                f"╚{'═' * (sirka_okna + 2)}╝{NC}"
            )
    print(f"  {GREEN}A){NC} 🤖 Bezpečný automatický tah")
    print(f"  {CYAN}Q){NC} 🏠 Hlavní menu / uložit / nahrát / nastavení")
    menu_spodek = ""
    if hra.nastaveni.vyvojarsky_rezim:
        menu_spodek += (
            f"  {MAGENTA}T){NC} 🧪 Testovací otrokyně   │   "
        )
    print(f"{menu_spodek}{RED}0) 🚪 Konec hry{NC}")
    if hra.nastaveni.vyvojarsky_rezim:
        print(f"  {GOLD}$) 💰 Cheat: +10 000 zl. a doplnění všech energií{NC}")
        print(f"  {CYAN}&) 🧪 Cheat: +1 000 od všech surovin a zásob pevnosti{NC}")
        print(f"  {MAGENTA}#) 📈 Cheat: +10 ke každé dovednosti a +10 výzkumných bodů{NC}")
        print(f"  {YELLOW}*) 🏗️ Cheat: vylepšit všechny budovy{NC}")
        print(f"  :) 💚 Cheat: loajalita, důvěra a romance všech otrokyň na maximum{NC}")
    if getattr(hra.hrac, "bonus_za_questy", 0):
        print(f"  {GREEN}✨ Quest bonus získaný celkem: {hra.hrac.bonus_za_questy} zl.{NC}")
    if getattr(hra.hrac, "bonus_za_souboje", 0):
        print(f"  {RED}⚔️ Soubojové bonusy získané celkem: {hra.hrac.bonus_za_souboje} zl.{NC}")
    print(f"  {DIM}Tvůrce: #LordRusty23{NC}")

"""Systémová menu: ukládání, načítání, nastavení a meta menu hry."""
from config import RED, GREEN, YELLOW, CYAN, WHITE
from game.save_load import uloz_hru, uloz_slot, nacti_slot, seznam_slotu
from game.settings import aplikuj_nastaveni
from utils.vypis import (
    clear, nacti_volbu, terminalni_obrazek, tisk_ok, tisk_chyba, tisk_info,
    hlavicka,
)


def _vykresli_sloty(hlavni_soubor=None):
    for slot in seznam_slotu(hlavni_soubor) if hlavni_soubor else seznam_slotu():
        if not slot["existuje"]:
            print(f"  {slot['slot']}) 🆕 {slot['nazev']} — prázdný")
            continue
        meta = slot.get("meta") or {}
        den = meta.get("den", "?")
        zlato = meta.get("zlato", "?")
        harem = meta.get("pocet_haremu", "?")
        kdy = meta.get("ulozene", "?")
        oblib = meta.get("oblibenkyně")
        oblib_txt = f" | ★ {oblib}" if oblib else ""
        print(
            f"  {slot['slot']}) 💾 {slot['nazev']} — den {den}, zlato {zlato}, "
            f"harém {harem}{oblib_txt}"
        )
        print(f"    uloženo: {kdy} (JSON)")


def menu_ulozeni(hra):
    clear()
    if getattr(hra.nastaveni, "ironman", False):
        tisk_chyba("V režimu IRONMAN nelze manuálně ukládat do libovolných slotů!")
        tisk_info("Hra se automaticky a trvale ukládá při odpočinku (nový den) nebo ukončení hry.")
        return False
    hlavicka("Uložení hry (JSON)")
    _vykresli_sloty()
    print("0) Zpět")
    try:
        volba = nacti_volbu({"0", "1", "2", "3", "4", "5"})
        if volba == "0":
            return False
        slot = int(volba)
        uspech = uloz_slot(hra, slot)
        if uspech:
            tisk_ok(f"Hra byla uložena do JSON slotu {slot}.")
        return uspech
    except ValueError:
        tisk_chyba("Zadej číslo slotu 1 až 5.")
        return False
    except EOFError:
        return False


def menu_nacteni():
    clear()
    hlavicka("Načtení hry (JSON)")
    _vykresli_sloty()
    print("0) Zpět")
    try:
        volba = nacti_volbu({"0", "1", "2", "3", "4", "5"})
        if volba == "0":
            return None
        slot = int(volba)
        hra = nacti_slot(slot)
        if hra:
            tisk_ok(f"Načten JSON slot {slot}.")
        return hra
    except ValueError:
        tisk_chyba("Zadej číslo slotu 1 až 5.")
        return None
    except EOFError:
        return None


def menu_nastaveni(hra):
    from config import THEMES, apply_theme
    from game.settings import STYLY_MENU, STYLY_MENU_POPISY
    while True:
        clear()
        nastaveni = hra.nastaveni
        terminalni_obrazek("nastaveni")
        hlavicka("Nastavení hry")
        print("Vzhled se mění okamžitě; herní nastavení se ukládají do save.")
        print(f"1) Barvy terminálu: {'zapnuté' if nastaveni.barvy else 'vypnuté'}")
        print(f"2) Obtížnost: {nastaveni.obtiznost_text}")
        print(f"3) Skin / barevné schéma: {getattr(nastaveni, 'tema_text', 'Temné dominium')}")
        print(f"4) Ironman: {'ANO' if getattr(nastaveni, 'ironman', False) else 'ne'}")
        print(f"5) AI dialogy: {'zapnuté (Ollama/API)' if getattr(nastaveni, 'ai_dialogy', False) else 'vypnuté'}")
        print(
            f"6) Vývojářský režim (cheaty a testy): "
            f"{'zapnutý' if nastaveni.vyvojarsky_rezim else 'vypnutý'}"
        )
        print(f"7) Styl hlavního menu: {nastaveni.styl_menu_text}")
        print("8) Náhled aktivního skinu a rozložení")
        print(f"9) Výzdoba města: {getattr(nastaveni, 'dekorace_mesta_text', 'Křivolaké tržiště')}")
        print("10) Obnovit výchozí vzhled")
        print("11) Nápověda k nastavení")
        print("0) Zpět")
        try:
            volba = input("> ").strip().lower()
        except EOFError:
            return
        if volba == "0":
            return
        if volba == "1":
            nastaveni.barvy = not nastaveni.barvy
            aplikuj_nastaveni(nastaveni)
            tisk_ok("Nastavení barev změněno.")
            input("Enter...")
        elif volba == "2":
            print("\n1) Lehká  2) Normální  3) Těžká")
            vyber = input("> ").strip()
            mapa = {"1": "lehka", "2": "normalni", "3": "tezka"}
            if vyber in mapa:
                nastaveni.obtiznost = mapa[vyber]
                aplikuj_nastaveni(nastaveni)
                tisk_ok(f"Obtížnost nastavena na {nastaveni.obtiznost_text}.")
            else:
                tisk_chyba("Neplatná obtížnost.")
            input("Enter...")
        elif volba == "3":
            print("\n--- Barevná témata ---\n")
            seznam = list(THEMES.items())
            for i, (tid, info) in enumerate(seznam, 1):
                aktivni = " ← aktivní" if tid == getattr(nastaveni, "tema", "") else ""
                vzorek = ""
                if nastaveni.barvy:
                    vzorek = "".join(
                        f"{info['barvy'][barva]}██"
                        for barva in ("RED", "GREEN", "BLUE", "MAGENTA", "GOLD")
                    ) + "\033[0m "
                print(f"{i}) {vzorek}{info['nazev']}{aktivni}")
                print(f"   {info['popis']}")
            print("0) Zpět")
            vyber = input("> ").strip()
            if vyber == "0":
                continue
            try:
                idx = int(vyber) - 1
                if 0 <= idx < len(seznam):
                    tid = seznam[idx][0]
                    nastaveni.tema = tid
                    nastaveni.barvy = True
                    aplikuj_nastaveni(nastaveni)
                    nazev = apply_theme(tid)
                    tisk_ok(f"Téma nastaveno: {nazev}")
                    terminalni_obrazek("menu")
                else:
                    tisk_chyba("Špatná volba.")
            except ValueError:
                tisk_chyba("Zadej číslo.")
            input("Enter...")
        elif volba == "4":
            nastaveni.ironman = not getattr(nastaveni, "ironman", False)
            tisk_ok("Ironman " + ("zapnut" if nastaveni.ironman else "vypnut") + ".")
            input("Enter...")
        elif volba == "5":
            nastaveni.ai_dialogy = not getattr(nastaveni, "ai_dialogy", False)
            if nastaveni.ai_dialogy:
                tisk_ok("AI dialogy zapnuty. Ollama :11434 nebo AI_API_KEY.")
            else:
                tisk_ok("AI dialogy vypnuty.")
            input("Enter...")
        elif volba == "6":
            nastaveni.vyvojarsky_rezim = not nastaveni.vyvojarsky_rezim
            stav = "zapnut" if nastaveni.vyvojarsky_rezim else "vypnut"
            tisk_info(
                f"Vývojářský režim {stav}. "
                "Změna se uloží spolu s uloženou hrou."
            )
            input("Enter...")
        elif volba == "7":
            print("\n--- Styl hlavního menu ---\n")
            for index, styl in enumerate(STYLY_MENU, 1):
                aktivni = " ← aktivní" if styl == nastaveni.styl_menu else ""
                print(f"{index}) {STYLY_MENU_POPISY[styl]}{aktivni}")
            print("0) Zpět")
            vyber = input("> ").strip()
            if vyber == "0":
                continue
            try:
                index = int(vyber) - 1
                if 0 <= index < len(STYLY_MENU):
                    nastaveni.styl_menu = STYLY_MENU[index]
                    tisk_ok(f"Styl menu změněn: {nastaveni.styl_menu_text}.")
                else:
                    tisk_chyba("Špatná volba.")
            except ValueError:
                tisk_chyba("Zadej číslo.")
            input("Enter...")
        elif volba == "8":
            print("\n--- Náhled aktivního vzhledu ---")
            print(
                f"Skin: {nastaveni.tema_text} | "
                f"barvy terminálu: {'zapnuté' if nastaveni.barvy else 'vypnuté'}"
            )
            print(f"Rozložení: {nastaveni.styl_menu_text}")
            print("Ukázka barev: ", end="")
            if nastaveni.barvy:
                print("".join(
                    f"{THEMES[nastaveni.tema]['barvy'][barva]}██"
                    for barva in ("RED", "GREEN", "BLUE", "MAGENTA", "GOLD")
                ) + "\033[0m")
            else:
                print("barvy jsou vypnuté")
            print("\nDostupné skiny:")
            for info in THEMES.values():
                print(f"  • {info['nazev']}: {info['popis']}")
            print("\nDostupné rozložení:")
            for styl in STYLY_MENU:
                print(f"  • {STYLY_MENU_POPISY[styl]}")
            input("Enter...")
        elif volba == "9":
            from game.settings import MESTSKA_DEKORACE
            print("\n--- Výzdoba města ---\n")
            seznam = list(MESTSKA_DEKORACE.items())
            for i, (kluc, info) in enumerate(seznam, 1):
                aktivni = " ← aktivní" if kluc == getattr(nastaveni, "dekorace_mesta", "trh") else ""
                print(f"{i}) {info['nazev']}{aktivni}")
                print(f"   {info['popis']}")
            print("0) Zpět")
            vyber = input("> ").strip()
            if vyber == "0":
                continue
            try:
                idx = int(vyber) - 1
                if 0 <= idx < len(seznam):
                    kluc = seznam[idx][0]
                    nastaveni.dekorace_mesta = kluc
                    tisk_ok(f"Výzdoba města nastavena na: {MESTSKA_DEKORACE[kluc]['nazev']}")
                else:
                    tisk_chyba("Špatná volba.")
            except ValueError:
                tisk_chyba("Zadej číslo.")
            input("Enter...")
        elif volba == "10":
            from game.settings import (
                VYCHOZI_DEKORACE_MESTA,
                VYCHOZI_STYL_MENU,
                VYCHOZI_TEMA,
            )
            nastaveni.tema = VYCHOZI_TEMA
            nastaveni.styl_menu = VYCHOZI_STYL_MENU
            nastaveni.dekorace_mesta = VYCHOZI_DEKORACE_MESTA
            nastaveni.barvy = True
            aplikuj_nastaveni(nastaveni)
            tisk_ok("Výchozí vzhled hry byl obnoven.")
            input("Enter...")
        elif volba == "11":
            print(
                "\nSkin mění barvy terminálu; při vypnutých barvách zůstane "
                "aktivní a projeví se po jejich zapnutí."
            )
            print(
                "Styl menu mění pouze zobrazení možností. Obtížnost ovlivňuje "
                "hru, Ironman omezuje obnovu a AI dialogy vyžadují externí "
                "službu, pokud jsou povolené."
            )
            print(
                "V hlavním menu otevře Q nabídku hlavního menu, uložení, "
                "načtení a nastavení. Změny vzhledu lze "
                "kdykoli vrátit výchozím nastavením."
            )
            input("Enter...")
        else:
            tisk_chyba("Neplatná volba.")
            input("Enter...")


def menu_meta_hlavni(hra):
    while True:
        clear()
        terminalni_obrazek("nastaveni")
        hlavicka("Hlavní menu")
        print(f"{GREEN}1) 💾 Uložit hru")
        print(f"{CYAN}2) 📂 Načíst hru")
        print(f"{WHITE}3) ⚙️ Nastavení hry")
        print(f"{YELLOW}4) 🏠 Zpět do hry")
        print(f"{RED}0) 🚪 Ukončit hru (s uložením)")
        try:
            volba = input("> ").strip().lower()
        except EOFError:
            uloz_hru(hra)
            return "quit"
        if volba in ("1", "s"):
            menu_ulozeni(hra)
            input("Enter...")
        elif volba in ("2", "l"):
            nova = menu_nacteni()
            if nova:
                tisk_ok("Hra načtena.")
                input("Enter...")
                return nova
            input("Enter...")
        elif volba == "3":
            menu_nastaveni(hra)
        elif volba in ("4", ""):
            return None
        elif volba in ("0", "q"):
            uloz_hru(hra)
            print("Hra uložena. Konec hry.")
            return "quit"
        else:
            tisk_chyba("Neplatná volba.")
            input("Enter...")

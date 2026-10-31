#!/usr/bin/env python3
# main.py
import random
from dataclasses import dataclass
from config import RED, GREEN, YELLOW, MAGENTA, CYAN, GOLD, BOLD, WHITE, NC, DIM
from game.save_load import (
    Hra, uloz_hru, uloz_slot, nacti_slot, seznam_slotu,
)
from game.trailer import prehraj_trailer, menu_trailer
from game.interakce import zobraz_interakce, zobraz_hromadne_interakce
from game.ekonomika import najem_otrokyně
from game.mafie import spravovat_mafii
from game.vyvoj import zobraz_vyvoj
from game.diplomacie import Diplomacie
from game.vyzkum import VyzkumSystem
from game.subky_domestikace import SubkyDomestikace
from game.lov import lov_otrokyn
from game.odpocinek import odpocinek
from game.energie import zobraz_menu as menu_energie
from game.obchod import obchod
from game.drazba import drazba_otrokyn
from game.budovy import spravovat_budovy
from game.denni_udalosti import spust_denni_udalost
from game.udalosti import spust_nahodnou_udalost
from game.statistiky import zobraz_statistiky
from game.souboje import Souboj
from game.crafting import CraftingSystem
from game.harem_interakce import menu_haremu
from game.settings import NastaveniHry, aplikuj_nastaveni
from game.automaticky_tah import obsluz_automaticky_tah
from game.manzelstvi import menu_manzelstvi
from game.menu_extra import obsluz_extra_volbu
from game.menu_hlavni import (
    MAPOVANI_CISEL_MENU, ZKRATKY_HLAVNIHO_MENU,
    normalizuj_volbu, vykresli_hlavni_menu,
)
from game.nevestinec import menu_nevestinec
from game.menu_system import (
    menu_ulozeni, menu_nacteni, menu_nastaveni, menu_meta_hlavni,
)
from utils.vypis import (
    clear, nacti_volbu, terminalni_obrazek, tisk_ok, tisk_chyba, tisk_info,
    ukazatel, hlavicka,
)
from utils.diagnostika import configure_logging
from data.jmena import vyber_nove_jmeno
from data.charaktery import nazev_charakteru, vyber_charakter
from data.degradace import nazev_faze
from models.otrokyne import Otrokyně

import logging

# Current active game (used for crash-save)
_CURRENT_GAME = None


@dataclass
class HlavniMenuRuntime:
    diplo: Diplomacie
    vyzkum: VyzkumSystem
    subky: SubkyDomestikace
    souboj: Souboj
    crafting: CraftingSystem


def _pockej_na_enter():
    try:
        input("Enter...")
    except EOFError:
        pass


def _obnov_hru_runtime(hra: Hra):
    global _CURRENT_GAME
    _CURRENT_GAME = hra
    return HlavniMenuRuntime(
        diplo=Diplomacie(hra.frakce),
        vyzkum=hra.vyzkum,
        subky=SubkyDomestikace(),
        souboj=Souboj(hra.hrac, hra.mafie, hra),
        crafting=CraftingSystem(),
    )


def _bezpecne_volba(nazev, akce, *args, **kwargs):
    try:
        return akce(*args, **kwargs)
    except Exception as exc:
        logging.exception("Akce hlavního menu selhala: %s", nazev)
        tisk_chyba(f"{nazev} selhalo: {exc}")
        _pockej_na_enter()
        return None


def _obsluz_volbu_hlavniho_menu(
    hra: Hra, volba: str, runtime: HlavniMenuRuntime
):

    if volba in (
        "test", "cheat", "cheat_suroviny", "cheat_dovednosti",
        "cheat_budovy", "cheat_loajalita",
    ) and not hra.nastaveni.vyvojarsky_rezim:
        tisk_chyba(
            "Vývojářské volby jsou vypnuté. Zapni Vývojářský režim v nastavení hry."
        )
        _pockej_na_enter()
        return hra, runtime, False

    if volba == "auto":
        obsluz_automaticky_tah(hra)
        _pockej_na_enter()
    elif volba == "cheat":
        hra.hrac.gold += 10_000
        hra.hrac.dopln_energie_naplno()
        tisk_ok(
            f"Cheat aktivován: +10 000 zl. | energie doplněna "
            f"(⚡ {hra.hrac.sex_energy}/{hra.hrac.max_sex()}, "
            f"🌑 {hra.hrac.dark_energy}/{hra.hrac.max_temno()})."
        )
        _pockej_na_enter()
    elif volba == "cheat_suroviny":
        from game.alchymie import SUROVINY

        for surovina_id in SUROVINY:
            hra.alchymie.pridat_surovinu(surovina_id, 1_000)
        for atribut in ("zasoby", "drevo", "kamen", "zelezo", "krystaly"):
            setattr(hra.pevnost, atribut, getattr(hra.pevnost, atribut) + 1_000)
        tisk_ok(
            f"Cheat aktivován: +1 000 ks všech {len(SUROVINY)} "
            "alchymistických surovin a zásob pevnosti."
        )
        _pockej_na_enter()
    elif volba == "cheat_dovednosti":
        for dovednost in hra.hrac.skilly:
            hra.hrac.skilly[dovednost] += 100
        hra.hrac.skill_body += 100
        hra.vyzkum.pridej_body(100)
        for frakce in hra.frakce.frakce.values():
            frakce.reputace = 100
        tisk_ok(
            f"Cheat aktivován: +100 ke každé dovednosti "
            f"({len(hra.hrac.skilly)} dovedností), bojové zdatnosti, "
            "+100 výzkumných bodů a reputace 100% u všech frakcí."
        )
        _pockej_na_enter()
    elif volba == "cheat_budovy":
        from models.fortress import PEVNOSTNI_BUDOVY

        for budova_id in PEVNOSTNI_BUDOVY:
            hra.pevnost.budovy[budova_id] = (
                hra.pevnost.budovy.get(budova_id, 0) + 1
            )
        hra.pevnost.uroven += 1
        tisk_ok(
            f"Cheat aktivován: všechny {len(PEVNOSTNI_BUDOVY)} budovy "
            f"i hlavní citadela byly vylepšeny o 1 úroveň."
        )
        _pockej_na_enter()
    elif volba == "cheat_loajalita":
        for otrok in hra.harem.otrokyne:
            otrok.zvysit_stat("loajalita", 100)
            otrok.zvysit_stat("duvera", 100)
            otrok.romance_body = 100
        tisk_ok(
            f"Cheat aktivován: loajalita, důvěra a body romance všech "
            f"{len(hra.harem.otrokyne)} otrokyň nastaveny na maximum."
        )
        _pockej_na_enter()
    elif volba == "1":
        aktivni = hra.harem.vsechny_aktivni()
        if aktivni:
            hlavicka("👑 HARÉM — Výběr otrokyně")
            for i, o in enumerate(aktivni, 1):
                faze_nazev = nazev_faze(getattr(o, "faze_zkazenosti", 0))
                char_nazev = nazev_charakteru(getattr(o, "charakter", "subka"))
                hvezda = f"{GOLD}★ {NC}" if getattr(o, "oblibena", False) else "  "
                manzel = f" {MAGENTA}💍{NC}" if getattr(o, "je_manzelkou", False) else ""
                partner = f" {RED}♥{NC}" if getattr(o, "partnerka", False) else ""
                loj_bar = ukazatel(o.loajalita, 100, sirka=12)
                print(f"  {BOLD}{CYAN}{i}){NC} {hvezda}{BOLD}{o.jmeno}{NC}{manzel}{partner}")
                print(f"      {DIM}{char_nazev} • {faze_nazev} • věk {o.vek}{NC}")
                print(f"      Loajalita: {loj_bar}  {DIM}Osud: {o.popis_osudu()}{NC}")
                print()
            print(f"  {GOLD}@){NC} Vybrat všechny aktivní otrokyně")
            print(f"  {RED}0){NC} Zpět")
            try:
                volba_otrokyn = input(f"\n{BOLD}>{NC} ").strip()
                if volba_otrokyn == "@":
                    zobraz_hromadne_interakce(aktivni, hra.hrac)
                    return hra, runtime, False
                if volba_otrokyn == "0":
                    return hra, runtime, False
                idx = int(volba_otrokyn) - 1
                if 0 <= idx < len(aktivni):
                    zobraz_interakce(aktivni[idx], hra.hrac, nastaveni=hra.nastaveni)
                else:
                    tisk_chyba("Špatná volba.")
            except ValueError:
                tisk_chyba("Zadej číslo.")
            _pockej_na_enter()
        else:
            tisk_chyba("Nemáš žádné otrokyně.")
            _pockej_na_enter()
    elif volba == "2":
        aktivni = hra.harem.vsechny_aktivni()
        if aktivni:
            volne = [
                o for o in aktivni
                if not o.na_najmu
                and not o.je_manzelkou
                and not o.partnerka
                and not o.v_nevestinci
            ]
            if volne:
                print("\nVyber otrokyni k pronájmu:")
                for i, o in enumerate(volne, 1):
                    print(f"{i}) {o.jmeno}")
                try:
                    idx = int(input("> ")) - 1
                    if 0 <= idx < len(volne):
                        najem_otrokyně(hra.hrac, volne[idx], hra.nastaveni.obtiznost)
                    else:
                        tisk_chyba("Špatná volba.")
                except ValueError:
                    tisk_chyba("Zadej číslo.")
            else:
                tisk_chyba("Všechny otrokyně jsou na najmu.")
            _pockej_na_enter()
        else:
            tisk_chyba("Nemáš otrokyně.")
            _pockej_na_enter()
    elif volba == "3":
        _bezpecne_volba("Mafie", spravovat_mafii, hra)
    elif volba == "4":
        zobraz_vyvoj(hra.hrac)
    elif volba == "5":
        _bezpecne_volba("Diplomacie", runtime.diplo.menu, hra)
    elif volba == "6":
        _bezpecne_volba("Výzkum", runtime.vyzkum.menu, hra)
    elif volba == "7":
        aktivni = hra.harem.vsechny_aktivni()
        if aktivni:
            runtime.subky.menu(hra, aktivni)
        else:
            tisk_chyba("Nemáš otrokyně pro domestikaci.")
            _pockej_na_enter()
    elif volba == "8":
        hra.svet.menu(hra)
    elif volba == "9":
        hra.kampan.menu(hra)
    elif volba == "test":
        jmeno = vyber_nove_jmeno(hra.harem.otrokyne)
        otrok = Otrokyně(jmeno=jmeno, charakter=vyber_charakter())
        hra.harem.pridat(otrok)
        tisk_ok(f"Přidána testovací otrokyně: {jmeno}")
        _pockej_na_enter()
    elif volba == "11":
        otrok = lov_otrokyn(hra)
        if otrok:
            hra.harem.pridat(otrok)
        _pockej_na_enter()
    elif volba == "12":
        odpocinek(hra)
        _bezpecne_volba("Událost dne", spust_denni_udalost, hra)
        _bezpecne_volba("Náhodná událost", spust_nahodnou_udalost, hra)
        from game.save_load import uloz_autosave
        _bezpecne_volba("Autosave události", uloz_autosave, hra)
    elif volba == "13":
        obchod(hra)
    elif volba == "14":
        _bezpecne_volba("Questy", hra.questy.menu, hra)
    elif volba == "15":
        drazba_otrokyn(hra.hrac, hra.harem)
        _pockej_na_enter()
    elif volba == "16":
        spravovat_budovy(hra)
    elif volba == "17":
        zobraz_statistiky(hra)
        _pockej_na_enter()
    elif volba == "18":
        runtime.souboj.menu()
    elif volba == "19":
        hra.alchymie.zobraz_menu(hra.hrac, hra.harem)
    elif volba == "21":
        _bezpecne_volba("Nevěstinec", menu_nevestinec, hra)
    elif volba == "22":
        from game.denik_ukolu import zobraz_denik_ukolu
        zobraz_denik_ukolu(hra)
        _pockej_na_enter()
    elif volba == "27":
        from game.pruvodce import zobraz_pruvodce
        zobraz_pruvodce(hra)
        _pockej_na_enter()
    elif volba == "23":
        menu_haremu(hra)
    elif volba == "24":
        runtime.crafting.menu(hra)
    elif volba == "25":
        menu_energie(hra)
    elif volba == "28":
        menu_manzelstvi(hra)
    elif volba == "40":
        from game.drogovy_provoz import menu_drogoveho_provozu
        menu_drogoveho_provozu(hra)
    elif volba in ("29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39"):
        obsluz_extra_volbu(volba, hra)
    elif volba == "26":
        vysledek = menu_meta_hlavni(hra)
        if vysledek == "quit":
            return hra, runtime, True
        if vysledek is not None:
            hra = vysledek
            runtime = _obnov_hru_runtime(hra)
    elif volba == "0":
        uloz_hru(hra)
        print("Hra uložena. Konec hry.")
        return hra, runtime, True
    elif volba == "20":
        clear()
        print(f"{GOLD}--- Rychlý přehled dne {hra.hrac.den} ---{NC}\n")
        max_s = hra.hrac.max_sex() if hasattr(hra.hrac, "max_sex") else 100
        max_t = hra.hrac.max_temno() if hasattr(hra.hrac, "max_temno") else 100
        print(
            f"HP {hra.hrac.hp}/{hra.hrac.max_hp} | "
            f"Energie {hra.hrac.sex_energy}/{max_s} | "
            f"Temno {hra.hrac.dark_energy}/{max_t}"
        )
        print(
            f"Místo: {hra.svet.aktualni_lokace} | "
            f"Kampaň: {hra.kampan.kapitola + 1 if hra.kampan.aktualni() else 'hotová'}"
        )
        najmy = [
            f"{o.jmeno} ({o.najem_zbyva_dni} dní)"
            for o in hra.harem.vsechny_aktivni() if o.na_najmu
        ]
        if najmy:
            print("Na najmu: " + ", ".join(najmy))
        oblib = next((o for o in hra.harem.vsechny_aktivni() if getattr(o, "oblibena", False)), None)
        if oblib:
            print(f"★ Oblíbenkyně: {oblib.jmeno}")
        _pockej_na_enter()
    else:
        tisk_chyba("Neplatná volba.")
        _pockej_na_enter()

    return hra, runtime, False


def hlavni_menu(hra: Hra):
    runtime = _obnov_hru_runtime(hra)
    platne_volby = (
        set(MAPOVANI_CISEL_MENU)
        | set(ZKRATKY_HLAVNIHO_MENU)
        | {"0", "auto", "test", "cheat", "cheat_suroviny", "cheat_dovednosti",
           "cheat_budovy", "cheat_loajalita"}
    )
    while True:
        clear()
        vykresli_hlavni_menu(hra)
        try:
            volba = nacti_volbu(platne_volby)
        except EOFError:
            uloz_hru(hra)
            return

        try:
            hra, runtime, skoncit = _obsluz_volbu_hlavniho_menu(
                hra, normalizuj_volbu(volba), runtime
            )
        except EOFError:
            uloz_hru(hra)
            return
        except Exception:
            logging.exception("Obsluha volby hlavního menu selhala: %s", volba)
            tisk_chyba(
                "Tato akce selhala. Hra pokračuje; podrobnosti jsou v harem_debug.log."
            )
            _pockej_na_enter()
            continue
        if skoncit:
            return


def nova_hra(nastaveni=None):
    """Vytvoří novou hru s výchozím nastavením a dvěma dospělými otrokyněmi."""
    hra = Hra()
    if nastaveni is not None:
        hra.nastaveni = aplikuj_nastaveni(NastaveniHry.from_dict(nastaveni.to_dict()))
    for _ in range(2):
        jmeno = vyber_nove_jmeno(hra.harem.otrokyne)
        otrok = Otrokyně(
            jmeno, vek=random.randint(18, 28), charakter=vyber_charakter()
        )
        hra.harem.pridat(otrok)
    global _CURRENT_GAME
    _CURRENT_GAME = hra
    return hra


def start():
    global _CURRENT_GAME
    configure_logging()
    while True:
        clear()
        print(f"{GOLD}{BOLD}👑 HAREM DARK{NC}")
        print(f"{DIM}Dark Expansion{NC}\n")
        print(f"{GREEN}1) Nová hra")
        print(f"{CYAN}2) Načíst hru")
        print(f"{WHITE}3) Nastavení")
        print(f"{MAGENTA}4) 🎬 Trailer")
        print(f"{RED}0) Konec")
        try:
            volba = nacti_volbu({"0", "1", "2", "3", "4"})
        except EOFError:
            return
        if volba == "1":
            try:
                prehraj_trailer(rychle=True, interaktivni=True)
            except Exception as exc:
                logging.exception("Přehrání traileru selhalo.")
                tisk_chyba(f"Trailer se nepodařilo přehrát: {exc}. Hra bude pokračovat.")
            hra = nova_hra()
            _CURRENT_GAME = hra
            hlavni_menu(hra)
        elif volba == "2":
            hra = menu_nacteni()
            if hra:
                _CURRENT_GAME = hra
                hlavni_menu(hra)
        elif volba == "3":
            h = Hra()
            menu_nastaveni(h)
        elif volba == "4":
            menu_trailer()
        elif volba == "0":
            return


if __name__ == "__main__":
    try:
        start()
    except Exception as e:
        logpath = configure_logging()
        logging.exception("Nezachycená chyba hlavní herní smyčky.")
        try:
            if _CURRENT_GAME and not getattr(_CURRENT_GAME.nastaveni, "ironman", False):
                uloz_hru(_CURRENT_GAME)
                print(f"Nečekaný pád: pokus o uložení dokončen. Log: {logpath}")
        except Exception:
            logging.exception("Automatické uložení po pádu selhalo.")
        print(f"Nečekaná chyba: {e}. Trace uložen do {logpath}.")
        raise

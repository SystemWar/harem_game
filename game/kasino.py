"""Městské kasino, kostky a jednadvacet."""

import random

from models.kasino import KasinoSystem
from utils.vypis import tisk_chyba, tisk_info, tisk_ok, vytiskni_volbu

CENA_OTEVRENI = 300
MIN_SAZKA = 10
MAX_UROVEN = 5


def menu_kasina(hra):
    kasino = hra.kasino
    while True:
        print("\n=== KASINO U ČERVENÉ ČTVRTI ===")
        print(f"Místo: Červená čtvrť | Pokladna hráče: {hra.hrac.gold} zl.")
        if kasino.otevreno:
            print(
                f"Úroveň {kasino.uroven}/{MAX_UROVEN} | "
                f"limit sázky {kasino.limit_sazky} zl. | "
                f"denní příjem {kasino.uroven * 10} zl."
            )
            print(
                f"Výhry {kasino.vyhry} | prohry {kasino.prohry} | "
                f"remízy {kasino.remizy} | čistý výsledek {kasino.cisty_zisk:+} zl."
            )
            vytiskni_volbu("1", "Hrát kostky — tipni si, zda součet bude pod/nad 7")
            vytiskni_volbu("2", "Hrát jednadvacet — přibliž se k 21 bez přetažení")
            if kasino.uroven < MAX_UROVEN:
                cena = _cena_vylepseni(kasino.uroven)
                vytiskni_volbu(
                    "3",
                    f"Vylepšit kasino na úroveň {kasino.uroven + 1} ({cena} zl.)",
                )
        else:
            vytiskni_volbu("1", f"Otevřít kasino ({CENA_OTEVRENI} zl.)")
        vytiskni_volbu("4", "Historie posledních her")
        vytiskni_volbu("0", "Zpět")
        try:
            volba = input("> ").strip()
        except EOFError:
            return
        if volba == "0":
            return
        if not kasino.otevreno and volba == "1":
            otevri_kasino(hra)
        elif kasino.otevreno and volba in ("1", "2"):
            sazka = _nacti_sazku(hra)
            if sazka is None:
                continue
            if volba == "1":
                tip = _nacti_tip_kostek()
                if tip:
                    hraj_kostky(hra, sazka, tip)
            else:
                hraj_jednadvacet(hra, sazka)
        elif kasino.otevreno and volba == "3" and kasino.uroven < MAX_UROVEN:
            vylepsi_kasino(hra)
        elif volba == "4":
            zobraz_historii(kasino)
        else:
            tisk_chyba("Tato volba teď není dostupná.")


def otevri_kasino(hra):
    kasino = hra.kasino
    if kasino.otevreno:
        return False
    if hra.hrac.gold < CENA_OTEVRENI:
        tisk_chyba(f"Otevření kasina stojí {CENA_OTEVRENI} zlata.")
        return False
    hra.hrac.gold -= CENA_OTEVRENI
    kasino.otevreno = True
    kasino.uroven = 1
    tisk_ok(
        "Kasino U Červené čtvrti je otevřeno. "
        "První stůl má limit sázky 100 zl."
    )
    return True


def vylepsi_kasino(hra):
    kasino = hra.kasino
    if not kasino.otevreno or kasino.uroven >= MAX_UROVEN:
        tisk_chyba("Kasino nelze dále vylepšit.")
        return False
    cena = _cena_vylepseni(kasino.uroven)
    if hra.hrac.gold < cena:
        tisk_chyba(f"Vylepšení stojí {cena} zlata.")
        return False
    hra.hrac.gold -= cena
    kasino.uroven += 1
    tisk_ok(
        f"Kasino vylepšeno na úroveň {kasino.uroven}; "
        f"limit sázek je nyní {kasino.limit_sazky} zl. "
        f"a denní příjem {kasino.uroven * 10} zl."
    )
    return True


def hraj_kostky(hra, sazka, tip):
    if not _over_sazku(hra, sazka):
        return False
    if tip not in ("pod", "nad"):
        tisk_chyba("Tip musí být „pod“ nebo „nad“.")
        return False
    if not _odeber_sazku(hra, sazka):
        return False
    prvni, druha = random.randint(1, 6), random.randint(1, 6)
    soucet = prvni + druha
    if soucet == 7:
        hra.hrac.gold += sazka
        hra.kasino.remizy += 1
        _zaznam_hry(hra, "Kostky", sazka, 0, "Remíza", f"Padlo {soucet}.")
        tisk_info(f"Kostky: {prvni} + {druha} = {soucet}. Vrací se sázka.")
    else:
        vyhra = (soucet < 7 and tip == "pod") or (soucet > 7 and tip == "nad")
        _vyhodnot_sazku(
            hra, "Kostky", sazka, vyhra,
            f"Padlo {prvni} + {druha} = {soucet}; tipoval jsi {tip} 7.",
        )
    return True


def hraj_jednadvacet(hra, sazka):
    if not _over_sazku(hra, sazka):
        return False
    if not _odeber_sazku(hra, sazka):
        return False
    hrac_karty = [_tahni_kartu(), _tahni_kartu()]
    dealer_karty = [_tahni_kartu(), _tahni_kartu()]
    print(
        f"\nTvoje karty: {_popis_karet(hrac_karty)} "
        f"(součet {_hodnota_ruky(hrac_karty)})."
    )
    print(f"Karta krupiéra: {dealer_karty[0]}.")

    while _hodnota_ruky(hrac_karty) < 21:
        vytiskni_volbu("1", "Vzít kartu")
        vytiskni_volbu("2", "Zůstat")
        try:
            volba = input("> ").strip()
        except EOFError:
            volba = "2"
        if volba == "2":
            break
        if volba != "1":
            tisk_chyba("Zvol 1 nebo 2.")
            continue
        hrac_karty.append(_tahni_kartu())
        print(
            f"Tvoje karty: {_popis_karet(hrac_karty)} "
            f"(součet {_hodnota_ruky(hrac_karty)})."
        )

    while _hodnota_ruky(dealer_karty) < 17:
        dealer_karty.append(_tahni_kartu())
    hodnota_hrace = _hodnota_ruky(hrac_karty)
    hodnota_dealera = _hodnota_ruky(dealer_karty)
    print(
        f"Krupiér: {_popis_karet(dealer_karty)} "
        f"(součet {hodnota_dealera})."
    )
    prirozeny_blackjack = len(hrac_karty) == 2 and hodnota_hrace == 21
    blackjack_dealera = len(dealer_karty) == 2 and hodnota_dealera == 21
    if prirozeny_blackjack and blackjack_dealera:
        hra.hrac.gold += sazka
        hra.kasino.remizy += 1
        _zaznam_hry(
            hra, "Jednadvacet", sazka, 0, "Remíza",
            "Oba mají přirozený blackjack.",
        )
        tisk_info("Oba mají přirozený blackjack. Sázka se vrací.")
    elif prirozeny_blackjack:
        cista_vyhra = sazka * 3 // 2
        hra.hrac.gold += sazka + cista_vyhra
        kasino = hra.kasino
        kasino.vyhry += 1
        kasino.cisty_zisk += cista_vyhra
        _zaznam_hry(
            hra, "Jednadvacet", sazka, cista_vyhra,
            "Přirozený blackjack", f"21 proti {hodnota_dealera}.",
        )
        tisk_ok(f"Přirozený blackjack! Čistá výhra +{cista_vyhra} zl.")
    elif hodnota_hrace > 21:
        _vyhodnot_sazku(hra, "Jednadvacet", sazka, False, "Přetáhl jsi 21.")
    elif blackjack_dealera or hodnota_dealera > hodnota_hrace:
        _vyhodnot_sazku(
            hra, "Jednadvacet", sazka, False,
            f"Ty {hodnota_hrace}, krupiér {hodnota_dealera}.",
        )
    elif hodnota_dealera == hodnota_hrace:
        hra.hrac.gold += sazka
        hra.kasino.remizy += 1
        _zaznam_hry(
            hra, "Jednadvacet", sazka, 0, "Remíza",
            f"Oba mají {hodnota_hrace}.",
        )
        tisk_info(f"Remíza při {hodnota_hrace}. Sázka se vrací.")
    else:
        _vyhodnot_sazku(
            hra, "Jednadvacet", sazka, True,
            f"Ty {hodnota_hrace}, krupiér {hodnota_dealera}.",
        )
    return True


def _vyhodnot_sazku(hra, hra_nazev, sazka, vyhral, vysledek):
    kasino = hra.kasino
    if vyhral:
        hra.hrac.gold += sazka * 2
        kasino.vyhry += 1
        kasino.cisty_zisk += sazka
        _zaznam_hry(hra, hra_nazev, sazka, sazka, "Výhra", vysledek)
        tisk_ok(f"Výhra! Čistý zisk +{sazka} zl. {vysledek}")
    else:
        kasino.prohry += 1
        kasino.cisty_zisk -= sazka
        _zaznam_hry(hra, hra_nazev, sazka, -sazka, "Prohra", vysledek)
        tisk_info(f"Prohra −{sazka} zl. {vysledek}")


def _zaznam_hry(hra, hra_nazev, sazka, cisty_vysledek, vysledek, detail):
    kasino = hra.kasino
    kasino.celkem_vsazeno += sazka
    kasino.historie.append({
        "den": max(1, int(hra.hrac.den)),
        "hra": hra_nazev,
        "sazka": sazka,
        "cisty_vysledek": cisty_vysledek,
        "vysledek": vysledek,
        "detail": detail,
    })
    kasino.historie = kasino.historie[-20:]


def _over_sazku(hra, sazka):
    kasino = hra.kasino
    if not kasino.otevreno:
        tisk_chyba("Nejdřív otevři kasino.")
        return False
    if isinstance(sazka, bool) or not isinstance(sazka, int):
        tisk_chyba("Sázka musí být celé číslo.")
        return False
    if not MIN_SAZKA <= sazka <= kasino.limit_sazky:
        tisk_chyba(
            f"Sázka musí být od {MIN_SAZKA} do {kasino.limit_sazky} zl."
        )
        return False
    if hra.hrac.gold < sazka:
        tisk_chyba("Nemáš dost zlata na tuto sázku.")
        return False
    return True


def _odeber_sazku(hra, sazka):
    if not _over_sazku(hra, sazka):
        return False
    hra.hrac.gold -= sazka
    return True


def _nacti_sazku(hra):
    try:
        vstup = input(
            f"Sázka ({MIN_SAZKA}–{hra.kasino.limit_sazky} zl., 0 zpět): "
        ).strip()
    except EOFError:
        return None
    if vstup == "0":
        return None
    try:
        sazka = int(vstup)
    except ValueError:
        tisk_chyba("Sázka musí být celé číslo.")
        return None
    return sazka if _over_sazku(hra, sazka) else None


def _nacti_tip_kostek():
    vytiskni_volbu("1", "Pod 7")
    vytiskni_volbu("2", "Nad 7")
    try:
        volba = input("Tip: ").strip()
    except EOFError:
        return None
    if volba in ("1", "pod"):
        return "pod"
    if volba in ("2", "nad"):
        return "nad"
    tisk_chyba("Zvol tip pod nebo nad 7.")
    return None


def zobraz_historii(kasino):
    print("\n=== POSLEDNÍ HRY KASINA ===")
    if not kasino.historie:
        print("Zatím zde není žádný výsledek.")
        return
    for zaznam in reversed(kasino.historie):
        print(
            f"Den {zaznam['den']}: {zaznam['hra']} — {zaznam['vysledek']}, "
            f"sázka {zaznam['sazka']} zl., "
            f"výsledek {zaznam['cisty_vysledek']:+} zl. "
            f"({zaznam['detail']})"
        )


def _cena_vylepseni(uroven):
    return 250 * uroven


def _tahni_kartu():
    hod = random.randint(1, 13)
    if hod == 1:
        return 11
    return min(hod, 10)


def _hodnota_ruky(karty):
    hodnota = sum(karty)
    esa = sum(karta == 11 for karta in karty)
    while hodnota > 21 and esa:
        hodnota -= 10
        esa -= 1
    return hodnota


def _popis_karet(karty):
    return ", ".join("A" if karta == 11 else str(karta) for karta in karty)

"""Nábor, úkoly a denní provoz personálu dominia."""

import random

from models.agent import Agent
from utils.vypis import clear, tisk_chyba, tisk_info, tisk_ok, vytiskni_volbu


SPECIALIZACE = {
    "pruzkumnik": {
        "nazev": "Průzkumník", "cena": 120, "plat": 6,
        "ukol": "Prohledává mapu a odhaluje přilehlé lokace.",
    },
    "herold": {
        "nazev": "Herold", "cena": 100, "plat": 5,
        "ukol": "Šíří zprávy o tvých činech a posiluje pověst města.",
    },
    "spravce": {
        "nazev": "Správce zásob", "cena": 140, "plat": 4,
        "ukol": "Zajišťuje každodenní příjem a obchodní zásobování.",
    },
    "lekar": {
        "nazev": "Polní lékař", "cena": 160, "plat": 6,
        "ukol": "Ošetřuje tebe i aktivní členy harému.",
    },
    "velitel": {
        "nazev": "Válečný velitel", "cena": 250, "plat": 8,
        "ukol": "Cvičí armádu a zvyšuje její morálku.",
    },
}

JMENA_PERSONALU = {
    "pruzkumnik": ("Karel", "Běla", "Radek"),
    "herold": ("Jitka", "Marek", "Věra"),
    "spravce": ("Ota", "Milena", "Bohdan"),
    "lekar": ("Mira", "Viktor", "Sára"),
    "velitel": ("Varek", "Tereza", "Dobromil"),
}

ROZKAZY_ARMADY = {
    "hlidkovat": "Hlídky — zvyšují městskou reputaci a klid",
    "vycvik": "Výcvik — připravuje oddíly a zvyšuje bojovou morálku",
    "patrolovat": "Patrola — posiluje kontrolu nejslabšího území",
    "tažení": "Tažení — riskantní výprava za kořistí",
}


def najmi_personal(hra, specializace):
    definice = SPECIALIZACE.get(specializace)
    if not definice:
        return False
    if len(hra.hrac.agenti) >= max(1, hra.hrac.max_agentu):
        tisk_chyba("Nemáš volné místo v personálu. Rozšiř kapacitu v této správě.")
        return False
    if hra.hrac.gold < definice["cena"]:
        tisk_chyba(f"Nábor stojí {definice['cena']} zlata.")
        return False
    hra.hrac.gold -= definice["cena"]
    jmena = JMENA_PERSONALU[specializace]
    obsazena = {agent.jmeno for agent in hra.hrac.agenti}
    jmeno = next(
        (moznost for moznost in jmena if moznost not in obsazena),
        f"{jmena[0]} {len(hra.hrac.agenti) + 1}",
    )
    agent = Agent(
        jmeno=jmeno,
        specializace=specializace,
        ukol=specializace,
        cil_lokace=hra.svet.aktualni_lokace,
        plat=definice["plat"],
    )
    hra.hrac.agenti.append(agent)
    tisk_ok(
        f"Najat {definice['nazev']} {jmeno}. "
        f"Počáteční cena {definice['cena']} zl., denní plat {definice['plat']} zl."
    )
    return True


def menu_personalu(hra):
    while True:
        clear()
        print("=== PERSONÁL DOMINIA ===")
        print(
            f"Pokladna: {hra.hrac.gold} zl. | "
            f"Obsazená místa: {len(hra.hrac.agenti)}/{hra.hrac.max_agentu}"
        )
        if hra.hrac.agenti:
            for index, agent in enumerate(hra.hrac.agenti, 1):
                definice = SPECIALIZACE.get(agent.specializace, {})
                print(
                    f"{index}) {agent.jmeno} — "
                    f"{definice.get('nazev', agent.specializace)}, "
                    f"denní plat {agent.plat} zl., mise: {agent.ukol or 'bez úkolu'}"
                )
        else:
            print("Zatím nemáš najatý personál.")
        vytiskni_volbu("1", "Najmout pracovníka")
        vytiskni_volbu("2", "Přeřadit pracovníka na jinou misi")
        vytiskni_volbu(
            "3",
            f"Rozšířit kapacitu o jedno místo ({150 + hra.hrac.max_agentu * 100} zl.)",
        )
        vytiskni_volbu("4", "Nastavit rozkazy armády")
        vytiskni_volbu("0", "Zpět")
        try:
            volba = input("> ").strip()
        except EOFError:
            return
        if volba == "0":
            return
        if volba == "1":
            for index, (klic, definice) in enumerate(SPECIALIZACE.items(), 1):
                vytiskni_volbu(
                    str(index),
                    f"{definice['nazev']} — {definice['ukol']} "
                    f"({definice['cena']} zl., {definice['plat']} zl./den)",
                )
            vytiskni_volbu("0", "Zpět")
            try:
                volba_naboru = input("> ").strip()
                if volba_naboru == "0":
                    continue
                index = int(volba_naboru) - 1
                if not 0 <= index < len(SPECIALIZACE):
                    continue
                specializace = tuple(SPECIALIZACE)[index]
            except (ValueError, IndexError):
                continue
            najmi_personal(hra, specializace)
            continue
        if volba == "2":
            _predelej_misi(hra)
        elif volba == "3":
            cena = 150 + hra.hrac.max_agentu * 100
            if hra.hrac.gold < cena:
                tisk_chyba(f"Rozšíření kapacity stojí {cena} zlata.")
            else:
                hra.hrac.gold -= cena
                hra.hrac.max_agentu += 1
                tisk_ok(f"Personál má nyní kapacitu {hra.hrac.max_agentu}.")
        elif volba == "4":
            nastav_rozkaz_armady(hra)


def _predelej_misi(hra):
    if not hra.hrac.agenti:
        tisk_info("Nejdřív najmi pracovníka.")
        return
    for index, agent in enumerate(hra.hrac.agenti, 1):
        print(f"{index}) {agent.jmeno} — {agent.ukol}")
    try:
        agent_index = int(input("Pracovník: ")) - 1
        if not 0 <= agent_index < len(hra.hrac.agenti):
            raise IndexError
        agent = hra.hrac.agenti[agent_index]
    except (ValueError, IndexError):
        tisk_chyba("Neplatná volba.")
        return
    moznosti = list(SPECIALIZACE)
    for index, ident in enumerate(moznosti, 1):
        definice = SPECIALIZACE[ident]
        vytiskni_volbu(str(index), f"{definice['nazev']}: {definice['ukol']}")
    try:
        volba = int(input("Nová mise: ")) - 1
        specializace = moznosti[volba]
    except (ValueError, IndexError):
        tisk_chyba("Neplatná mise.")
        return
    agent.specializace = specializace
    agent.ukol = specializace
    agent.plat = SPECIALIZACE[specializace]["plat"]
    agent.cil_lokace = hra.svet.aktualni_lokace
    tisk_ok(f"{agent.jmeno} nastupuje na misi: {SPECIALIZACE[specializace]['nazev']}.")


def nastav_rozkaz_armady(hra):
    if hra.mafie.vojaci + hra.mafie.kapitanove <= 0:
        tisk_info("Nejdřív naverbuj vojáky nebo kapitána ve správě podsvětí.")
        return
    for index, (ident, text) in enumerate(ROZKAZY_ARMADY.items(), 1):
        aktivni = " [aktivní]" if hra.mafie.rozkaz_armady == ident else ""
        vytiskni_volbu(str(index), text + aktivni)
    try:
        index = int(input("Rozkaz: ")) - 1
        if not 0 <= index < len(ROZKAZY_ARMADY):
            raise IndexError
        hra.mafie.rozkaz_armady = tuple(ROZKAZY_ARMADY)[index]
    except (ValueError, IndexError):
        tisk_chyba("Neplatný rozkaz.")
        return
    tisk_ok(f"Rozkaz armády nastaven: {ROZKAZY_ARMADY[hra.mafie.rozkaz_armady]}.")


def zpracuj_denni_personal(hra):
    """Zaplacení mezd a provedení přidělených misí po denních příjmech."""
    agenti = [
        agent for agent in hra.hrac.agenti
        if agent.ukol in SPECIALIZACE
    ]
    mohou_pracovat = True
    if agenti:
        celkove_platy = sum(max(0, int(agent.plat)) for agent in agenti)
        if hra.hrac.gold < celkove_platy:
            tisk_chyba(
                f"Personál dnes odpočívá: na denní platy {celkove_platy} zl. "
                "není dost zlata."
            )
            mohou_pracovat = False
        else:
            hra.hrac.gold -= celkove_platy
            tisk_info(f"Mzdy personálu: −{celkove_platy} zlata.")

    zpravy = []
    for agent in (agenti if mohou_pracovat else ()):
        zacatek_zprav = len(zpravy)
        if agent.ukol == "pruzkumnik":
            zpravy.extend(_mise_pruzkumnika(hra, agent))
        elif agent.ukol == "herold":
            pred = hra.hrac.reputace_mesta
            hra.hrac.reputace_mesta = min(100, pred + 1)
            zpravy.append(f"{agent.jmeno} rozšířil zprávy o dominiu; reputace +{hra.hrac.reputace_mesta - pred}.")
        elif agent.ukol == "spravce":
            hra.hrac.gold += 8
            zpravy.append(f"{agent.jmeno} zajistil obchodní příjem +8 zlata.")
        elif agent.ukol == "lekar":
            leceni_hrace = min(8, hra.hrac.max_hp - hra.hrac.hp)
            hra.hrac.hp += leceni_hrace
            leceni_haremu = 0
            for postava in hra.harem.vsechny_aktivni():
                pred = postava.hp
                postava.hp = min(postava.max_hp, postava.hp + 3)
                leceni_haremu += postava.hp - pred
            zpravy.append(
                f"{agent.jmeno} ošetřil dominium (ty +{leceni_hrace} HP, "
                f"harém +{leceni_haremu} HP)."
            )
        elif agent.ukol == "velitel":
            pred = hra.mafie.moral_armady
            hra.mafie.moral_armady = min(100, pred + 5)
            zpravy.append(f"{agent.jmeno} vedl výcvik; morálka armády +{hra.mafie.moral_armady - pred}.")
        agent.xp += 10
        if agent.xp >= agent.level * 50:
            agent.xp -= agent.level * 50
            agent.level += 1
            zpravy.append(f"{agent.jmeno} získal zkušenosti a postoupil na úroveň {agent.level}.")
        agent.posledni_akce = (
            zpravy[-1] if len(zpravy) > zacatek_zprav else ""
        )
    for zprava in zpravy:
        tisk_ok(zprava)

    _zpracuj_armadni_rozkaz(hra)
    return zpravy


def _mise_pruzkumnika(hra, agent):
    from game.svet import LOKACE

    svet = hra.svet
    cil = agent.cil_lokace if agent.cil_lokace in svet.odhalene_lokace else svet.aktualni_lokace
    sousedni = LOKACE.get(cil, {}).get("sousedni", [])
    neznama = [
        lokace for lokace in sousedni
        if lokace not in svet.odhalene_lokace and lokace in LOKACE
    ]
    if neznama:
        nova = random.choice(neznama)
        svet.odhal_lokaci(nova)
        agent.cil_lokace = nova
        vysledek = f"{agent.jmeno} prozkoumal okolí a odhalil lokaci {LOKACE[nova]['nazev']}."
    elif random.random() < 0.25:
        nalez = random.randint(8, 20)
        hra.hrac.gold += nalez
        vysledek = f"{agent.jmeno} prohledal známé stezky a našel {nalez} zlata."
    else:
        vysledek = f"{agent.jmeno} zmapoval okolí lokace {cil.replace('_', ' ')}."
    return [vysledek]


def _zpracuj_armadni_rozkaz(hra):
    mafie = hra.mafie
    pocet_oddilu = max(0, mafie.vojaci) + max(0, mafie.kapitanove)
    if not pocet_oddilu:
        return
    if getattr(mafie, "placena_armada", False):
        mzdy = mafie.vojaci + mafie.kapitanove * 4
        if hra.hrac.gold < mzdy:
            tisk_chyba(f"Armáda dnes nevyrazila: chybí {mzdy} zl. na žold.")
            return
        hra.hrac.gold -= mzdy
        tisk_info(f"Žold armády: −{mzdy} zlata.")
    rozkaz = mafie.rozkaz_armady
    if rozkaz == "vycvik":
        pred = mafie.moral_armady
        mafie.moral_armady = min(100, pred + 4 + mafie.kapitanove)
        tisk_ok(f"Armáda dokončila výcvik. Morálka {pred} → {mafie.moral_armady}.")
    elif rozkaz == "patrolovat":
        uzemi = [
            u for u in mafie.uzemi
            if u.obsazeno and u.kontrola < 100
        ]
        if uzemi:
            cil = min(uzemi, key=lambda u: (u.kontrola, u.nazev))
            cil.kontrola = min(100, cil.kontrola + 2 + mafie.kapitanove)
            tisk_ok(f"Armádní hlídka posílila kontrolu v {cil.nazev} na {cil.kontrola} %.")
        else:
            tisk_info("Hlídky prošly městskými ulicemi; nemáš žádné území k zabezpečení.")
    elif rozkaz == "tažení":
        sila = mafie.bojova_sila()
        if sila >= 12:
            korist = random.randint(12, 24) + mafie.kapitanove * 4
            hra.hrac.gold += korist
            mafie.moral_armady = min(100, mafie.moral_armady + 2)
            tisk_ok(f"Vojenské tažení uspělo. Kořist +{korist} zlata; morálka +2.")
        elif mafie.vojaci:
            mafie.vojaci -= 1
            mafie.moral_armady = max(0, mafie.moral_armady - 5)
            tisk_chyba("Tažení selhalo; armáda ztratila jednoho vojáka a 5 morálky.")
    else:
        hrac_rep = hra.hrac.reputace_mesta
        hra.hrac.reputace_mesta = min(100, hrac_rep + 1)
        if "policie" in hra.frakce.frakce:
            hra.frakce.frakce["policie"].zmenit(1)
        tisk_info("Armádní hlídky uklidnily město. Reputace +1.")

"""Nábor, úkoly a denní provoz personálu dominia."""

import random

from data.mesta import MESTA
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

STYLY_MISE = {
    "vyvazene": ("Vyváženě", 0, None),
    "setrne": ("Úsporně (denní mzda −2 zl., nejméně 0)", -2, None),
    "podpora": ("Podpořit cílové město (+1 stabilita, mzda +1 zl.)", 1, "stabilita"),
    "intenzivni": ("Pracovat intenzivně (+1 prosperita, mzda +2 zl.)", 2, "prosperita"),
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
        cil_mesto=_mesto_lokace(hra.svet.aktualni_lokace),
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
                    f"denní plat {_denni_plat(agent)} zl., mise: {agent.ukol or 'bez úkolu'}, "
                    f"styl: {STYLY_MISE.get(agent.styl_mise, STYLY_MISE['vyvazene'])[0]}, "
                    f"oblast: {MESTA.get(getattr(agent, 'cil_mesto', ''), {}).get('nazev', 'Staré město')}"
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
        vyber = input("Nová mise: ").strip()
        if vyber == "0":
            return
        volba = int(vyber) - 1
        if not 0 <= volba < len(moznosti):
            raise IndexError
        specializace = moznosti[volba]
    except (ValueError, IndexError):
        tisk_chyba("Neplatná mise.")
        return
    agent.specializace = specializace
    agent.ukol = specializace
    agent.plat = SPECIALIZACE[specializace]["plat"]
    print("\nStyl mise:")
    styly = tuple(STYLY_MISE)
    for index, styl in enumerate(styly, 1):
        vytiskni_volbu(str(index), STYLY_MISE[styl][0])
    vytiskni_volbu("0", "Ponechat vyvážený styl")
    try:
        vyber_styl = input("Styl: ").strip()
        if vyber_styl != "0":
            styl_index = int(vyber_styl) - 1
            if not 0 <= styl_index < len(styly):
                raise IndexError
            agent.styl_mise = styly[styl_index]
    except (EOFError, ValueError, IndexError):
        agent.styl_mise = "vyvazene"
    mesta = tuple(MESTA)
    for index, mesto_id in enumerate(mesta, 1):
        vytiskni_volbu(str(index), MESTA[mesto_id]["nazev"])
    vytiskni_volbu("0", "Ponechat aktuální oblast")
    try:
        volba_mesta = input("Cílové město: ").strip()
        mesto_index = int(volba_mesta) - 1 if volba_mesta != "0" else -1
        cil_mesto = (
            mesta[mesto_index]
            if 0 <= mesto_index < len(mesta)
            else _mesto_lokace(hra.svet.aktualni_lokace)
        )
    except (EOFError, ValueError, IndexError):
        cil_mesto = _mesto_lokace(hra.svet.aktualni_lokace)
    agent.cil_mesto = cil_mesto
    tisk_ok(
        f"{agent.jmeno} nastupuje na misi: {SPECIALIZACE[specializace]['nazev']} "
        f"(oblast: {MESTA[cil_mesto]['nazev']})."
    )


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
        celkove_platy = sum(_denni_plat(agent) for agent in agenti)
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
            mesto = _stav_mesta(hra, agent)
            mesto.uprav(stabilita=1)
            zpravy.append(
                f"{agent.jmeno} rozšířil zprávy o dominiu v {mesto.nazev}; "
                f"reputace +{hra.hrac.reputace_mesta - pred}, stabilita +1."
            )
        elif agent.ukol == "spravce":
            mesto = _stav_mesta(hra, agent)
            prijem = 8 + mesto.prosperita // 25
            if mesto.bezpeci < 20:
                prijem //= 2
            hra.hrac.gold += prijem
            zpravy.append(
                f"{agent.jmeno} zajistil obchodní příjem v {mesto.nazev} "
                f"+{prijem} zlata."
            )
        elif agent.ukol == "lekar":
            mesto = _stav_mesta(hra, agent)
            mesto.uprav(bezpeci=1)
            leceni_hrace = min(8, hra.hrac.max_hp - hra.hrac.hp)
            hra.hrac.hp += leceni_hrace
            leceni_haremu = 0
            for postava in hra.harem.vsechny_aktivni():
                pred = postava.hp
                postava.hp = min(postava.max_hp, postava.hp + 3)
                leceni_haremu += postava.hp - pred
            zpravy.append(
                f"{agent.jmeno} ošetřil dominium (ty +{leceni_hrace} HP, "
                f"harém +{leceni_haremu} HP, {mesto.nazev}: bezpečí +1)."
            )
        elif agent.ukol == "velitel":
            mesto = _stav_mesta(hra, agent)
            mesto.uprav(bezpeci=2)
            pred = hra.mafie.moral_armady
            hra.mafie.moral_armady = min(100, pred + 5)
            zpravy.append(
                f"{agent.jmeno} vedl výcvik v oblasti {mesto.nazev}; "
                f"morálka armády +{hra.mafie.moral_armady - pred}, bezpečí +2."
            )
        styl = STYLY_MISE.get(
            getattr(agent, "styl_mise", "vyvazene"),
            STYLY_MISE["vyvazene"],
        )
        metrika = styl[2]
        if metrika:
            mesto = _stav_mesta(hra, agent)
            mesto.uprav(**{metrika: 1})
            zpravy.append(
                f"Styl mise „{styl[0]}“: {mesto.nazev} "
                f"{'stabilita' if metrika == 'stabilita' else 'prosperita'} +1."
            )
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
    from utils.decision_ai import vzdalenosti_od_cilu

    svet = hra.svet
    cil = agent.cil_lokace if agent.cil_lokace in svet.odhalene_lokace else svet.aktualni_lokace
    mesto_id = _cilove_mesto(hra, agent)
    lokace_mesta = set(MESTA[mesto_id]["lokace"])
    if cil not in lokace_mesta:
        vzdalenosti = vzdalenosti_od_cilu(
            {lokace_id: data["sousedni"] for lokace_id, data in LOKACE.items()},
            lokace_mesta,
        )
        sousedi = LOKACE.get(cil, {}).get("sousedni", [])
        kandidat = min(
            (lokace for lokace in sousedi if lokace in vzdalenosti),
            key=lambda lokace: vzdalenosti[lokace],
            default=None,
        )
        if kandidat and vzdalenosti.get(kandidat, 0) < vzdalenosti.get(cil, 0):
            svet.odhal_lokaci(kandidat)
            agent.cil_lokace = kandidat
            return [
                f"{agent.jmeno} postupuje po mapě směrem do {MESTA[mesto_id]['nazev']}."
            ]
    sousedni = LOKACE.get(cil, {}).get("sousedni", [])
    neznama = [
        lokace for lokace in sousedni
        if lokace not in svet.odhalene_lokace and lokace in LOKACE
        and LOKACE[lokace].get("mesto", "stare_mesto") == mesto_id
    ]
    if neznama:
        nova = random.choice(neznama)
        svet.odhal_lokaci(nova)
        agent.cil_lokace = nova
        vysledek = (
            f"{agent.jmeno} prozkoumal okolí města {MESTA[mesto_id]['nazev']} "
            f"a odhalil lokaci {LOKACE[nova]['nazev']}."
        )
    elif random.random() < 0.25:
        nalez = random.randint(8, 20)
        hra.hrac.gold += nalez
        vysledek = f"{agent.jmeno} prohledal známé stezky a našel {nalez} zlata."
    else:
        vysledek = f"{agent.jmeno} zmapoval okolí lokace {cil.replace('_', ' ')}."
    return [vysledek]


def _cilove_mesto(hra, agent):
    mesto_id = getattr(agent, "cil_mesto", "")
    if mesto_id in MESTA:
        return mesto_id
    return _mesto_lokace(getattr(agent, "cil_lokace", hra.svet.aktualni_lokace))


def _denni_plat(agent):
    styl = STYLY_MISE.get(
        getattr(agent, "styl_mise", "vyvazene"),
        STYLY_MISE["vyvazene"],
    )
    return max(0, int(agent.plat) + styl[1])


def _mesto_lokace(lokace_id):
    from game.svet import LOKACE

    return LOKACE.get(lokace_id, {}).get("mesto", "stare_mesto")


def _stav_mesta(hra, agent):
    mesto_id = _cilove_mesto(hra, agent)
    return hra.zivy_svet.mesta[mesto_id]


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

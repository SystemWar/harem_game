"""Sestavení aktivních cílů a doporučeného dalšího kroku podle stavu hry."""

from game.svet import LOKACE, NPC


def _cislo_volby(stare_cislo):
    from game.menu_hlavni import POLOZKY_HLAVNIHO_MENU

    for nove_cislo, (stare, _popis) in enumerate(POLOZKY_HLAVNIHO_MENU, 1):
        if stare == str(stare_cislo):
            return nove_cislo
    return stare_cislo


def _nazev_lokace(lokace_id):
    return LOKACE.get(lokace_id, {}).get("nazev", lokace_id or "neznámé lokaci")


def prehled_uvodu(hra):
    """Krátký, na skutečném postupu založený checklist pro první hodinu hry."""
    rozhovory = getattr(hra.svet, "pamet_rozhovoru", {})
    mluvil_s_npc = False
    if isinstance(rozhovory, dict):
        for zaznam in rozhovory.values():
            if not isinstance(zaznam, dict):
                continue
            try:
                mluvil_s_npc = int(zaznam.get("pocet", 0) or 0) > 0
            except (TypeError, ValueError):
                mluvil_s_npc = False
            if mluvil_s_npc:
                break
    kroky = (
        (
            bool(hra.svet.navstiveno.get("trh", 0)),
            "Navštiv Starý trh a objev první stopu kampaně.",
            f"Mapa ({_cislo_volby('8')}) → Starý trh.",
        ),
        (
            mluvil_s_npc,
            "Promluv s NPC; postavy si pamatují, jak ses zachoval.",
            f"Na Starém trhu stiskni N a oslov Miru nebo Eliana.",
        ),
        (
            hra.hrac.den > 1,
            "Odpočiň si a sleduj, jak na tvá rozhodnutí zareaguje město.",
            f"Odpočinek ({_cislo_volby('12')}) posune svět do dalšího dne.",
        ),
    )
    splneno = sum(1 for hotovo, _, _ in kroky if hotovo)
    dalsi = next((krok for krok in kroky if not krok[0]), None)
    return {
        "kroky": kroky,
        "splneno": splneno,
        "doporuceni": dalsi[2] if dalsi else "",
    }


def _cil_kampane(hra):
    kapitola = hra.kampan.aktualni()
    if not kapitola:
        return None, None

    cil = kapitola.get("cil")
    lokaci_id = kapitola.get("lokace")
    nazev = kapitola.get("nazev", "Hlavní příběh")
    if cil == "navstiv_trh":
        if hra.svet.navstiveno.get("trh", 0):
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Otevři kampaň ({_cislo_volby('9')}) a potvrď dokončení návštěvy trhu.",
            )
        return (
            f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
            f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(lokaci_id)}; navštiv lokaci a prozkoumej ji.",
        )
    if cil == "vyber_spojence":
        if not hra.svet.navstiveno.get("pristav", 0):
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Mapa ({_cislo_volby('8')}) → Černý přístav; po návštěvě zvol spojence v kampani ({_cislo_volby('9')}).",
            )
        return (
            f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
            f"Kampaň ({_cislo_volby('9')}) → vyber spojence Miru nebo Radana.",
        )
    if cil == "uzavri_kampan":
        if not hra.svet.navstiveno.get("hranice", 0):
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Mapa ({_cislo_volby('8')}) → Hraniční ves; navštiv ji, pak pokračuj kampaní ({_cislo_volby('9')}).",
            )
        return (
            f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
            f"Kampaň ({_cislo_volby('9')}) → rozhodni, zda síť odhalíš, nebo využiješ.",
        )
    if cil == "navstiv_zahradu":
        if hra.svet.navstiveno.get("sklenena_zahrada", 0):
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Otevři kampaň ({_cislo_volby('9')}) a potvrď dokončení návštěvy zahrady.",
            )
        return (
            f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
            f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(lokaci_id)}; návštěva odemkne další část příběhu.",
        )
    if cil == "uzavri_hvezdny_slib":
        observator = kapitola.get("lokace", "observator")
        if observator not in hra.svet.odhalene_lokace:
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Pokračuj předchozím cílem kampaně ({_cislo_volby('9')}); nejdřív se musí odhalit observatoř.",
            )
        if hra.svet.aktualni_lokace != observator:
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(observator)}.",
            )
        if "strazce_hvezdne_brany" not in hra.kampan.boss_porazeni:
            return (
                f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
                f"Souboj ({_cislo_volby('18')}) → poraz Strážce hvězdné brány.",
            )
        return (
            f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
            f"Kampaň ({_cislo_volby('9')}) → vyber závěr příběhu.",
        )
    return (
        f"Kampaň {hra.kampan.kapitola + 1}/5: {nazev}",
        f"Otevři kampaň ({_cislo_volby('9')}) a zkontroluj podmínky dalšího kroku.",
    )


def _cil_bezneho_ukolu(hra):
    quest = hra.questy.aktivni_quest
    if not isinstance(quest, dict):
        return None, None
    nazev = quest.get("nazev", "Aktivní úkol")
    lokaci_id = quest.get("lokace")
    zbyva = max(0, int(getattr(hra.questy, "dny_zbyva", 0)))
    if lokaci_id and hra.svet.aktualni_lokace != lokaci_id:
        doporuceni = f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(lokaci_id)}; pak plň úkol v menu ({_cislo_volby('14')})"
    else:
        doporuceni = f"Questy ({_cislo_volby('14')}) → zvol „Plnit quest“"
    if zbyva:
        doporuceni += f" (zbývá {zbyva} dní)."
    else:
        doporuceni += "."
    return f"Úkol: {nazev} (zbývá {zbyva} dní)", doporuceni


def _cil_npc_ukolu(hra):
    aktivni = getattr(hra.npc_questy, "aktivni", {})
    if not isinstance(aktivni, dict) or not aktivni:
        return None, None
    npc_id, zaznam = next(iter(aktivni.items()))
    quest = zaznam.get("quest", {}) if isinstance(zaznam, dict) else {}
    data_npc = NPC.get(npc_id, {})
    lokaci_id = data_npc.get("lokace")
    jmeno = data_npc.get("jmeno", npc_id)
    nazev_ukolu = quest.get("nazev", "Aktivní úkol NPC")
    if lokaci_id and hra.svet.aktualni_lokace != lokaci_id:
        doporuceni = (
            f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(lokaci_id)}; "
            f"promluv s {jmeno}."
        )
    else:
        doporuceni = f"Promluv s {jmeno} a pokračuj v úkolu „{nazev_ukolu}“."
    return f"Úkol NPC: {nazev_ukolu} — {jmeno}", doporuceni


def prehled_cilu(hra):
    """Vrátí krátké cíle a jedno prioritní doporučení pro hlavní menu."""
    kampan_cil, kampan_krok = _cil_kampane(hra)
    bezny_cil, bezny_krok = _cil_bezneho_ukolu(hra)
    npc_cil, npc_krok = _cil_npc_ukolu(hra)

    aktivni = [
        cil for cil in (kampan_cil, bezny_cil, npc_cil) if cil
    ]
    npc_aktivni = getattr(hra.npc_questy, "aktivni", {})
    npc_aktivni = npc_aktivni if isinstance(npc_aktivni, dict) else {}
    if len(npc_aktivni) > 1 and npc_cil:
        pocet = len(npc_aktivni) - 1
        aktivni.append(f"a další úkoly NPC ({pocet})")

    doporuceni = next(
        (
            krok for krok in (bezny_krok, kampan_krok, npc_krok)
            if krok
        ),
        None,
    )
    if not doporuceni and hra.kampan.dokonceno:
        dostupne = hra.npc_questy.dostupne(hra)
        pristupne = [
            (npc_id, quest)
            for npc_id, quest in dostupne
            if NPC.get(npc_id, {}).get("lokace") in hra.svet.odhalene_lokace
        ]
        if pristupne:
            npc_id, quest = pristupne[0]
            npc = NPC.get(npc_id, {})
            lokaci_id = npc.get("lokace")
            jmeno = npc.get("jmeno", npc_id)
            if lokaci_id == hra.svet.aktualni_lokace:
                doporuceni = f"Promluv s {jmeno}; může ti zadat úkol „{quest['nazev']}“."
            else:
                doporuceni = (
                    f"Mapa ({_cislo_volby('8')}) → {_nazev_lokace(lokaci_id)}; "
                    f"promluv s {jmeno} a přijmi úkol."
                )
    if not doporuceni:
        doporuceni = (
            f"Získej nový úkol v menu Questy ({_cislo_volby('14')}) "
            "nebo pokračuj v průzkumu světa."
        )

    return {"aktivni": aktivni, "doporuceni": doporuceni}


def doporuceni_pro_pruvodce(hra):
    """Doporučení pro samostatnou obrazovku průvodce."""
    return [prehled_cilu(hra)["doporuceni"]]

"""Volitelné příběhové události, které se nabídnou po příchodu nového dne."""

import random

from utils.vypis import tisk_info, tisk_ok, vytiskni_volbu
from game.kronika import zaznamenej


PRIBEHOVE_LINKY = {
    "inkvizicni_stop": {
        "nazev": "Inkviziční stopa",
        "vaha": lambda hra: 1 + max(0, hra.hrac.vliv_inkvizice // 25),
        "etapy": (
            {
                "titulek": "Zvědové inkvizice",
                "text": (
                    "Hlídka inkvizice se vyptává na tvé kontakty. "
                    "Můžeš zaplatit informátorovi, nebo rozšířit falešnou stopu."
                ),
                "moznosti": (
                    {
                        "text": "Zaplatit 40 zlata za odvedení hlídky",
                        "vetv": "platba",
                        "efekt": "inkvizice_platba",
                        "cena": 40,
                    },
                    {
                        "text": "Rozšířit falešnou stopu",
                        "vetv": "falesna_stopa",
                        "efekt": "inkvizice_falesna",
                    },
                ),
            },
            {
                "titulek": "Zpráva z ulice",
                "text": "Informátor přináší zprávu o tom, jak inkvizice zareagovala.",
                "vysledky": {
                    "platba": (
                        "inkvizice_zaplaceno",
                        "Zaplatila se hlídka; pozornost inkvizice ochabla.",
                    ),
                    "falesna_stopa": (
                        "inkvizice_falesna_stopa",
                        "Falešná stopa odvedla inkvizici jinam, ale město si všimlo rozruchu.",
                    ),
                },
            },
        ),
    },
    "cechovni_karavana": {
        "nazev": "Kupecká karavana",
        "vaha": lambda hra: 1 + max(
            0, hra.frakce.frakce["obchodnici"].reputace // 20
        ),
        "etapy": (
            {
                "titulek": "Karavana v nesnázích",
                "text": (
                    "Kupecká karavana uvízla za městskou branou. Cech nabízí "
                    "dlouhodobou přízeň za pomoc, nebo rychlý podíl za zboží."
                ),
                "moznosti": (
                    {
                        "text": "Přispět 30 zlata na opravu vozů",
                        "vetv": "pomoc",
                        "efekt": "karavana_pomoc",
                        "cena": 30,
                    },
                    {
                        "text": "Vyjednat okamžitý podíl na nákladu",
                        "vetv": "podil",
                        "efekt": "karavana_podil_start",
                    },
                ),
            },
            {
                "titulek": "Odměna od cechu",
                "text": "Cech posílá závěrečné vyúčtování za karavanu.",
                "vysledky": {
                    "pomoc": (
                        "karavana_odmena",
                        "Karavana dorazila v pořádku a cech ocenil tvou pomoc.",
                    ),
                    "podil": (
                        "karavana_podil_end",
                        "Obchod proběhl rychle; kupci si ale pamatují tvrdé vyjednávání.",
                    ),
                },
            },
        ),
    },
    "rivalni_posel": {
        "nazev": "Posel rivala",
        "vaha": lambda hra: 1 + len(hra.mafie.uzemi),
        "etapy": (
            {
                "titulek": "Ultimátum od rivala",
                "text": (
                    "Posel soupeřícího syndikátu žádá ústupek v městské síti. "
                    "Můžeš otevřít jednání, nebo odmítnout a dát najevo odhodlání."
                ),
                "moznosti": (
                    {
                        "text": "Poslat vyjednavače (25 zlata)",
                        "vetv": "jednani",
                        "efekt": "rival_jednani",
                        "cena": 25,
                    },
                    {
                        "text": "Odmítnout ultimátum",
                        "vetv": "odmitnuti",
                        "efekt": "rival_odmitnuti_start",
                    },
                ),
            },
            {
                "titulek": "Odezva rivala",
                "text": "Zpráva odhaluje, zda rival přijal tvou odpověď.",
                "vysledky": {
                    "jednani": (
                        "rival_dohoda",
                        "Vyjednavač získal krátké příměří a posílil tvou pověst.",
                    ),
                    "odmitnuti": (
                        "rival_odmitnuti_end",
                        "Rival ustoupil před tvým odhodláním; jeho posel zanechal užitečný obnos.",
                    ),
                },
            },
        ),
    },
}

SAMOSTATNE_UDALOSTI = (
    {
        "id": "mestsky_svatecni_trh",
        "titulek": "Sváteční trh",
        "text": "Na náměstí se koná trh a radní žádají o příspěvek na výzdobu.",
        "moznosti": (
            {
                "text": "Přispět 20 zlata na výzdobu",
                "vetv": "prispevek",
                "efekt": "trh_prispevek",
                "cena": 20,
            },
            {
                "text": "Pronajmout stánek a prodat zásoby",
                "vetv": "stanek",
                "efekt": "trh_stanek",
            },
        ),
    },
    {
        "id": "ztracena_mapa",
        "titulek": "Ztracená mapa",
        "text": "Poslíček nabízí starou mapu s poznámkami k zapomenutým ruinám.",
        "moznosti": (
            {
                "text": "Koupit mapu za 15 zlata",
                "vetv": "koupit",
                "efekt": "mapa_koupit",
                "cena": 15,
            },
            {
                "text": "Předat mapu badatelům města",
                "vetv": "predat",
                "efekt": "mapa_predat",
            },
        ),
    },
    {
        "id": "ztraceny_vuz",
        "titulek": "Ztracený vůz",
        "text": "U cesty stojí poškozený vůz. Majitel prosí o pomoc s opravou nápravy.",
        "moznosti": (
            {
                "text": "Zaplatit 10 zlata za opravu",
                "vetv": "opravit",
                "efekt": "vuz_opravit",
                "cena": 10,
            },
            {
                "text": "Koupit zachráněný náklad za 20 zlata",
                "vetv": "vykoupit",
                "efekt": "vuz_vykoupit",
                "cena": 20,
            },
        ),
    },
)


def _zmen_frakci(hra, frakce_id, delta):
    frakce = hra.frakce.frakce.get(frakce_id)
    if frakce:
        frakce.zmenit(delta)


def _aplikuj_efekt(hra, efekt):
    hrac = hra.hrac
    if efekt == "inkvizice_platba":
        hrac.gold -= 40
        hrac.vliv_inkvizice = max(0, hrac.vliv_inkvizice - 4)
        _zmen_frakci(hra, "cirkev", -2)
    elif efekt == "inkvizice_falesna":
        hrac.vliv_inkvizice = min(100, hrac.vliv_inkvizice + 3)
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 1)
    elif efekt == "inkvizice_zaplaceno":
        hrac.vliv_inkvizice = max(0, hrac.vliv_inkvizice - 2)
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 1)
    elif efekt == "inkvizice_falesna_stopa":
        hrac.vliv_inkvizice = max(0, hrac.vliv_inkvizice - 1)
        hrac.gold += 25
    elif efekt == "karavana_pomoc":
        hrac.gold -= 30
        _zmen_frakci(hra, "obchodnici", 4)
    elif efekt == "karavana_podil_start":
        hrac.gold += 25
        _zmen_frakci(hra, "obchodnici", -2)
    elif efekt == "karavana_odmena":
        hrac.gold += 55
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 1)
        _zmen_frakci(hra, "obchodnici", 2)
    elif efekt == "rival_jednani":
        hrac.gold -= 25
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 3)
    elif efekt == "rival_odmitnuti_start":
        hrac.vliv_inkvizice = min(100, hrac.vliv_inkvizice + 2)
        _zmen_frakci(hra, "syndikat_stinu", -2)
    elif efekt == "rival_dohoda":
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 2)
        hrac.vliv_inkvizice = max(0, hrac.vliv_inkvizice - 1)
    elif efekt == "rival_odmitnuti_end":
        hrac.gold += 15
        _zmen_frakci(hra, "syndikat_stinu", -1)
    elif efekt == "karavana_podil_end":
        hrac.gold += 30
        _zmen_frakci(hra, "obchodnici", -1)
    elif efekt == "trh_prispevek":
        hrac.gold -= 20
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 3)
        _zmen_frakci(hra, "obchodnici", 1)
    elif efekt == "trh_stanek":
        hrac.gold += 25
        hrac.reputace_mesta = max(-100, hrac.reputace_mesta - 1)
    elif efekt == "mapa_koupit":
        hrac.gold -= 15
        hra.vyzkum.pridej_body(3)
    elif efekt == "mapa_predat":
        hrac.reputace_mesta = min(100, hrac.reputace_mesta + 1)
        _zmen_frakci(hra, "obchodnici", 2)
    elif efekt == "vuz_opravit":
        hrac.gold -= 10
        _zmen_frakci(hra, "obchodnici", 3)
    elif efekt == "vuz_vykoupit":
        hrac.gold -= 20
        hrac.gold += 45
        _zmen_frakci(hra, "obchodnici", -2)


def _zaznamenej_udalost(hra, linka_id, titulek, den):
    zaznam = {
        "den": den,
        "udalost": titulek,
        "typ": "pribehova",
        "udalost_id": linka_id,
    }
    hra.kalendar.udalosti.append(zaznam)
    hra.kalendar.udalosti = hra.kalendar.udalosti[-30:]


def _vyber_moznost(hra, moznosti):
    while True:
        for index, moznost in enumerate(moznosti, 1):
            cena = moznost.get("cena", 0)
            nedostupna = cena > hra.hrac.gold
            oznaceni = " — nedostatek zlata" if nedostupna else ""
            vytiskni_volbu(str(index), f"{moznost['text']}{oznaceni}")
        vytiskni_volbu("0", "Nechat událost bez zásahu")
        try:
            volba = input("> ").strip()
        except EOFError:
            return None
        if volba == "0":
            return None
        try:
            index = int(volba) - 1
        except ValueError:
            index = -1
        if not 0 <= index < len(moznosti):
            print("Zadej číslo dostupné možnosti.")
            continue
        moznost = moznosti[index]
        if moznost.get("cena", 0) > hra.hrac.gold:
            print("Na tuto možnost nemáš dost zlata.")
            continue
        return moznost


def _spust_pribehovou_udalost(hra, den):
    kalendar = hra.kalendar
    linka = kalendar.aktivni_pribehova_linka
    linka_id_ulozene = linka.get("id") if isinstance(linka, dict) else None
    if isinstance(linka_id_ulozene, str) and linka_id_ulozene in PRIBEHOVE_LINKY:
        linka_id = linka_id_ulozene
        try:
            etapa_index = int(linka.get("etapa", 1))
        except (TypeError, ValueError):
            etapa_index = -1
        if not 0 < etapa_index < len(PRIBEHOVE_LINKY[linka_id]["etapy"]):
            kalendar.aktivni_pribehova_linka = {}
            return _spust_pribehovou_udalost(hra, den)
        vetv = linka.get("vetv", "")
        if not isinstance(vetv, str):
            vetv = ""
        definice = PRIBEHOVE_LINKY[linka_id]
        etapa = definice["etapy"][etapa_index]
        vysledek = etapa["vysledky"].get(vetv)
        if not vysledek:
            kalendar.aktivni_pribehova_linka = {}
            return _spust_pribehovou_udalost(hra, den)
        efekt, text_vysledku = vysledek
        print(f"\n{etapa['titulek']}\n{text_vysledku}")
        _aplikuj_efekt(hra, efekt)
        tisk_ok(text_vysledku)
        kalendar.aktivni_pribehova_linka = {}
        _zaznamenej_udalost(hra, linka_id, etapa["titulek"], den)
    else:
        if linka:
            kalendar.aktivni_pribehova_linka = {}
        nedavne = {
            zaznam.get("udalost_id")
            for zaznam in kalendar.udalosti[-3:]
            if isinstance(zaznam, dict) and zaznam.get("typ") == "pribehova"
        }
        dostupne = [
            (ident, data)
            for ident, data in PRIBEHOVE_LINKY.items()
            if ident not in nedavne
        ]
        if not dostupne:
            dostupne = list(PRIBEHOVE_LINKY.items())
        linka_id, definice = random.choices(
            dostupne,
            weights=[max(1, definice["vaha"](hra)) for _, definice in dostupne],
            k=1,
        )[0]
        etapa = definice["etapy"][0]
        print(f"\n{etapa['titulek']}\n{etapa['text']}")
        moznost = _vyber_moznost(hra, etapa["moznosti"])
        if moznost is None:
            tisk_info("Do události ses nevložil; rozhodnutí zůstává na tobě příště.")
            _zaznamenej_udalost(hra, linka_id, etapa["titulek"], den)
            zaznamenej(
                hra, f"Příběhová událost: {etapa['titulek']} (bez zásahu)"
            )
            return True
        _aplikuj_efekt(hra, moznost["efekt"])
        tisk_ok(f"Zvolená možnost: {moznost['text']}.")
        kalendar.aktivni_pribehova_linka = {
            "id": linka_id,
            "etapa": 1,
            "vetv": moznost["vetv"],
        }
        _zaznamenej_udalost(hra, linka_id, etapa["titulek"], den)

    zaznamenej(hra, f"Příběhová událost: {etapa['titulek']}")
    return True


def _spust_samostatnou_udalost(hra, den):
    nedavne = {
        zaznam.get("udalost_id")
        for zaznam in hra.kalendar.udalosti[-3:]
        if isinstance(zaznam, dict) and zaznam.get("typ") == "denni_drobnost"
    }
    dostupne = [
        udalost for udalost in SAMOSTATNE_UDALOSTI
        if udalost["id"] not in nedavne
    ]
    if not dostupne:
        dostupne = list(SAMOSTATNE_UDALOSTI)
    udalost = random.choice(dostupne)
    print(f"\n{udalost['titulek']}\n{udalost['text']}")
    moznost = _vyber_moznost(hra, udalost["moznosti"])
    zaznam = {
        "den": den,
        "udalost": udalost["titulek"],
        "typ": "denni_drobnost",
        "udalost_id": udalost["id"],
    }
    hra.kalendar.udalosti.append(zaznam)
    hra.kalendar.udalosti = hra.kalendar.udalosti[-30:]
    if moznost is None:
        tisk_info("Nechal jsi událost proběhnout bez zásahu.")
        zaznamenej(hra, f"Událost dne: {udalost['titulek']} (bez zásahu)")
        return
    _aplikuj_efekt(hra, moznost["efekt"])
    tisk_ok(f"Zvolená možnost: {moznost['text']}.")
    zaznamenej(hra, f"Událost dne: {udalost['titulek']}")


def spust_denni_udalost(hra):
    """Nabídne příběhovou událost a drobnou událost nejvýše jednou za den."""
    kalendar = hra.kalendar
    den = max(1, int(hra.hrac.den))
    if kalendar.den_posledni_pribehove_udalosti >= den:
        return False

    _spust_pribehovou_udalost(hra, den)
    _spust_samostatnou_udalost(hra, den)
    kalendar.den_posledni_pribehove_udalosti = den
    return True

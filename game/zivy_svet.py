"""Denní simulace frakcí, NPC a rozhodovacích situací."""

import random
from copy import deepcopy
from dataclasses import dataclass, field

from data.mesta import DOPADY_AI_NPC, FRAKCNI_ZONY, MESTA, PROFILY_AI_NPC
from game.svet import LOKACE
from models.mesto import StavMesta
from utils.decision_ai import vyber_nejlepsi_uzitek, vzdalenosti_od_cilu
from utils.vypis import tisk_chyba, tisk_info, tisk_ok, vytiskni_volbu


FRAKCNI_CILE = {
    "policie": ("Udržet pořádek ve čtvrtích", "Stráž posiluje hlídky a hledá podporu obyvatel."),
    "podsveti": ("Rozšířit vliv v podzemí", "Gangy budují nové kontakty a soupeří o kontrolu uliček."),
    "cirkev": ("Odhalit zakázané aktivity", "Inkvizice sbírá svědectví a hledá stopy po dominiu."),
    "obchodnici": ("Zajistit bezpečné obchodní trasy", "Kupci připravují karavany a vyjednávají výhodnější průchod."),
    "kult_krve": ("Shromáždit suroviny pro rituál", "Kult pátrá po vzácných přísadách a příznivcích."),
    "syndikat_stinu": ("Získat převahu v informační síti", "Špehové vyměňují zprávy a mapují slabá místa rivalů."),
    "cech_kurtizan": ("Získat nové mecenáše", "Cech pořádá společenská setkání a rozšiřuje své kontakty."),
    "narkomani": ("Omezit pouliční krize", "Dobrovolníci hledají bezpečnější pomoc pro lidi v nouzi."),
    "cyberpunkaci": ("Ovládnout městskou datovou síť", "Technici opravují uzly a obchodují s ověřenými informacemi."),
    "nymfomanky": ("Uspořádat dobrovolný slavnostní večer", "Organizátorky připravují společenskou akci s jasnými pravidly účasti."),
}

FRAKCNI_AKCE = {
    "policie": (
        "posílila hlídky",
        "bezpeci",
        {"bezpeci": 1, "stabilita": 1},
    ),
    "podsveti": (
        "rozšířilo noční obchod",
        "prosperita",
        {"prosperita": 1, "bezpeci": -1},
    ),
    "cirkev": (
        "zprostředkovala veřejné smírčí jednání",
        "stabilita",
        {"stabilita": 1, "bezpeci": 1},
    ),
    "obchodnici": (
        "otevřeli novou obchodní trasu",
        "prosperita",
        {"prosperita": 1, "bezpeci": 1},
    ),
    "kult_krve": (
        "vyvolal neklid kolem tajného rituálu",
        "stabilita",
        {"stabilita": -1, "bezpeci": -1},
    ),
    "syndikat_stinu": (
        "rozšířil síť ověřených zpráv",
        "stabilita",
        {"stabilita": 1},
    ),
    "cech_kurtizan": (
        "uspořádal dobrovolný společenský večer",
        "prosperita",
        {"prosperita": 1, "stabilita": 1},
    ),
    "narkomani": (
        "zajistili bezpečnější pouliční pomoc",
        "bezpeci",
        {"bezpeci": 1, "stabilita": 1},
    ),
    "cyberpunkaci": (
        "opravili městské komunikační uzly",
        "stabilita",
        {"stabilita": 1, "prosperita": 1},
    ),
    "nymfomanky": (
        "uspořádaly slavnost s jasnými pravidly účasti",
        "prosperita",
        {"prosperita": 1, "stabilita": 1},
    ),
}

VYCHOZI_POSTAVY = (
    {
        "id": "mira_lecitelka", "jmeno": "Mira", "role": "Potulná léčitelka",
        "frakce": "policie", "lokace": "hostinec", "duvera": 0,
        "akce": (
            "Objíždí čtvrti a nabízí první pomoc.",
            "Připravuje zásoby pro městskou ošetřovnu.",
            "Vyslechla obyvatele a předala zprávu stráži.",
        ),
    },
    {
        "id": "radan_paserak", "jmeno": "Radan", "role": "Pašerák",
        "frakce": "podsveti", "lokace": "pristav", "duvera": 0,
        "akce": (
            "Vyjednává o průchodu zboží městem.",
            "Hledá bezpečnější cestu pro noční zásilku.",
            "Vyměnil zprávy s přístavními kontakty.",
        ),
    },
    {
        "id": "elian_informator", "jmeno": "Elian", "role": "Informátor",
        "frakce": "syndikat_stinu", "lokace": "trh", "duvera": 0,
        "akce": (
            "Ověřuje zprávy mezi městskými čtvrtěmi.",
            "Předává radě ověřené informace z tržiště.",
            "Sleduje, kdo se vyptává na městské plány.",
        ),
    },
    {
        "id": "selene_vedma", "jmeno": "Selene", "role": "Vědma",
        "frakce": "kult_krve", "lokace": "akademie", "duvera": 0,
        "akce": (
            "Studuje změny v magických proudech.",
            "Sbírá svědectví o zvláštních světlech nad městem.",
            "Vyměnila s akademiky poznámky o starých runách.",
        ),
    },
    {
        "id": "talia_kupkyne", "jmeno": "Talia", "role": "Kupecká vyjednavačka",
        "frakce": "obchodnici", "lokace": "cechovni_ulicky", "duvera": 0,
        "akce": (
            "Sjednává bezpečný průjezd pro karavanu.",
            "Kontroluje ceny a dostupnost zásob.",
            "Vyjednala s cechem nový obchodní termín.",
        ),
    },
    {
        "id": "vespera_kuryrka", "jmeno": "Vespera", "role": "Kurýrka",
        "frakce": "cirkev", "lokace": "chram_cistoty", "duvera": 0,
        "akce": (
            "Předává zprávy mezi chrámem a městskou radou.",
            "Vyslýchá svědky a ověřuje jejich výpovědi.",
            "Dohlíží na hlídky u městských bran.",
        ),
    },
    {
        "id": "nela_umelkyne", "jmeno": "Nela", "role": "Městská umělkyně",
        "frakce": "cech_kurtizan", "lokace": "cervena_ctvrt", "duvera": 0,
        "akce": (
            "Připravuje večerní vystoupení pro dobrovolné hosty.",
            "Domlouvá se s mecenáši na podmínkách večerní akce.",
            "Rozšiřuje síť bezpečných a dobrovolných společenských setkání.",
        ),
    },
    {
        "id": "mira_vychodni", "jmeno": "Mira z Brodu",
        "role": "Léčitelka říčních osad", "frakce": "policie",
        "lokace": "vychodni_zahrady", "duvera": 0,
        "akce": (
            "Zřídila ošetřovnu pro karavanové dělníky.",
            "Pomohla obyvatelům opravit zavlažovací kanál.",
        ),
    },
    {
        "id": "rovan_kapitan", "jmeno": "Kapitán Rovan",
        "role": "Velitel pohraniční hlídky", "frakce": "policie",
        "lokace": "vychodni_kasarna", "duvera": 0,
        "akce": (
            "Zkontroloval hlídky u východního mostu.",
            "Doprovodil karavanu přes nebezpečný úsek cesty.",
        ),
    },
    {
        "id": "vesna_radni", "jmeno": "Vesna z městské rady",
        "role": "Vyjednavačka Východního Brodu", "frakce": "obchodnici",
        "lokace": "rada_vychodniho_brodu", "duvera": 0,
        "akce": (
            "Zprostředkovala jednání mezi radou a cechy.",
            "Vyjednala zásoby pro čtvrti za řekou.",
        ),
    },
)

MOZNOSTI_ZASAHU = (
    {"text": "Podpořit cíl a získat přízeň frakce (25 zlata)", "cena": 25, "frakce": 8, "mesto": 1},
    {"text": "Vyjednat kompromis (10 zlata)", "cena": 10, "frakce": 3, "mesto": 2},
    {"text": "Postavit se plánu a oslabit vliv frakce", "cena": 0, "frakce": -6, "mesto": -1},
)

UDALOSTI_MESTA = {
    "karavana": {
        "frakce": "obchodnici",
        "nazev": "Karavana žádá o bezpečný průjezd",
        "text": "Kupecká karavana čeká na zajištění trasy a zásob.",
        "volby": (
            ("Zajistit průjezd (25 zl.)", 25, {"prosperita": 5, "stabilita": 1}, 5),
            ("Vyjednat pomoc místních (bez nákladů)", 0, {"prosperita": 2, "stabilita": 1}, 2),
        ),
        "zanik": {"prosperita": -2, "bezpeci": -1},
    },
    "most": {
        "frakce": "obchodnici",
        "nazev": "Městský most potřebuje opravu",
        "text": "Poškozený most brzdí dopravu mezi čtvrtěmi a okolními osadami.",
        "volby": (
            ("Zaplatit opravu (30 zl.)", 30, {"prosperita": 2, "bezpeci": 5}, 4),
            ("Povolat dobrovolníky (10 zl.)", 10, {"bezpeci": 2, "stabilita": 1}, 2),
        ),
        "zanik": {"prosperita": -2, "bezpeci": -2},
    },
    "hlidky": {
        "frakce": "policie",
        "nazev": "Obyvatelé žádají posílit hlídky",
        "text": "Obchodníci a rodiny hlásí neklid na cestách a v okrajových čtvrtích.",
        "volby": (
            ("Zaplatit posílené hlídky (20 zl.)", 20, {"bezpeci": 5, "stabilita": 2}, 5),
            ("Požádat místní o spolupráci", 0, {"bezpeci": 2, "stabilita": 1}, 2),
        ),
        "zanik": {"bezpeci": -3, "stabilita": -1},
    },
}

MISTA_UDALOSTI = {
    "karavana": {"stare_mesto": "trh", "vychodni_brod": "vychodni_trziste"},
    "most": {"stare_mesto": "pristav", "vychodni_brod": "vychodni_pristav"},
    "hlidky": {"stare_mesto": "hranice", "vychodni_brod": "vychodni_kasarna"},
}


@dataclass
class ZivySvetSystem:
    posledni_den: int = 0
    frakcni_cile: dict = field(default_factory=dict)
    postavy: list = field(default_factory=lambda: deepcopy(VYCHOZI_POSTAVY))
    nabidky: list = field(default_factory=list)
    historie: list = field(default_factory=list)
    mesta: dict = field(default_factory=dict)
    kontrola_lokaci: dict = field(default_factory=dict)
    udalosti_mesta: list = field(default_factory=list)
    dalsi_frakce: int = 0
    dalsi_postava: int = 0

    def __post_init__(self):
        for frakce_id, (nazev, popis) in FRAKCNI_CILE.items():
            cil = self.frakcni_cile.get(frakce_id)
            if not isinstance(cil, dict):
                cil = {}
                self.frakcni_cile[frakce_id] = cil
            cil.setdefault("nazev", nazev)
            cil.setdefault("popis", popis)
            cil["cil"] = max(1, min(10, _kladne_cislo(cil.get("cil", 3))))
            cil["postup"] = min(cil["cil"], _kladne_cislo(cil.get("postup", 0)))
            mesto_id = cil.get("mesto_id")
            if mesto_id not in MESTA:
                mesto_id = _prvni_mesto_frakce(frakce_id)
            cil["mesto_id"] = mesto_id
            cil["posledni_akce"] = (
                cil.get("posledni_akce")
                if isinstance(cil.get("posledni_akce"), str)
                else ""
            )
        self.postavy = [p for p in self.postavy if isinstance(p, dict)]
        for index, postava in enumerate(self.postavy):
            postava.setdefault("id", f"npc_{index}")
            postava.setdefault("jmeno", "Neznámá postava")
            postava.setdefault("role", "Obyvatel města")
            postava.setdefault("frakce", "")
            postava.setdefault("lokace", "trh")
            postava.setdefault("duvera", 0)
            if not isinstance(postava.get("akce"), (str, tuple, list)):
                postava["akce"] = ("Prochází městem a vyřizuje své záležitosti.",)
        for definice in VYCHOZI_POSTAVY:
            if not any(p.get("id") == definice["id"] for p in self.postavy):
                self.postavy.append(deepcopy(definice))
            else:
                postava = next(p for p in self.postavy if p.get("id") == definice["id"])
                for klic, hodnota in definice.items():
                    postava.setdefault(klic, hodnota)
        ulozena_mesta = self.mesta if isinstance(self.mesta, dict) else {}
        self.mesta = {
            mesto_id: StavMesta.from_dict(
                ulozena_mesta.get(mesto_id),
                {
                    "ident": mesto_id,
                    "nazev": definice["nazev"],
                    "prosperita": definice["prosperita"],
                    "bezpeci": definice["bezpeci"],
                    "stabilita": definice["stabilita"],
                },
            )
            for mesto_id, definice in MESTA.items()
        }
        ulozena_kontrola = (
            self.kontrola_lokaci if isinstance(self.kontrola_lokaci, dict) else {}
        )
        self.kontrola_lokaci = {}
        for lokace_id in LOKACE:
            vliv = ulozena_kontrola.get(lokace_id)
            if not isinstance(vliv, dict):
                vlastnik = _vychozi_frakce_lokace(lokace_id)
                vliv = {vlastnik: 55}
                rival = next(
                    (frakce for frakce in FRAKCNI_CILE if frakce != vlastnik),
                    vlastnik,
                )
                vliv[rival] = 30
            ocisteny = {
                frakce_id: max(0, min(100, _kladne_cislo(hodnota)))
                for frakce_id, hodnota in vliv.items()
                if frakce_id in FRAKCNI_CILE
            }
            if not ocisteny:
                ocisteny[_vychozi_frakce_lokace(lokace_id)] = 55
            self.kontrola_lokaci[lokace_id] = ocisteny
        udalosti = []
        if isinstance(self.udalosti_mesta, list):
            for udalost in self.udalosti_mesta:
                if (
                    not isinstance(udalost, dict)
                    or udalost.get("mesto_id") not in MESTA
                    or udalost.get("typ") not in UDALOSTI_MESTA
                    or not isinstance(udalost.get("den"), int)
                ):
                    continue
                udalost = deepcopy(udalost)
                udalost["den"] = max(0, udalost["den"])
                udalost["nazev"] = UDALOSTI_MESTA[udalost["typ"]]["nazev"]
                udalost["text"] = UDALOSTI_MESTA[udalost["typ"]]["text"]
                udalost["lokace_id"] = MISTA_UDALOSTI[udalost["typ"]][udalost["mesto_id"]]
                udalosti.append(udalost)
        self.udalosti_mesta = udalosti[-3:]
        self.nabidky = [
            nabidka for nabidka in self.nabidky
            if isinstance(nabidka, dict)
            and all(
                isinstance(nabidka.get(klic), str)
                for klic in ("frakce_id", "frakce_nazev", "cilek", "text", "postava")
            )
        ]
        self.historie = [
            zaznam for zaznam in self.historie
            if isinstance(zaznam, dict)
            and "den" in zaznam
            and isinstance(zaznam.get("text"), str)
        ][-30:]
        self.dalsi_frakce %= len(FRAKCNI_CILE)
        self.dalsi_postava %= max(1, len(self.postavy))

    def to_dict(self):
        return {
            "posledni_den": self.posledni_den,
            "frakcni_cile": deepcopy(self.frakcni_cile),
            "postavy": deepcopy(self.postavy),
            "nabidky": deepcopy(self.nabidky),
            "historie": deepcopy(self.historie[-30:]),
            "mesta": {
                mesto_id: mesto.to_dict()
                for mesto_id, mesto in self.mesta.items()
            },
            "kontrola_lokaci": deepcopy(self.kontrola_lokaci),
            "udalosti_mesta": deepcopy(self.udalosti_mesta),
            "dalsi_frakce": self.dalsi_frakce,
            "dalsi_postava": self.dalsi_postava,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("Data živého světa musí být objekt.")
        cile = data.get("frakcni_cile", {})
        postavy = data.get("postavy", [])
        nabidky = data.get("nabidky", [])
        historie = data.get("historie", [])
        mesta = data.get("mesta", {})
        kontrola_lokaci = data.get("kontrola_lokaci", {})
        udalosti_mesta = data.get("udalosti_mesta", [])
        if not isinstance(cile, dict) or not isinstance(postavy, list):
            raise ValueError("Uložený živý svět má neplatný formát.")
        if (
            not isinstance(nabidky, list)
            or not isinstance(historie, list)
            or not isinstance(mesta, dict)
            or not isinstance(kontrola_lokaci, dict)
            or not isinstance(udalosti_mesta, list)
        ):
            raise ValueError("Uložené události živého světa mají neplatný formát.")
        return cls(
            posledni_den=_kladne_cislo(data.get("posledni_den", 0)),
            frakcni_cile=deepcopy(cile),
            postavy=deepcopy(postavy),
            nabidky=deepcopy(nabidky),
            historie=deepcopy(historie[-30:]),
            mesta=deepcopy(mesta),
            kontrola_lokaci=deepcopy(kontrola_lokaci),
            udalosti_mesta=deepcopy(udalosti_mesta[-3:]),
            dalsi_frakce=_kladne_cislo(data.get("dalsi_frakce", 0)),
            dalsi_postava=_kladne_cislo(data.get("dalsi_postava", 0)),
        )

    def posun_den(self, hra):
        """Simuluje jeden den; opakované volání ve stejný den stav nemění."""
        den = max(1, int(hra.hrac.den))
        if self.posledni_den >= den:
            return []
        self.posledni_den = den
        zpravy = []
        for mesto in self.mesta.values():
            mesto.posun_den()
        self._vyres_expirovane_udalosti(den, zpravy)

        frakce_ids = tuple(FRAKCNI_CILE)
        vedlejsi_frakce = random.choice(
            tuple(
                frakce_id for frakce_id in frakce_ids
                if frakce_id != frakce_ids[self.dalsi_frakce % len(frakce_ids)]
            )
        )
        dnesni_frakce = (
            frakce_ids[self.dalsi_frakce % len(frakce_ids)],
            vedlejsi_frakce,
        )
        for frakce_id in dnesni_frakce:
            zprava_cile = self._vykonej_cil_fakce(frakce_id)
            if zprava_cile:
                zpravy.append(zprava_cile)
            zmena_kontroly = self._rozsir_vliv_fakce(frakce_id, den)
            if zmena_kontroly:
                zpravy.append(zmena_kontroly)
            cil = self.frakcni_cile[frakce_id]
            postup_pred = cil["postup"]
            cil["postup"] = min(cil["cil"], int(cil.get("postup", 0)) + 1)
            if cil["postup"] >= cil["cil"]:
                if len(self.nabidky) < 10:
                    cil["postup"] = 0
                    nabidka = self._vytvor_nabidku(frakce_id, den)
                    self.nabidky.append(nabidka)
                    zpravy.append(
                        f"{nabidka['frakce_nazev']} pokročila ve svém cíli: "
                        f"{nabidka['cilek']}. Na rozhodnutí čeká nová situace."
                    )
                elif postup_pred < cil["cil"]:
                    zpravy.append(
                        f"{FRAKCNI_CILE[frakce_id][0]} dokončila cíl, ale "
                        "čeká na uvolnění fronty rozhodnutí."
                    )
        self.dalsi_frakce = (self.dalsi_frakce + 1) % len(frakce_ids)

        if den % 4 == 0 and len(self.udalosti_mesta) < 3:
            udalost = self._vytvor_udalost_mesta(den)
            self.udalosti_mesta.append(udalost)
            zpravy.append(
                f"{self.mesta[udalost['mesto_id']].nazev}: "
                f"{udalost['nazev'].lower()}. Ve městě čeká rozhodnutí."
            )
        if den % 5 == 0:
            prijem = self._prijem_karavan()
            if prijem:
                hra.hrac.gold += prijem
                zpravy.append(
                    f"Obchodní trasy přinesly {prijem} zl. "
                    "podle bezpečí a prosperity měst."
                )

        postava = self.postavy[self.dalsi_postava % len(self.postavy)]
        self.dalsi_postava = (self.dalsi_postava + 1) % len(self.postavy)
        nova_lokace = self._rozhodni_pohyb_npc(postava)
        if not nova_lokace:
            nova_lokace = postava.get("lokace", "trh")
        postava["lokace"] = nova_lokace
        if hasattr(hra, "svet"):
            hra.svet.odhal_lokaci(nova_lokace)
        mesto_id = _mesto_lokace(nova_lokace)
        dopad = DOPADY_AI_NPC.get(postava.get("id"))
        if dopad and mesto_id in self.mesta:
            self.mesta[mesto_id].uprav_akci(*dopad)
        akce = postava["akce"]
        if isinstance(akce, (tuple, list)):
            akce = random.choice(akce)
        postava["posledni_akce"] = akce
        zpravy.append(
            f"{postava['jmeno']} ({postava['role']}) se přesunula do lokace "
            f"{nova_lokace.replace('_', ' ')}. {akce}"
        )
        self.historie.extend({"den": den, "text": zprava} for zprava in zpravy)
        self.historie = self.historie[-30:]
        return zpravy

    def _vykonej_cil_fakce(self, frakce_id):
        """Nechá frakci vykonat malý, průběžný krok jejího městského cíle."""
        akce = FRAKCNI_AKCE.get(frakce_id)
        if not akce:
            return ""
        popis, metrika, dopady = akce
        mesta_vlivu = {
            _mesto_lokace(lokace_id)
            for lokace_id in FRAKCNI_ZONY.get(frakce_id, ())
            if lokace_id in LOKACE
        }
        kandidati = [
            mesto_id for mesto_id in MESTA
            if not mesta_vlivu or mesto_id in mesta_vlivu
        ]
        mesto_id = vyber_nejlepsi_uzitek(
            (klic, 100 - getattr(self.mesta[klic], metrika))
            for klic in kandidati
        )
        if not mesto_id:
            return ""
        mesto = self.mesta[mesto_id]
        mesto.uprav(**dopady)
        cil = self.frakcni_cile[frakce_id]
        cil["mesto_id"] = mesto_id
        cil["posledni_akce"] = popis
        return f"{mesto.nazev}: {FRAKCNI_CILE[frakce_id][0]} {popis}."

    def _rozsir_vliv_fakce(self, frakce_id, den):
        lokace = tuple(
            lokace_id for lokace_id in FRAKCNI_ZONY.get(frakce_id, ())
            if lokace_id in self.kontrola_lokaci
        )
        if not lokace:
            return ""
        index_fakce = tuple(FRAKCNI_CILE).index(frakce_id)
        lokace_id = lokace[(den + index_fakce) % len(lokace)]
        vliv = self.kontrola_lokaci[lokace_id]
        puvodni = self.frakce_lokace(lokace_id)
        vliv[frakce_id] = min(100, vliv.get(frakce_id, 0) + 2)
        if puvodni != frakce_id:
            vliv[puvodni] = max(0, vliv.get(puvodni, 0) - 1)
        novy = self.frakce_lokace(lokace_id)
        if novy != puvodni:
            return (
                f"{FRAKCNI_CILE[novy][0]} získala převahu v lokaci "
                f"{lokace_id.replace('_', ' ')}."
            )
        return ""

    def frakce_lokace(self, lokace_id):
        """Vrátí frakci s nejvyšším uloženým vlivem v lokaci."""
        vliv = self.kontrola_lokaci.get(lokace_id, {})
        return max(
            vliv,
            key=lambda frakce: (vliv[frakce], -tuple(FRAKCNI_CILE).index(frakce)),
            default=_vychozi_frakce_lokace(lokace_id),
        )

    def _uprav_vliv_lokace(self, lokace_id, frakce_id, zmena):
        if lokace_id not in self.kontrola_lokaci or frakce_id not in FRAKCNI_CILE:
            return
        vliv = self.kontrola_lokaci[lokace_id]
        vliv[frakce_id] = max(0, min(100, vliv.get(frakce_id, 0) + zmena))

    def _vytvor_udalost_mesta(self, den):
        typy = tuple(UDALOSTI_MESTA)
        mesta = tuple(MESTA)
        typ = typy[(den // 4 - 1) % len(typy)]
        mesto_id = mesta[(den // 4 - 1) % len(mesta)]
        definice = UDALOSTI_MESTA[typ]
        return {
            "id": f"{mesto_id}-{typ}-{den}",
            "den": den,
            "mesto_id": mesto_id,
            "typ": typ,
            "nazev": definice["nazev"],
            "text": definice["text"],
            "lokace_id": MISTA_UDALOSTI[typ][mesto_id],
        }

    def _vyres_expirovane_udalosti(self, den, zpravy):
        cekajici = []
        for udalost in self.udalosti_mesta:
            if den - udalost["den"] < 4:
                cekajici.append(udalost)
                continue
            mesto = self.mesta[udalost["mesto_id"]]
            mesto.uprav(**UDALOSTI_MESTA[udalost["typ"]]["zanik"])
            zpravy.append(
                f"Neřešená situace «{udalost['nazev']}» ve městě "
                f"{mesto.nazev} skončila zhoršením místních poměrů."
            )
            self.historie.append({
                "den": den,
                "text": f"{mesto.nazev}: nevyřešeno — {udalost['nazev']}.",
            })
        self.udalosti_mesta = cekajici[-3:]

    def _prijem_karavan(self):
        prijem = 0
        for mesto in self.mesta.values():
            if mesto.bezpeci < 20 or mesto.stabilita < 20:
                continue
            prijem += min(
                8,
                (mesto.prosperita + mesto.bezpeci + mesto.stabilita) // 60,
            )
        return prijem

    def _vyres_udalost_mesta(self, hra, udalost):
        definice = UDALOSTI_MESTA[udalost["typ"]]
        mesto = self.mesta[udalost["mesto_id"]]
        print(f"\n{mesto.nazev}: {udalost['nazev']}\n{udalost['text']}")
        for index, (text, cena, _, _) in enumerate(definice["volby"], 1):
            oznaceni = " — nedostatek zlata" if hra.hrac.gold < cena else ""
            vytiskni_volbu(str(index), text + oznaceni)
        vytiskni_volbu("0", "Nechat situaci bez zásahu")
        try:
            volba = input("> ").strip()
        except EOFError:
            return False
        if volba == "0":
            mesto.uprav(**definice["zanik"])
            tisk_info("Situaci ponecháváš bez zásahu; městské poměry se zhorší.")
            self._zapis_udalost(udalost, "bez zásahu")
            return True
        try:
            index = int(volba) - 1
            text, cena, dopady, vliv = definice["volby"][index]
        except (ValueError, IndexError):
            tisk_chyba("Zadej číslo dostupné možnosti.")
            return False
        if hra.hrac.gold < cena:
            tisk_chyba("Na tuto možnost nemáš dost zlata.")
            return False
        hra.hrac.gold -= cena
        mesto.uprav(**dopady)
        frakce_id = definice["frakce"]
        frakce = hra.frakce.frakce.get(frakce_id)
        if frakce:
            frakce.zmenit(vliv)
        self._uprav_vliv_lokace(
            udalost["lokace_id"], frakce_id, vliv
        )
        tisk_ok(f"Rozhodl ses: {text}.")
        self._zapis_udalost(udalost, text)
        return True

    def _zapis_udalost(self, udalost, rozhodnuti):
        mesto = self.mesta[udalost["mesto_id"]]
        self.historie.append({
            "den": udalost["den"],
            "text": f"{mesto.nazev}: {rozhodnuti} — {udalost['nazev']}.",
        })
        self.historie = self.historie[-30:]

    def _rozhodni_pohyb_npc(self, postava):
        """NPC volí trasu k městu, kde jeho specializace nejvíc pomůže."""
        aktualni = postava.get("lokace", "trh")
        if aktualni not in LOKACE:
            aktualni = "trh"
        profil = PROFILY_AI_NPC.get(postava.get("id"))
        sousedi = LOKACE[aktualni]["sousedni"]
        if not sousedi:
            return aktualni
        if not profil:
            return sousedi[0]

        metrika = profil["metrika"]
        smer = profil["smer"]
        mesto_cil = vyber_nejlepsi_uzitek(
            (
                mesto_id,
                (
                    100 - getattr(mesto, metrika)
                    if smer == "minimum"
                    else getattr(mesto, metrika)
                ),
            )
            for mesto_id, mesto in self.mesta.items()
        )
        lokace_cile = MESTA[mesto_cil]["lokace"]
        vzdalenosti = vzdalenosti_od_cilu(
            {lokace_id: data["sousedni"] for lokace_id, data in LOKACE.items()},
            lokace_cile,
        )
        kandidati = [lokace for lokace in sousedi if lokace in vzdalenosti]
        if aktualni in lokace_cile:
            kandidati = [
                lokace for lokace in kandidati
                if lokace in lokace_cile
            ] or kandidati
        vybrany = vyber_nejlepsi_uzitek(
            (lokace, -vzdalenosti[lokace]) for lokace in kandidati
        )
        return vybrany or aktualni

    def _vytvor_nabidku(self, frakce_id, den):
        definice = self.frakcni_cile[frakce_id]
        frakce_nazev = FRAKCNI_CILE[frakce_id][0]
        postava = next(
            (p for p in self.postavy if p.get("frakce") == frakce_id),
            self.postavy[den % len(self.postavy)],
        )
        return {
            "id": f"{frakce_id}-{den}",
            "den": den,
            "frakce_id": frakce_id,
            "frakce_nazev": frakce_nazev,
            "cilek": definice["nazev"],
            "text": definice["popis"],
            "postava": postava["jmeno"],
            "mesto_id": _mesto_lokace(postava.get("lokace", "trh")),
            "lokace_id": postava.get("lokace", "trh"),
        }

    def menu(self, hra):
        while True:
            print("\n=== ŽIVÝ SVĚT ===")
            print("Denní cíle frakcí:")
            for frakce_id, cil in self.frakcni_cile.items():
                frakce = hra.frakce.frakce.get(frakce_id)
                jmeno = frakce.nazev if frakce else frakce_id
                mesto = self.mesta[cil["mesto_id"]].nazev
                akce = f" — {cil['posledni_akce']}" if cil["posledni_akce"] else ""
                print(
                    f"  {jmeno}: {cil['nazev']} [{cil['postup']}/{cil['cil']}] "
                    f"→ {mesto}{akce}"
                )
            print("\nPostavy ve městě:")
            for postava in self.postavy:
                print(
                    f"  {postava['jmeno']} — {postava['role']}, "
                    f"{postava['lokace'].replace('_', ' ')}"
                )
            print("\nStav měst:")
            for mesto_id, mesto in self.mesta.items():
                print(
                    f"  {mesto.nazev}: prosperita {mesto.prosperita}, "
                    f"bezpečí {mesto.bezpeci}, stabilita {mesto.stabilita}"
                )
            if self.nabidky:
                nabidka = self.nabidky[0]
                print(
                    f"\nSituace: {nabidka['frakce_nazev']} — {nabidka['cilek']}\n"
                    f"{nabidka['text']} {nabidka['postava']} přináší zprávu."
                )
                if not self._vyres_nabidku(hra, nabidka):
                    return
                self.nabidky.pop(0)
                if self.nabidky:
                    try:
                        dalsi = input("Vyřešit také další situaci? (a/n): ").strip().lower()
                    except EOFError:
                        return
                    if dalsi not in ("a", "ano"):
                        return
                continue
            if self.udalosti_mesta:
                udalost = self.udalosti_mesta[0]
                if not self._vyres_udalost_mesta(hra, udalost):
                    return
                self.udalosti_mesta.pop(0)
                continue
            if self.historie:
                print("\nPoslední dění:")
                for zaznam in self.historie[-5:]:
                    print(f"  Den {zaznam['den']}: {zaznam['text']}")
            vytiskni_volbu("0", "Zpět")
            try:
                if input("> ").strip() == "0":
                    return
            except EOFError:
                return

    def _vyres_nabidku(self, hra, nabidka):
        while True:
            for index, moznost in enumerate(MOZNOSTI_ZASAHU, 1):
                oznaceni = (
                    " — nedostatek zlata"
                    if hra.hrac.gold < moznost["cena"] else ""
                )
                vytiskni_volbu(str(index), moznost["text"] + oznaceni)
            vytiskni_volbu("0", "Nechat situaci bez zásahu")
            try:
                volba = input("> ").strip()
            except EOFError:
                return False
            if volba == "0":
                tisk_info("Situaci ponecháváš jejímu vývoji.")
                self._zapis(hra, nabidka, "bez zásahu")
                return True
            try:
                index = int(volba) - 1
            except ValueError:
                index = -1
            if not 0 <= index < len(MOZNOSTI_ZASAHU):
                tisk_chyba("Zadej číslo dostupné možnosti.")
                continue
            moznost = MOZNOSTI_ZASAHU[index]
            if hra.hrac.gold < moznost["cena"]:
                tisk_chyba("Na tuto možnost nemáš dost zlata.")
                continue
            hra.hrac.gold -= moznost["cena"]
            frakce = hra.frakce.frakce.get(nabidka["frakce_id"])
            if frakce:
                frakce.zmenit(moznost["frakce"])
            mesto_id = nabidka.get("mesto_id", "stare_mesto")
            lokace_id = nabidka.get("lokace_id")
            if lokace_id not in self.kontrola_lokaci:
                lokace_id = MESTA.get(mesto_id, MESTA["stare_mesto"])["lokace"][0]
            self._uprav_vliv_lokace(
                lokace_id, nabidka["frakce_id"], moznost["frakce"]
            )
            hra.hrac.reputace_mesta = max(
                -100,
                min(100, hra.hrac.reputace_mesta + moznost["mesto"]),
            )
            mesto = self.mesta.get(nabidka.get("mesto_id", "stare_mesto"))
            if mesto:
                dopady = (
                    {"prosperita": 2, "stabilita": 1},
                    {"bezpeci": 1, "stabilita": 2},
                    {"bezpeci": -1, "stabilita": -2},
                )
                mesto.uprav(**dopady[index])
            tisk_ok(f"Rozhodl ses: {moznost['text']}.")
            self._zapis(hra, nabidka, moznost["text"])
            return True

    def _zapis(self, hra, nabidka, rozhodnuti):
        zaznam = {
            "den": max(1, int(hra.hrac.den)),
            "text": f"{nabidka['frakce_nazev']}: {rozhodnuti}.",
        }
        self.historie.append(zaznam)
        self.historie = self.historie[-30:]
        from game.kronika import zaznamenej
        zaznamenej(hra, f"Živý svět: {zaznam['text']}")


def _kladne_cislo(hodnota):
    if isinstance(hodnota, bool):
        return 0
    try:
        return max(0, int(hodnota))
    except (TypeError, ValueError):
        return 0


def _mesto_lokace(lokace_id):
    return LOKACE.get(lokace_id, {}).get("mesto", "stare_mesto")


def _vychozi_frakce_lokace(lokace_id):
    for frakce_id, lokace in FRAKCNI_ZONY.items():
        if lokace_id in lokace:
            return frakce_id
    return "policie"


def _prvni_mesto_frakce(frakce_id):
    for lokace_id in FRAKCNI_ZONY.get(frakce_id, ()):
        if lokace_id in LOKACE:
            return _mesto_lokace(lokace_id)
    return "stare_mesto"

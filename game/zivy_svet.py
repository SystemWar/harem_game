"""Denní simulace frakcí, NPC a rozhodovacích situací."""

import random
from copy import deepcopy
from dataclasses import dataclass, field

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

POHYB_NPC = {
    "pevnost": ("trh", "les"),
    "trh": ("pevnost", "pristav", "ctvrt_remeselniku", "hostinec"),
    "pristav": ("trh", "paserska_zatoka", "palac_bohatych"),
    "hostinec": ("trh", "pevnost", "ctvrt_remeselniku"),
    "akademie": ("trh", "observator", "ctvrt_remeselniku"),
    "cechovni_ulicky": ("trh", "ctvrt_remeselniku", "pulnocni_trh"),
    "chram_cistoty": ("trh", "akademicke_namesti", "vezeni_inkvizice"),
    "palac_bohatych": ("trh", "pristav", "cervena_ctvrt"),
    "cervena_ctvrt": ("trh", "palac_bohatych", "hostinec"),
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
)

MOZNOSTI_ZASAHU = (
    {"text": "Podpořit cíl a získat přízeň frakce (25 zlata)", "cena": 25, "frakce": 8, "mesto": 1},
    {"text": "Vyjednat kompromis (10 zlata)", "cena": 10, "frakce": 3, "mesto": 2},
    {"text": "Postavit se plánu a oslabit vliv frakce", "cena": 0, "frakce": -6, "mesto": -1},
)


@dataclass
class ZivySvetSystem:
    posledni_den: int = 0
    frakcni_cile: dict = field(default_factory=dict)
    postavy: list = field(default_factory=lambda: deepcopy(VYCHOZI_POSTAVY))
    nabidky: list = field(default_factory=list)
    historie: list = field(default_factory=list)
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
            cil["postup"] = min(2, _kladne_cislo(cil.get("postup", 0)))
            cil["cil"] = max(1, min(10, _kladne_cislo(cil.get("cil", 3))))
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
        if not isinstance(cile, dict) or not isinstance(postavy, list):
            raise ValueError("Uložený živý svět má neplatný formát.")
        if not isinstance(nabidky, list) or not isinstance(historie, list):
            raise ValueError("Uložené události živého světa mají neplatný formát.")
        return cls(
            posledni_den=_kladne_cislo(data.get("posledni_den", 0)),
            frakcni_cile=deepcopy(cile),
            postavy=deepcopy(postavy),
            nabidky=deepcopy(nabidky),
            historie=deepcopy(historie[-30:]),
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
            cil = self.frakcni_cile[frakce_id]
            cil["postup"] = min(cil["cil"], int(cil.get("postup", 0)) + 1)
            if cil["postup"] >= cil["cil"]:
                cil["postup"] = 0
                nabidka = self._vytvor_nabidku(frakce_id, den)
                self.nabidky.append(nabidka)
                zpravy.append(
                    f"{nabidka['frakce_nazev']} pokročila ve svém cíli: "
                    f"{nabidka['cilek']}. Na rozhodnutí čeká nová situace."
                )
        self.dalsi_frakce = (self.dalsi_frakce + 1) % len(frakce_ids)

        postava = self.postavy[self.dalsi_postava % len(self.postavy)]
        self.dalsi_postava = (self.dalsi_postava + 1) % len(self.postavy)
        moznosti = POHYB_NPC.get(postava.get("lokace"), ("trh", "pevnost"))
        nova_lokace = random.choice(moznosti)
        postava["lokace"] = nova_lokace
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
        }

    def menu(self, hra):
        while True:
            print("\n=== ŽIVÝ SVĚT ===")
            print("Denní cíle frakcí:")
            for frakce_id, cil in self.frakcni_cile.items():
                frakce = hra.frakce.frakce.get(frakce_id)
                jmeno = frakce.nazev if frakce else frakce_id
                print(f"  {jmeno}: {cil['nazev']} [{cil['postup']}/{cil['cil']}]")
            print("\nPostavy ve městě:")
            for postava in self.postavy:
                print(
                    f"  {postava['jmeno']} — {postava['role']}, "
                    f"{postava['lokace'].replace('_', ' ')}"
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
            hra.hrac.reputace_mesta = max(
                -100,
                min(100, hra.hrac.reputace_mesta + moznost["mesto"]),
            )
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

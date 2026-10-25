import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.menu_hlavni import normalizuj_volbu
from game.save_load import Hra, migrate_save
from game.zivy_svet import FRAKCNI_AKCE, ZivySvetSystem
from game.svet import LOKACE
from data.mesta import MESTA
from config import YELLOW
from models.frakce import FrakcniSystem
from utils.decision_ai import vzdalenosti_od_cilu, vyber_nejlepsi_uzitek


class ZivySvetTesty(unittest.TestCase):
    def test_vsechny_frakce_maji_cil_a_stav_se_uklada(self):
        svet = ZivySvetSystem()

        self.assertEqual(set(svet.frakcni_cile), set(FrakcniSystem().frakce))
        self.assertEqual(set(FRAKCNI_AKCE), set(svet.frakcni_cile))
        obnoveno = ZivySvetSystem.from_dict(svet.to_dict())
        self.assertEqual(obnoveno.frakcni_cile, svet.frakcni_cile)
        self.assertEqual(
            {postava["id"] for postava in obnoveno.postavy},
            {postava["id"] for postava in svet.postavy},
        )
        for frakce_id in svet.frakcni_cile:
            self.assertEqual(
                obnoveno.frakcni_cile[frakce_id]["mesto_id"],
                svet.frakcni_cile[frakce_id]["mesto_id"],
            )

    def test_denni_tah_pohybuje_npc_a_neopakuje_se(self):
        hra = Hra()
        hra.hrac.den = 2
        postava = hra.zivy_svet.postavy[0]
        postava_pred = postava["lokace"]
        vzdalenosti = vzdalenosti_od_cilu(
            {lokace: data["sousedni"] for lokace, data in LOKACE.items()},
            MESTA["vychodni_brod"]["lokace"],
        )

        zpravy = hra.zivy_svet.posun_den(hra)
        druhy_vysledek = hra.zivy_svet.posun_den(hra)

        self.assertTrue(zpravy)
        self.assertEqual(druhy_vysledek, [])
        self.assertNotEqual(hra.zivy_svet.postavy[0]["lokace"], postava_pred)
        self.assertLess(
            vzdalenosti[postava["lokace"]],
            vzdalenosti[postava_pred],
        )
        self.assertEqual(hra.zivy_svet.posledni_den, 2)

    def test_dokonceny_frakcni_cil_vytvori_nabidku_s_rozhodnutim(self):
        hra = Hra()
        hra.hrac.den = 1
        hra.zivy_svet.frakcni_cile["policie"]["cil"] = 1

        hra.zivy_svet.posun_den(hra)

        self.assertEqual(len(hra.zivy_svet.nabidky), 1)
        self.assertEqual(
            hra.zivy_svet.nabidky[0]["frakce_id"],
            "policie",
        )
        self.assertIn("postava", hra.zivy_svet.nabidky[0])

    def test_volba_nabidky_zmeni_zlato_frakci_a_reputaci(self):
        hra = Hra()
        nabidka = {
            "frakce_id": "policie",
            "frakce_nazev": "Policie",
            "cilek": "hlídky",
        }
        zlato_pred = hra.hrac.gold
        reputace_pred = hra.frakce.frakce["policie"].reputace
        mesto_pred = hra.hrac.reputace_mesta

        with patch("builtins.input", return_value="1"), redirect_stdout(io.StringIO()):
            self.assertTrue(hra.zivy_svet._vyres_nabidku(hra, nabidka))

        self.assertEqual(hra.hrac.gold, zlato_pred - 25)
        self.assertEqual(hra.frakce.frakce["policie"].reputace, reputace_pred + 8)
        self.assertEqual(hra.hrac.reputace_mesta, mesto_pred + 1)

    def test_rozhodnuti_frakcni_situace_meni_stav_prislusneho_mesta(self):
        hra = Hra()
        mesto = hra.zivy_svet.mesta["vychodni_brod"]
        bezpeci_pred = mesto.bezpeci
        stabilita_pred = mesto.stabilita
        nabidka = {
            "frakce_id": "policie",
            "frakce_nazev": "Policie",
            "cilek": "hlídky",
            "mesto_id": "vychodni_brod",
        }

        with patch("builtins.input", return_value="2"), redirect_stdout(io.StringIO()):
            self.assertTrue(hra.zivy_svet._vyres_nabidku(hra, nabidka))

        self.assertEqual(mesto.bezpeci, bezpeci_pred + 1)
        self.assertEqual(mesto.stabilita, stabilita_pred + 2)

    def test_menu_a_migrace_starych_savu(self):
        hra = Hra()
        data = hra.to_dict()
        data["save_version"] = 1

        migrovano = migrate_save(data)

        self.assertEqual(migrovano["save_version"], 2)
        self.assertEqual(normalizuj_volbu("35"), "36")
        self.assertEqual(normalizuj_volbu("36"), "37")
        obnoveno = Hra.from_dict(migrovano)
        self.assertIsInstance(obnoveno.zivy_svet, ZivySvetSystem)

    def test_vychodni_mesto_je_propojene_a_cestovatelne(self):
        hra = Hra()
        hra.svet.aktualni_lokace = "pristav"
        hra.svet.odhal_lokaci("vychodni_pristav")
        hra.svet.odhal_lokaci("vychodni_trziste")
        hra.svet.odhal_lokaci("pristav")

        with patch("random.random", return_value=0.99):
            self.assertTrue(hra.svet.cestuj("vychodni_pristav", hra))
            self.assertTrue(hra.svet.cestuj("vychodni_trziste", hra))

        self.assertIn("vychodni_pristav", LOKACE["pristav"]["sousedni"])
        self.assertIn("vychodni_pristav", hra.svet.odhalene_lokace)

    def test_ai_najde_nejkratsi_cestu_k_cili_a_zvazuje_uzitek(self):
        graf = {
            "pevnost": ("trh", "les"),
            "trh": ("pevnost", "pristav"),
            "pristav": ("trh", "vychodni_pristav"),
            "vychodni_pristav": ("pristav", "vychodni_trziste"),
            "vychodni_trziste": ("vychodni_pristav",),
            "les": ("pevnost",),
        }

        vzdalenosti = vzdalenosti_od_cilu(graf, ("vychodni_trziste",))

        self.assertEqual(vzdalenosti["pevnost"], 4)
        self.assertEqual(
            vyber_nejlepsi_uzitek((("bezpecna", 1), ("rizikova", 3))),
            "rizikova",
        )

    def test_zivy_svet_ulozi_stav_druheho_mesta_a_ai_cil(self):
        hra = Hra()
        hra.zivy_svet.mesta["vychodni_brod"].uprav(bezpeci=-8, prosperita=12)
        hra.hrac.den = 2
        hra.zivy_svet.posun_den(hra)

        obnovena = Hra.from_dict(hra.to_dict())

        self.assertEqual(
            obnovena.zivy_svet.mesta["vychodni_brod"].prosperita,
            hra.zivy_svet.mesta["vychodni_brod"].prosperita,
        )
        self.assertIn(
            hra.zivy_svet.postavy[0]["lokace"],
            hra.svet.odhalene_lokace,
        )

    def test_mapa_barvi_lokace_podle_frakcni_kontroly(self):
        hra = Hra()
        hra.svet.aktualni_lokace = "pevnost"
        hra.svet.odhal_lokaci("trh")

        uzel = hra.svet._format_uzel("trh", hra)

        self.assertIn(str(YELLOW), uzel)
        self.assertEqual(hra.zivy_svet.frakce_lokace("trh"), "obchodnici")

    def test_frakcni_vliv_a_mestske_udalosti_se_ukladaji(self):
        hra = Hra()
        hra.hrac.den = 4
        hra.zivy_svet.posun_den(hra)

        obnovena = Hra.from_dict(hra.to_dict())

        self.assertEqual(
            obnovena.zivy_svet.kontrola_lokaci,
            hra.zivy_svet.kontrola_lokaci,
        )
        self.assertEqual(
            obnovena.zivy_svet.udalosti_mesta,
            hra.zivy_svet.udalosti_mesta,
        )
        self.assertEqual(len(obnovena.zivy_svet.udalosti_mesta), 1)

    def test_rozhodnuti_mestske_udalosti_maji_cenu_a_dopad(self):
        hra = Hra()
        hra.hrac.den = 4
        hra.zivy_svet.posun_den(hra)
        udalost = hra.zivy_svet.udalosti_mesta[0]
        mesto = hra.zivy_svet.mesta[udalost["mesto_id"]]
        prosperita_pred = mesto.prosperita
        zlato_pred = hra.hrac.gold

        with patch("builtins.input", return_value="1"), redirect_stdout(io.StringIO()):
            self.assertTrue(hra.zivy_svet._vyres_udalost_mesta(hra, udalost))

        self.assertEqual(hra.hrac.gold, zlato_pred - 25)
        self.assertEqual(mesto.prosperita, prosperita_pred + 5)

    def test_karavanni_prijem_respektuje_bezpeci_mest(self):
        hra = Hra()
        prijem_bezpecnych_mest = hra.zivy_svet._prijem_karavan()
        hra.zivy_svet.mesta["vychodni_brod"].uprav(bezpeci=-100)

        self.assertLess(
            hra.zivy_svet._prijem_karavan(),
            prijem_bezpecnych_mest,
        )

    def test_plna_fronta_nezahodi_dokonceny_frakcni_cil(self):
        hra = Hra()
        hra.zivy_svet.nabidky = [
            {
                "frakce_id": "policie",
                "frakce_nazev": "Policie",
                "cilek": "hlídky",
                "text": "Situace",
                "postava": "Mira",
            }
            for _ in range(10)
        ]
        hra.zivy_svet.frakcni_cile["policie"]["cil"] = 1
        hra.hrac.den = 1

        hra.zivy_svet.posun_den(hra)
        obnovena = Hra.from_dict(hra.to_dict())

        self.assertEqual(len(hra.zivy_svet.nabidky), 10)
        self.assertEqual(
            obnovena.zivy_svet.frakcni_cile["policie"]["postup"],
            1,
        )

    def test_ignorovana_mestska_udalost_ma_trvaly_dusledek(self):
        hra = Hra()
        hra.hrac.den = 4
        hra.zivy_svet.posun_den(hra)
        udalost = hra.zivy_svet.udalosti_mesta[0]
        mesto = hra.zivy_svet.mesta[udalost["mesto_id"]]
        prosperita_pred = mesto.prosperita

        with patch("builtins.input", return_value="0"), redirect_stdout(io.StringIO()):
            self.assertTrue(hra.zivy_svet._vyres_udalost_mesta(hra, udalost))

        self.assertEqual(mesto.prosperita, prosperita_pred - 2)
        self.assertIn("bez zásahu", hra.zivy_svet.historie[-1]["text"])

    def test_fakcni_cil_pusobi_na_mesto_kde_ma_fakce_vliv(self):
        hra = Hra()
        mesto = hra.zivy_svet.mesta["vychodni_brod"]
        bezpeci_pred = mesto.bezpeci
        stabilita_pred = mesto.stabilita

        zprava = hra.zivy_svet._vykonej_cil_fakce("policie")

        self.assertEqual(mesto.bezpeci, bezpeci_pred + 1)
        self.assertEqual(mesto.stabilita, stabilita_pred + 1)
        self.assertEqual(
            hra.zivy_svet.frakcni_cile["policie"]["mesto_id"],
            "vychodni_brod",
        )
        self.assertIn("Východní Brod", zprava)

    def test_fakcni_akce_maji_omezeny_a_odlisny_dopad(self):
        hra = Hra()
        stare_mesto = hra.zivy_svet.mesta["stare_mesto"]
        bezpeci_pred = stare_mesto.bezpeci
        prosperita_pred = stare_mesto.prosperita

        hra.zivy_svet._vykonej_cil_fakce("podsveti")

        self.assertEqual(stare_mesto.prosperita, prosperita_pred + 1)
        self.assertEqual(stare_mesto.bezpeci, bezpeci_pred - 1)

    def test_automaticky_vyvoj_zustava_v_rozsahu_po_ctyriceti_dnech(self):
        hra = Hra()
        for den in range(1, 41):
            hra.hrac.den = den
            hra.zivy_svet.posun_den(hra)

        for mesto in hra.zivy_svet.mesta.values():
            for atribut in ("prosperita", "bezpeci", "stabilita"):
                self.assertGreaterEqual(getattr(mesto, atribut), 0)
                self.assertLessEqual(getattr(mesto, atribut), 100)
        self.assertLessEqual(len(hra.zivy_svet.udalosti_mesta), 3)
        self.assertLessEqual(len(hra.zivy_svet.nabidky), 10)
        self.assertLessEqual(len(hra.zivy_svet.historie), 30)


if __name__ == "__main__":
    unittest.main()

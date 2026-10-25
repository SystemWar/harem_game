import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.menu_hlavni import normalizuj_volbu
from game.save_load import Hra, migrate_save
from game.zivy_svet import ZivySvetSystem
from models.frakce import FrakcniSystem


class ZivySvetTesty(unittest.TestCase):
    def test_vsechny_frakce_maji_cil_a_stav_se_uklada(self):
        svet = ZivySvetSystem()

        self.assertEqual(set(svet.frakcni_cile), set(FrakcniSystem().frakce))
        obnoveno = ZivySvetSystem.from_dict(svet.to_dict())
        self.assertEqual(obnoveno.frakcni_cile, svet.frakcni_cile)
        self.assertEqual(
            {postava["id"] for postava in obnoveno.postavy},
            {postava["id"] for postava in svet.postavy},
        )

    def test_denni_tah_pohybuje_npc_a_neopakuje_se(self):
        hra = Hra()
        hra.hrac.den = 2
        postava_pred = hra.zivy_svet.postavy[0]["lokace"]

        zpravy = hra.zivy_svet.posun_den(hra)
        druhy_vysledek = hra.zivy_svet.posun_den(hra)

        self.assertTrue(zpravy)
        self.assertEqual(druhy_vysledek, [])
        self.assertNotEqual(hra.zivy_svet.postavy[0]["lokace"], postava_pred)
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


if __name__ == "__main__":
    unittest.main()

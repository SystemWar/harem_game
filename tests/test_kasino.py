import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.kasino import (
    hraj_duel_kostek,
    hraj_jednadvacet,
    hraj_kostky,
    otevri_kasino,
    vylepsi_kasino,
)
from game.menu_hlavni import normalizuj_volbu
from game.save_load import Hra, migrate_save
from models.kasino import KasinoSystem
from game.zivy_svet import FRAKCNI_AKCE, ZivySvetSystem
from models.frakce import FrakcniSystem


class KasinoTesty(unittest.TestCase):
    def test_otevreni_a_vylepseni_zvysi_limit_a_prijem(self):
        hra = Hra()
        hra.hrac.gold = 1_000

        with redirect_stdout(io.StringIO()):
            self.assertTrue(otevri_kasino(hra))
            self.assertTrue(vylepsi_kasino(hra))

        self.assertEqual(hra.hrac.gold, 450)
        self.assertEqual(hra.kasino.limit_sazky, 200)
        self.assertEqual(hra.kasino.denni_prijem(2), 20)
        self.assertEqual(hra.kasino.denni_prijem(2), 0)

    def test_kostky_vyhra_a_remiza_zapisuji_historii(self):
        hra = Hra()
        hra.hrac.gold = 100
        hra.kasino = KasinoSystem(otevreno=True, uroven=1)

        with patch("game.kasino.random.randint", side_effect=[2, 3]), \
             redirect_stdout(io.StringIO()):
            self.assertTrue(hraj_kostky(hra, 10, "pod"))
        self.assertEqual(hra.hrac.gold, 110)
        self.assertEqual(hra.kasino.cisty_zisk, 10)

        with patch("game.kasino.random.randint", side_effect=[3, 4]), \
             redirect_stdout(io.StringIO()):
            self.assertTrue(hraj_kostky(hra, 10, "nad"))
        self.assertEqual(hra.hrac.gold, 110)
        self.assertEqual(hra.kasino.remizy, 1)
        self.assertEqual(len(hra.kasino.historie), 2)

    def test_neplatna_sazka_neodebere_zlato(self):
        hra = Hra()
        hra.hrac.gold = 500
        hra.kasino = KasinoSystem(otevreno=True, uroven=1)

        with redirect_stdout(io.StringIO()):
            self.assertFalse(hraj_kostky(hra, 101, "pod"))

        self.assertEqual(hra.hrac.gold, 500)
        self.assertEqual(hra.kasino.celkem_vsazeno, 0)

    def test_jednadvacet_blackjack_plati_zvyseny_vynos(self):
        hra = Hra()
        hra.hrac.gold = 100
        hra.kasino = KasinoSystem(otevreno=True, uroven=1)
        tahy = iter([1, 13, 10, 7])

        with patch("game.kasino.random.randint", side_effect=lambda *_: next(tahy)), \
             redirect_stdout(io.StringIO()):
            self.assertTrue(hraj_jednadvacet(hra, 10))

        self.assertEqual(hra.hrac.gold, 115)
        self.assertEqual(hra.kasino.vyhry, 1)
        self.assertEqual(hra.kasino.cisty_zisk, 15)

    def test_duel_kostek_sazi_jen_zlato_a_vyhra_zvysi_vliv_gembleru(self):
        hra = Hra()
        hra.hrac.gold = 100
        hra.kasino = KasinoSystem(otevreno=True, uroven=1)
        reputace_pred = hra.frakce.frakce["gembleri"].reputace
        vliv_pred = hra.zivy_svet.kontrola_lokaci["cervena_ctvrt"].get("gembleri", 0)

        with patch("game.kasino.random.randint", side_effect=[6, 6, 1, 1]), \
             redirect_stdout(io.StringIO()):
            self.assertTrue(hraj_duel_kostek(hra, 10))

        self.assertEqual(hra.hrac.gold, 110)
        self.assertEqual(hra.kasino.historie[-1]["hra"], "Duel v kostkách")
        self.assertEqual(
            hra.frakce.frakce["gembleri"].reputace,
            reputace_pred + 1,
        )
        self.assertEqual(
            hra.zivy_svet.kontrola_lokaci["cervena_ctvrt"]["gembleri"],
            vliv_pred + 1,
        )

    def test_nova_frakce_ma_cil_a_migraci_stareho_save(self):
        frakce = FrakcniSystem()
        svet = ZivySvetSystem()

        self.assertIn("gembleri", frakce.frakce)
        self.assertEqual(set(svet.frakcni_cile), set(frakce.frakce))
        self.assertIn("gembleri", FRAKCNI_AKCE)
        obnovena = Hra.from_dict(migrate_save({"save_version": 2}))
        self.assertIn("gembleri", obnovena.frakce.frakce)
        self.assertIn("gembleri", obnovena.zivy_svet.frakcni_cile)

    def test_kasino_se_uklada_a_stary_save_dostane_vychozi_stav(self):
        hra = Hra()
        hra.kasino = KasinoSystem(
            otevreno=True, uroven=2, vyhry=3, historie=[{
                "den": 4, "hra": "Kostky", "sazka": 20,
                "cisty_vysledek": 20, "vysledek": "Výhra",
                "detail": "Padlo 4.",
            }],
        )

        obnovena = Hra.from_dict(hra.to_dict())
        stara_data = migrate_save({"save_version": 2})
        stara = Hra.from_dict(stara_data)

        self.assertEqual(obnovena.kasino.uroven, 2)
        self.assertEqual(obnovena.kasino.historie[0]["hra"], "Kostky")
        self.assertFalse(stara.kasino.otevreno)
        self.assertEqual(stara.kasino.uroven, 0)
        self.assertEqual(normalizuj_volbu("38"), "39")


if __name__ == "__main__":
    unittest.main()

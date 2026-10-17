import unittest
from unittest.mock import patch

from game.save_load import Hra
from game.souboje import ARENA_LADDER, BOSSOVE, Souboj, dostupni_bossove


class ArenaBossTesty(unittest.TestCase):
    def test_stinova_liga_je_paty_stupen(self):
        self.assertEqual(len(ARENA_LADDER), 5)
        self.assertEqual(ARENA_LADDER[-1]["rank"], 5)
        self.assertEqual(ARENA_LADDER[-1]["titul"], "Pán stínové arény")
        self.assertIn("krystaly", ARENA_LADDER[-1]["bonus_suroviny"])

    def test_kolos_je_zamceny_dokud_hrac_nedosahne_zlato_ligy(self):
        hra = Hra()
        hra.svet.aktualni_lokace = "podzemni_arena"
        hra.pevnost.arena_rank = 2
        self.assertNotIn("kolos_podzemni_areny", [boss_id for boss_id, _ in dostupni_bossove(hra)])

        hra.pevnost.arena_rank = 3
        self.assertIn("kolos_podzemni_areny", [boss_id for boss_id, _ in dostupni_bossove(hra)])

        hra.kampan.boss_porazeni.append("kolos_podzemni_areny")
        self.assertNotIn("kolos_podzemni_areny", [boss_id for boss_id, _ in dostupni_bossove(hra)])

    def test_kolos_ma_tri_faze_a_odmenu(self):
        hra = Hra()
        hra.pevnost.krystaly = 0
        hra.hrac.reputace_mesta = 0
        souboj = Souboj(hra.hrac, hra.mafie, hra)
        souboj.generuj_bosse(1, "kolos_podzemni_areny")
        self.assertEqual(len(souboj.nepritel.faze), 3)
        self.assertEqual(BOSSOVE["kolos_podzemni_areny"]["schopnost"], "otres_pisku")

        souboj.nepritel.faze = []
        souboj.nepritel.hp = 1
        souboj.nepritel.obrana = 0
        with patch("builtins.input", side_effect=["1", ""]), patch("random.randint", return_value=0):
            self.assertTrue(souboj.proved_boj())
        self.assertIn("kolos_podzemni_areny", hra.kampan.boss_porazeni)
        self.assertEqual(hra.pevnost.krystaly, 12)
        self.assertEqual(hra.hrac.reputace_mesta, 6)
        self.assertGreaterEqual(hra.hrac.inventar.pocet_predmetu("trofej_kolosu"), 1)

    def test_otres_pisku_ublizi_az_od_druhe_faze(self):
        hra = Hra()
        souboj = Souboj(hra.hrac, hra.mafie, hra)
        souboj.generuj_bosse(1, "kolos_podzemni_areny")
        with patch("random.random", return_value=0.0):
            self.assertFalse(souboj._efekt_bosse(souboj.nepritel))
        souboj.nepritel.faze_index = 1
        with patch("random.random", return_value=0.0):
            self.assertTrue(souboj._efekt_bosse(souboj.nepritel))
        self.assertLess(hra.hrac.hp, hra.hrac.max_hp)

    def test_vitezstvi_ve_stinove_lize_prida_krystaly(self):
        hra = Hra()
        hra.pevnost.krystaly = 3
        souboj = Souboj(hra.hrac, hra.mafie, hra)
        souboj.nepritel = souboj.generuj_nepritele(1)
        souboj.nepritel.hp = 1
        souboj.nepritel.arena = True
        souboj.nepritel.arena_rank = 5
        with patch("builtins.input", side_effect=["1", ""]), patch("random.randint", return_value=0):
            self.assertTrue(souboj.proved_boj())
        self.assertEqual(hra.pevnost.arena_rank, 5)
        self.assertEqual(hra.pevnost.krystaly, 28)

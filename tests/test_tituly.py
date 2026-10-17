import unittest

from game.save_load import Hra
from game.souboje import Souboj
from game.tituly import hodnost, sance_vyzvy, uprav_dan, zaznamenej_povyseni
from game.udalosti import vyzva_z_areny


class TitulyTesty(unittest.TestCase):
    def test_novy_pan_nema_bonus(self):
        hra = Hra()
        self.assertEqual(hodnost(hra)["id"], "neznamy")
        self.assertEqual(uprav_dan(100, hra), 100)
        self.assertEqual(sance_vyzvy(hra), 4)

    def test_stinova_liga_sama_nestaci_na_pana_stinu(self):
        hra = Hra()
        hra.pevnost.arena_rank = 5
        hra.pevnost.uroven = 3
        hra.hrac.reputace_mesta = 14
        self.assertEqual(hodnost(hra)["id"], "pan_cerne_areny")
        hra.hrac.reputace_mesta = 15
        self.assertEqual(hodnost(hra)["id"], "pan_stinu")
        self.assertEqual(uprav_dan(100, hra), 118)

    def test_povyseni_zvysi_vztahy_jen_jednou(self):
        hra = Hra()
        npc_id = next(iter(hra.svet.vztahy_npc))
        puvodni = hra.svet.vztahy_npc[npc_id]
        hra.pevnost.arena_rank = 1
        self.assertEqual(zaznamenej_povyseni(hra)["nazev"], "Strážce dvora")
        self.assertEqual(hra.svet.vztahy_npc[npc_id], puvodni + 1)
        self.assertIsNone(zaznamenej_povyseni(hra))
        self.assertEqual(hra.svet.vztahy_npc[npc_id], puvodni + 1)

        hra.pevnost.arena_rank = 0
        self.assertIsNone(zaznamenej_povyseni(hra))
        self.assertEqual(hra.hrac.titul_mesta, "Strážce dvora")
        hra.pevnost.arena_rank = 1
        self.assertIsNone(zaznamenej_povyseni(hra))
        self.assertEqual(hra.svet.vztahy_npc[npc_id], puvodni + 1)

    def test_vysoka_hodnost_odradi_vyzyvatele_a_nahodne_boje(self):
        hra = Hra()
        hra.hrac.reputace_mesta = 0
        hra.hrac.gold = 100
        vyzva_z_areny(hra)
        self.assertLess(hra.hrac.gold, 100)

        hra.pevnost.arena_rank = 3
        hra.pevnost.uroven = 2
        hra.hrac.reputace_mesta = 8
        pred = hra.hrac.reputace_mesta
        vyzva_z_areny(hra)
        self.assertEqual(hra.hrac.reputace_mesta, pred + 1)

        slaby = Souboj(hra.hrac, hra.mafie, hra)
        silny = Souboj(hra.hrac, hra.mafie, None)
        import random
        random.seed(1)
        slaby.generuj_nepritele(3)
        random.seed(1)
        silny.generuj_nepritele(3)
        self.assertLess(slaby.nepritel.hp, silny.nepritel.hp)

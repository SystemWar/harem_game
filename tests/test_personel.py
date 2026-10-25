import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.personel import (
    menu_personalu,
    najmi_personal,
    nastav_rozkaz_armady,
    zpracuj_denni_personal,
)
from game.save_load import Hra
from models.agent import Agent


class PersonelTesty(unittest.TestCase):
    def test_nabor_overi_kapacitu_a_uhradi_cenu(self):
        hra = Hra()
        hra.hrac.gold = 200
        hra.hrac.max_agentu = 1

        with redirect_stdout(io.StringIO()):
            self.assertTrue(najmi_personal(hra, "pruzkumnik"))
            self.assertFalse(najmi_personal(hra, "herold"))

        self.assertEqual(hra.hrac.gold, 80)
        self.assertEqual(len(hra.hrac.agenti), 1)
        self.assertEqual(hra.hrac.agenti[0].ukol, "pruzkumnik")

    def test_nula_v_podmenu_naboru_nevybere_posledni_specializaci(self):
        hra = Hra()
        hra.hrac.gold = 500

        with patch("builtins.input", side_effect=["1", "0", "0"]), \
             redirect_stdout(io.StringIO()):
            menu_personalu(hra)

        self.assertEqual(hra.hrac.agenti, [])
        self.assertEqual(hra.hrac.gold, 500)

    def test_nedostatek_platu_personalu_nezastavi_armadni_rozkaz(self):
        hra = Hra()
        hra.hrac.gold = 0
        hra.hrac.agenti.append(
            Agent("Správce", specializace="spravce", ukol="spravce", plat=4)
        )
        hra.mafie.vojaci = 1
        hra.mafie.rozkaz_armady = "vycvik"

        with redirect_stdout(io.StringIO()):
            zpracuj_denni_personal(hra)

        self.assertEqual(hra.mafie.moral_armady, 4)
        self.assertEqual(hra.hrac.agenti[0].xp, 0)

    def test_nula_v_rozkazech_armady_neprepise_aktivni_rozkaz(self):
        hra = Hra()
        hra.mafie.vojaci = 1
        hra.mafie.rozkaz_armady = "patrolovat"

        with patch("builtins.input", return_value="0"), \
             redirect_stdout(io.StringIO()):
            nastav_rozkaz_armady(hra)

        self.assertEqual(hra.mafie.rozkaz_armady, "patrolovat")

    def test_osobni_historie_akce_neprebira_zpravu_jineho_agenta(self):
        hra = Hra()
        hra.hrac.gold = 20
        hra.hrac.agenti = [
            Agent("Herold", specializace="herold", ukol="herold", plat=5),
            Agent("Správce", specializace="spravce", ukol="spravce", plat=4),
        ]

        with redirect_stdout(io.StringIO()):
            zpracuj_denni_personal(hra)

        self.assertIn("rozšířil zprávy", hra.hrac.agenti[0].posledni_akce)
        self.assertIn("obchodní příjem", hra.hrac.agenti[1].posledni_akce)

    def test_spravce_cileneho_mesta_prizpusobi_prijem_prosperite(self):
        hra = Hra()
        hra.hrac.gold = 100
        hra.hrac.agenti = [
            Agent(
                "Správce", specializace="spravce", ukol="spravce",
                cil_mesto="vychodni_brod", plat=4,
            )
        ]
        mesto = hra.zivy_svet.mesta["vychodni_brod"]
        mesto.prosperita = 50

        with redirect_stdout(io.StringIO()):
            zpracuj_denni_personal(hra)

        self.assertEqual(hra.hrac.gold, 106)
        self.assertIn("Východní Brod", hra.hrac.agenti[0].posledni_akce)

    def test_stary_agent_bez_ciloveho_mesta_se_nacte(self):
        agent = Agent.from_dict({
            "jmeno": "Průzkumník",
            "specializace": "pruzkumnik",
            "ukol": "pruzkumnik",
            "cil_lokace": "pevnost",
        })

        self.assertEqual(agent.cil_mesto, "")


if __name__ == "__main__":
    unittest.main()

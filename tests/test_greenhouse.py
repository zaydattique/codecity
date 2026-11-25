import unittest
from dataclasses import replace
from codecity.model import Plant, advance, DEFAULT_CODE
from codecity.rules import evaluate, RuleError

class TestGreenhouse(unittest.TestCase):
    def test_branches(self):
        self.assertFalse(evaluate(DEFAULT_CODE,Plant()))
        self.assertTrue(evaluate(DEFAULT_CODE,Plant(moisture=20)))
        self.assertTrue(evaluate(DEFAULT_CODE,Plant(light=2)))
    def test_changed_rule(self):
        self.assertTrue(evaluate(DEFAULT_CODE.replace("40","70"),Plant()))
    def test_grow_and_stress(self):
        self.assertGreater(advance(Plant(),False).growth,0)
        self.assertLess(advance(Plant(light=0),False).health,1)
        self.assertEqual(advance(Plant(light=0),True).growth,0)
        self.assertLess(advance(Plant(moisture=95),True).health,1)
    def test_dead_plant(self):
        self.assertEqual(advance(Plant(health=0),True).health,0)
    def test_determinism(self):
        self.assertEqual(advance(Plant(),True),advance(Plant(),True))
    def test_bounds(self):
        with self.assertRaises(ValueError): Plant(moisture=101)
        self.assertEqual(advance(Plant(day=60),True).day,60)
    def test_denials(self):
        for code in ("import os","while True: pass", "if True:\n    irrigate(True)\nelse:\n    open('x')","if moisture.__class__:\n    irrigate(True)\nelse:\n    irrigate(False)","if True:\n    irrigate(1)\nelse:\n    irrigate(False)","if True:\n    irrigate(True)"):
            with self.subTest(code=code), self.assertRaises(RuleError):
                evaluate(code,Plant())
if __name__=="__main__": unittest.main()

import unittest,tempfile
from pathlib import Path
from codecity.model import Plant,DEFAULT_CODE
from codecity.rules import RuleError,evaluate
from codecity.session import Experiment,challenge,load_profile,write_profile

class SessionTests(unittest.TestCase):
    def test_full_domain(self):
        p,t,f=challenge(DEFAULT_CODE.replace("40","50"))
        self.assertEqual(p,t);self.assertEqual(t,78982);self.assertFalse(f)
        p,t,f=challenge(DEFAULT_CODE.replace("< 40","< 50 and light > 0"))
        self.assertLess(p,t);self.assertEqual(f[0][:3],(0,0,0))
    def test_all_boundaries(self):
        for n in range(101):
            self.assertEqual(evaluate(DEFAULT_CODE,Plant(moisture=n)),n<40)
    def test_pause_restore_and_resume(self):
        e=Experiment();e.start(DEFAULT_CODE,Plant(moisture=42,light=15,temperature=28))
        for _ in range(12):e.step()
        e.playing=False;before=e.snapshot();self.assertFalse(e.step());self.assertEqual(before,e.snapshot())
        clone=Experiment.restore(before);self.assertFalse(clone.playing)
        clone.playing=e.playing=True
        for _ in range(48):clone.step();e.step()
        self.assertEqual(clone.snapshot(),e.snapshot());self.assertEqual(e.state.growth,1)
    def test_invalid_rule_atomic(self):
        e=Experiment();e.start(DEFAULT_CODE,Plant());e.step();before=e.snapshot()
        with self.assertRaises(RuleError):e.start("import os",Plant(moisture=10))
        self.assertEqual(e.snapshot(),before);self.assertTrue(e.playing)
    def test_tamper_rejected(self):
        e=Experiment();e.start(DEFAULT_CODE,Plant());e.step();data=e.snapshot()
        data["state"]["growth"]=1
        with self.assertRaises(ValueError):Experiment.restore(data)
    def test_profile_roundtrip_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"progress.json"
            self.assertFalse(load_profile(p)["greenhouse_complete"])
            e=Experiment();e.start(DEFAULT_CODE,Plant());e.step()
            data=dict(greenhouse_complete=True,voice=False,pace=.7,experiment=e.snapshot(),draft="invalid draft")
            write_profile(p,data);self.assertEqual(load_profile(p),data)
            p.write_text("{broken");self.assertIsNone(load_profile(p)["experiment"])
    def test_elif_nested_and_invalid_indentation(self):
        code="if moisture < 40:\n    if temperature >= 12 and not light == 0:\n        irrigate(True)\n    else:\n        irrigate(False)\nelif moisture == 40:\n    irrigate(False)\nelse:\n    irrigate(False)"
        self.assertTrue(evaluate(code,Plant(moisture=39)))
        self.assertFalse(evaluate(code,Plant(moisture=39,light=0)))
        self.assertFalse(evaluate(code,Plant(moisture=40)))
        with self.assertRaises(RuleError):evaluate("if moisture < 40:\nirrigate(True)\nelse:\n    irrigate(False)",Plant())

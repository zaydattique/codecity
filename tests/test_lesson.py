import unittest
from codecity.model import Plant,DEFAULT_CODE
from codecity.rules import trace_rule,evaluate,RuleError
from codecity.session import Experiment
from codecity.lesson import comparison,trace_day,DRY_RULE,WET_RULE,FAN_EXAMPLE,FAN_START,fan_check

class LessonTests(unittest.TestCase):
    def test_trace_real_branches(self):
        for n,line in ((20,2),(40,4),(60,4)):
            p=Plant(moisture=n);t=trace_rule(DEFAULT_CODE,p)
            self.assertEqual(t.conditions,((1,n<40),))
            self.assertEqual(t.action_line,line)
            self.assertEqual(t.action,evaluate(DEFAULT_CODE,p))
    def test_trace_nested(self):
        code="if moisture < 30:\n    irrigate(True)\nelif moisture < 40 and light > 0:\n    irrigate(True)\nelse:\n    irrigate(False)"
        for n,lines in ((20,((1,True),)),(35,((1,False),(3,True))),(40,((1,False),(3,False)))):
            p=Plant(moisture=n);t=trace_rule(code,p)
            self.assertEqual(t.conditions,lines);self.assertEqual(t.action,evaluate(code,p))
        with self.assertRaises(RuleError):trace_rule("if _condition(1,True):\n    irrigate(True)\nelse:\n    irrigate(False)",Plant())
    def test_timeline_reproducible(self):
        e=Experiment();e.start(DEFAULT_CODE,Plant(moisture=42,light=15,temperature=28))
        e.seek(60);end=e.snapshot();e.seek(10);self.assertFalse(e.playing);self.assertEqual(e.state.day,10)
        self.assertIsNotNone(trace_day(e));e.playing=True
        for _ in range(50):e.step()
        self.assertEqual(e.snapshot(),end)
        e.seek(0);self.assertIsNone(trace_day(e));self.assertEqual(e.state.growth,0)
    def test_compare_isolated(self):
        e=Experiment();e.start(DEFAULT_CODE,Plant(moisture=20));e.seek(12);before=e.snapshot()
        a,b=comparison(e.source,e.initial,60,DRY_RULE)
        self.assertEqual(a.state.growth,1);self.assertEqual(b.state.growth,0)
        self.assertEqual(b.state.health,0);self.assertEqual(e.snapshot(),before)
        a,b=comparison(e.source,e.initial,60,WET_RULE)
        self.assertLess(b.state.health,.2)
    def test_independent_actuator(self):
        for temp in (29,30,31):
            t=trace_rule(FAN_EXAMPLE,Plant(temperature=temp),"ventilate")
            self.assertEqual(t.action,temp>30)
        p,t,f=fan_check(FAN_EXAMPLE);self.assertEqual(p,t);self.assertEqual(t,78982);self.assertIsNone(f)
        p,t,f=fan_check(FAN_START);self.assertLess(p,t);self.assertEqual(f[0].temperature,31)
        with self.assertRaises(RuleError):trace_rule(DEFAULT_CODE,Plant(),"ventilate")

    def test_mature_stress_intervention(self):
        from codecity.lesson import stop_after_growth
        initial=Plant(moisture=42,light=15,temperature=28)
        self.assertEqual(stop_after_growth(initial,20).growth,1)
        end=stop_after_growth(initial,60)
        self.assertEqual(end.growth,1);self.assertEqual(end.health,0)

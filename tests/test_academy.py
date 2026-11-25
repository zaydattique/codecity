import pytest
from ai.academy import Interpreter, LessonError, handle

def test_real_loop_and_conditions():
    r=Interpreter().run("count = 2\nfor lamp in range(count):\n    if lamp < count:\n        set_lamp(lamp, True)\nprint('Restored', count)")
    assert r["completed"] and r["output"]=="Restored 2"
    assert r["commands"]==[{"lamp":0,"on":True},{"lamp":1,"on":True}]

@pytest.mark.parametrize("source",["import os","print(open('a'))","while True: pass","if False:\n    import os","print((1).__class__)","for i in range(1000):\n    print(i)","print(2**100000)","set_lamp(2, True)","set_lamp(0, 1)","print(100000*100000)","print(1//0)","print('x'*1000)"])
def test_denial(source):
    with pytest.raises(LessonError):Interpreter().run(source)

def test_failed_request_is_atomic():
    r=handle({"version":1,"id":"a"*32,"source":"set_lamp(0, True)\nprint(unknown)"})
    assert not r["ok"] and r["commands"]==[] and not r["completed"]

def test_wrong_result():
    r=Interpreter().run("set_lamp(0, True)\nprint('one lamp')")
    assert not r["completed"]

def test_output_and_step_limits():
    with pytest.raises(LessonError):Interpreter().run("for i in range(32):\n    for j in range(32):\n        x = i+j")
    with pytest.raises(LessonError):Interpreter().run("for i in range(32):\n    print('abcdefghijklmnopqrstuvwxyz')")


def test_bounded_while_and_lists():
    r=Interpreter().run("ids = [0, 1]\ni = 0\nwhile i < 2:\n    set_lamp(ids[i], True)\n    i = i + 1\nprint('Ready')")
    assert r["completed"] and r["output"]=="Ready"
    assert {"while","list","index","arithmetic","assignment","print"} <= set(r["concepts"])

@pytest.mark.parametrize("source",[
    "i = 0\nwhile True:\n    i = i + 1",
    "x = [0,1,2,3,4,5,6,7,8]",
    "x = [[1]]",
    "x = [1]\nprint(x[2])",
    "x = [1]\nx[0] = 2",
    "x = [1]\nprint(x[True])",
    "x = [1]\nprint(x[:])",
    "for i in range(0,1,0):\n    print(i)",
])
def test_extended_language_denial(source):
    with pytest.raises(LessonError):Interpreter().run(source)

def test_executed_concepts_not_dead_code():
    r=Interpreter().run("if False:\n    x = [1]\n    while True:\n        print(x[0])\nprint('Ready')")
    assert "list" not in r["concepts"] and "while" not in r["concepts"]
    assert r["concepts"]==["if","print"]

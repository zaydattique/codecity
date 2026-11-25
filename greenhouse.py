"""Native Python greenhouse integration preview. No browser or Blender needed at runtime."""
import sys
from pathlib import Path
from dataclasses import replace
from codecity.model import Plant, advance
from codecity.rules import evaluate, compile_rule, RuleError

DEFAULT = "if moisture < 40:\n    irrigate(True)\nelse:\n    irrigate(False)"
def assets():
    return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))/"runtime"

def self_test():
    from panda3d.core import Loader, Filename, LoaderOptions
    root=assets()
    loader=Loader.getGlobalPtr()
    for name in ["bench.egg","drop.egg"]+[f"plant-{f:03}.egg" for f in list(range(1,121,3))+[120]]:
        assert (root/name).is_file(), name
        node=loader.loadSync(Filename.fromOsSpecific(str(root/name)),LoaderOptions())
        assert node is not None, name
    assert evaluate(DEFAULT,Plant(moisture=20))
    assert not evaluate(DEFAULT,Plant(moisture=60))
    assert advance(Plant(moisture=20),True).growth>0
    return 0

def run():
    from panda3d.core import loadPrcFileData, AmbientLight, DirectionalLight, Vec4, TextNode, Filename
    loadPrcFileData("", "window-title CodeCity | Greenhouse\nwin-size 1280 720\nframebuffer-multisample 1\nmultisamples 4\nsync-video true")
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectEntry, DirectSlider
    from direct.task import Task
    app=ShowBase()
    app.disableMouse()
    app.setBackgroundColor(.13,.19,.16,1)
    app.camLens.setFov(42)
    app.camera.setPos(.32,-1.5,.35);app.camera.lookAt(.24,0,.085)
    ambient=AmbientLight("fill");ambient.setColor(Vec4(.56,.56,.52,1))
    sun=DirectionalLight("daylight");sun.setColor(Vec4(.75,.72,.65,1))
    al=app.render.attachNewNode(ambient);sl=app.render.attachNewNode(sun);sl.setHpr(-35,-55,0)
    app.render.setLight(al);app.render.setLight(sl)
    root=assets()
    def model(name):
        n=app.loader.loadModel(Filename.fromOsSpecific(str(root/name)))
        if n.isEmpty(): raise RuntimeError("Missing geometry: "+name)
        n.reparentTo(app.render)
        return n
    bench=model("bench.egg")
    frames=list(range(1,121,3))+[120]
    plants=[model(f"plant-{f:03}.egg") for f in frames]
    for p in plants:p.hide()
    drops=[model("drop.egg") for _ in range(8)]
    for p in drops:p.hide()
    panel=DirectFrame(parent=app.a2dTopRight,frameColor=(.055,.095,.08,1),frameSize=(-1.26,0,-2,0))
    def label(text,x,z,scale=.044):
        return DirectLabel(parent=panel,text=text,pos=(x,0,z),scale=scale,text_fg=(.91,.94,.87,1),text_align=TextNode.ALeft,frameColor=(0,0,0,0))
    label("CODECITY   /   01", -1.17,-.12,.047)
    label("If / Else", -1.17,-.25,.075)
    label("Greenhouse controller", -1.17,-.34,.045)
    label("Edit the condition, then run.",-1.17,-.45,.042)
    editor=DirectEntry(parent=panel,initialText=DEFAULT,scale=.042,pos=(-1.14,0,-.55),width=25,numLines=6,frameColor=(.12,.20,.16,1),text_fg=(.95,.96,.88,1),focus=0)
    info=label("",-1.17,-1.04,.041)
    status=label("Ready. Time is compressed.",-1.17,-1.76,.037)
    state=Plant(); source=DEFAULT; playing=False; water=False; elapsed=0; shown=-1; visual=0.
    settings={}
    def slider(name,lo,hi,value,z):
        l=label(name,-1.17,z,.041)
        def change():
            if name in settings: l["text"]=f"{name}: {int(settings[name]['value'])}"
        s=DirectSlider(parent=panel,range=(lo,hi),value=value,pageSize=1,scale=.49,pos=(-.63,0,z-.065),command=change)
        settings[name]=s;change()
    slider("Moisture",0,100,55,-1.14)
    slider("Light hours",0,16,8,-1.31)
    slider("Temperature C",0,45,22,-1.48)
    def inputs():
        return dict(moisture=int(settings["Moisture"]["value"]),light=int(settings["Light hours"]["value"]),temperature=int(settings["Temperature C"]["value"]))
    def start():
        nonlocal state,source,playing,elapsed,water
        candidate=editor.get()
        try: compile_rule(candidate)
        except RuleError as e:
            status["text"]="Invalid rule. Check syntax / indentation."
            print(str(e));playing=False;water=False;return
        source=candidate;state=replace(state,**inputs());elapsed=1;playing=True
        editor["focus"]=0
        status["text"]="Running real Python conditionals."
    def pause():
        nonlocal playing
        playing=False;status["text"]="Paused. Run resumes with current inputs."
    def reset():
        nonlocal state,playing,water,elapsed,visual
        playing=False;water=False;elapsed=0;visual=0
        state=Plant(**inputs());status["text"]="Reset to seed."
    def button(text,x,func):
        DirectButton(parent=panel,text=text,scale=.048,pos=(x,0,-1.65),command=func,frameColor=(.22,.43,.29,1),text_fg=(1,1,1,1),pad=(.5,.35))
    button("Run",-.99,start);button("Pause",-.62,pause);button("Reset",-.24,reset)
    label("Simplified model / integration preview",-1.17,-1.91,.035)
    def update(task):
        nonlocal state,elapsed,water,playing,shown,visual
        dt=min(.10,app.clock.getDt()) if hasattr(app,"clock") else min(.10,globalClock.getDt())
        if playing:
            elapsed+=dt
            if elapsed>=1.1:
                elapsed=0
                water=evaluate(source,state);state=advance(state,water)
                if state.day>=60:playing=False;water=False
            visual+=(state.growth-visual)*min(1,dt*3.0)
        index=min(len(plants)-1,round(visual*(len(plants)-1)))
        if index!=shown:
            if shown>=0:plants[shown].hide()
            plants[index].show();shown=index
        plants[index].setColorScale(1,.52+.48*state.health,.42+.58*state.health,1)
        for i,p in enumerate(drops):
            if playing and water:
                phase=(elapsed*2.8+i/len(drops))%1
                p.setPos((i%3-1)*.004,.035,.36-(.36-.058)*phase);p.show()
            else:p.hide()
        info["text"]=f"Day {state.day:02}   Soil {state.moisture}%   Water {'ON' if water else 'OFF'}"
        return Task.cont
    app.taskMgr.add(update,"simulation")
    app.accept("escape",pause)
    app.run()

if __name__=="__main__":
    if "--self-test" in sys.argv:sys.exit(self_test())
    run()

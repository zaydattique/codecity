"""BloomLogic native Python learning studio. Blender assets render in Panda3D."""
import sys, json, traceback, os
from pathlib import Path
from codecity.model import Plant, advance, DEFAULT_CODE
from codecity.rules import evaluate, compile_rule, RuleError
from codecity.curriculum import LESSONS, GUIDE, CODE_STEPS

def assets():
    return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))/"runtime"

def profile_path():
    return Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"BloomLogic"/"progress.json"

def read_progress():
    try:
        return json.loads(profile_path().read_text()).get("greenhouse_complete") is True
    except (OSError,ValueError,AttributeError):
        return False

def save_progress():
    p=profile_path();p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps({"greenhouse_complete":True}));tmp.replace(p)

def challenge(source):
    # Check actual CPython outputs, including exact threshold.
    return [(n,evaluate(source,Plant(moisture=n)),n<50) for n in (10,35,49,50,80,100)]

def self_test():
    from panda3d.core import Loader, Filename, LoaderOptions, NodePath
    from direct.actor.Actor import Actor
    import gltf
    root=assets();loader=Loader.getGlobalPtr()
    for name in ["bench.egg","drop.egg"]+[f"plant-{f:03}.egg" for f in list(range(1,121,3))+[120]]:
        assert (root/name).is_file(),name
        assert loader.loadSync(Filename.fromOsSpecific(str(root/name)),LoaderOptions()) is not None,name
    teacher=Actor(NodePath(gltf.load_model(str(root/"teacher.glb"))))
    assert "explain" in teacher.getAnimNames()
    teacher.cleanup()
    assert list(root.glob("soil-diff.*"))
    plant=Plant(moisture=42,light=15,temperature=28)
    for _ in range(60):plant=advance(plant,evaluate(DEFAULT_CODE,plant))
    assert plant.growth==1 and plant.health>.9
    assert all(actual==expected for _,actual,expected in challenge(DEFAULT_CODE.replace("40","50")))
    assert not all(actual==expected for _,actual,expected in challenge(DEFAULT_CODE))
    assert len(LESSONS)==14
    return 0

def run():
    from panda3d.core import loadPrcFileData,AmbientLight,DirectionalLight,Vec4,Vec3,TextNode,Filename,NodePath,ClockObject,AntialiasAttrib,WindowProperties
    loadPrcFileData("", "window-title BloomLogic\nwin-size 1280 720\nframebuffer-multisample 1\nmultisamples 4\nsync-video true\nshow-frame-rate-meter false")
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import DirectFrame,DirectLabel,DirectButton,DirectEntry,DirectSlider
    from direct.actor.Actor import Actor
    from direct.task import Task
    import gltf
    app=ShowBase();app.disableMouse()
    app.setBackgroundColor(.66,.73,.66,1)
    dr=app.camNode.getDisplayRegion(0)
    dr.setDimensions(.024,.606,.184,.82)
    app.camLens.setFov(42)
    app.camLens.setAspectRatio(1280*.582/(720*.636))
    app.render.setAntialias(AntialiasAttrib.MMultisample)
    amb=AmbientLight("soft fill");amb.setColor(Vec4(.58,.62,.56,1))
    sun=DirectionalLight("daylight");sun.setColor(Vec4(.72,.70,.63,1))
    al=app.render.attachNewNode(amb);sl=app.render.attachNewNode(sun);sl.setHpr(-35,-55,0)
    app.render.setLight(al);app.render.setLight(sl)
    # Logical 1280 x 720 UI; all hit regions follow the same transform.
    ui=app.pixel2d.attachNewNode("studio")
    def resize(window):
        if window is None:return
        w,h=window.getXSize(),window.getYSize()
        if w and h:
            ui.setScale(w/1280,1,h/720)
            app.camLens.setAspectRatio(w*.582/(h*.636))
    resize(app.win);app.accept("window-event",resize)
    BG=(.956,.949,.913,1);WHITE=(1,.995,.969,1);GREEN=(.12,.29,.22,1)
    INK=(.10,.19,.15,1);MUTED=(.35,.43,.37,1);LINE=(.87,.89,.83,1);GOLD=(.94,.87,.65,1)
    page=None;screen="loading";stage=0;guide_step=0;code_step=0;prediction=None;complete=read_progress()
    state=Plant();source=DEFAULT_CODE;playing=False;water=False;elapsed=0.;visual=0.;shown=-1;last_input=state.moisture
    pace=.34;scene_loaded=False;camera_mode="wide";saved_code=DEFAULT_CODE
    plants=[];drops=[];teacher=None;bench=None;soil=None
    editor=None;status=None;metrics=None;output=None;settings={};guide_text=None;audio=None;voice=True
    def panel(parent,x,y,w,h,color):
        return DirectFrame(parent=parent,pos=(x,0,-y),frameSize=(0,w,-h,0),frameColor=color)
    def label(parent,text,x,y,size=18,color=INK,wrap=None):
        kw=dict(parent=parent,text=text,pos=(x,0,-y),text_scale=size,text_fg=color,text_align=TextNode.ALeft,frameColor=(0,0,0,0))
        if wrap:kw["text_wordwrap"]=wrap
        return DirectLabel(**kw)
    def button(parent,text,x,y,w,h,fn,primary=False,enabled=True):
        b=DirectButton(parent=parent,text=text,pos=(x,0,-y),frameSize=(0,w,-h,0),text_scale=16,text_pos=(w/2,-h/2-5),text_fg=WHITE if primary else INK,frameColor=GREEN if primary else LINE,relief=1,command=fn)
        if not enabled:b["state"]="disabled"
        return b
    def stop_audio():
        nonlocal audio
        if audio:audio.stop();audio=None
    def speak(key):
        nonlocal audio
        stop_audio()
        p=assets()/("voice-"+key+".wav")
        if voice and p.is_file():
            audio=app.loader.loadSfx(str(p));audio.play()
    def clear(mode):
        nonlocal page,screen,playing,water,editor,status,metrics,output,guide_text
        if editor is not None:editor["focus"]=0
        editor=status=metrics=output=guide_text=None
        stop_audio();playing=False;water=False
        if page is not None:page.destroy()
        page=DirectFrame(parent=ui,frameColor=(0,0,0,0),frameSize=(0,1280,-720,0))
        screen=mode
        dr.setActive(mode=="lesson")
        if mode!="lesson":panel(page,0,0,1280,720,BG)
        else:
            panel(page,0,0,1280,126,BG);panel(page,0,588,1280,132,BG)
            panel(page,0,126,30,462,BG);panel(page,776,126,504,462,BG)
        panel(page,0,0,1280,62,WHITE)
        label(page,"BloomLogic",30,39,27,GREEN)
        button(page,"Lessons",936,12,92,38,home)
        button(page,"Settings",1038,12,98,38,show_settings)
        button(page,"Exit",1146,12,102,38,app.userExit)
    def home():
        clear("home")
        label(page,"Explore Python through real life",32,108,32)
        label(page,"Choose an exhibit, follow the explanation, and make code change the world.",34,137,17,MUTED)
        label(page,("1" if complete else "0")+" / 14 lessons completed",1010,108,16,GREEN)
        panel(page,30,155,1220,116,GREEN)
        label(page,"If / Else",50,190,27,WHITE)
        label(page,"Greenhouse controller",50,218,19,WHITE)
        label(page,"Control irrigation, observe seed growth and test both branches.",50,246,16,(.82,.89,.81,1))
        button(page,"Continue lesson" if complete else "Start lesson",1030,191,193,45,open_lesson,primary=False)
        label(page,"Lesson library",32,301,22)
        for i,(title,exhibit,desc) in enumerate(LESSONS):
            x=30+(i%4)*307;y=319+(i//4)*89
            panel(page,x,y,294,79,WHITE)
            panel(page,x,y,5,79,GREEN if i==4 else LINE)
            label(page,title,x+13,y+23,18)
            label(page,exhibit,x+13,y+46,15,MUTED)
            button(page,"Open" if i==4 else "Details",x+212,y+49,70,23,open_lesson if i==4 else lambda i=i:details(i),i==4)
        label(page,"Each lesson has its own real-world exhibit.",32,700,14,MUTED)
    def details(i):
        clear("details")
        title,exhibit,desc=LESSONS[i]
        label(page,title,50,140,36)
        label(page,exhibit,50,180,25,GREEN)
        label(page,desc,50,230,20,MUTED,45)
        label(page,"This exhibit is not yet available.",50,300,18,MUTED)
        button(page,"Back to lessons",50,345,190,44,home,True)
    def show_settings():
        nonlocal voice,pace
        clear("settings")
        label(page,"Settings",40,130,33)
        label(page,"Simulation speed",40,196,22)
        for i,(n,v) in enumerate((("Slow",.7),("Normal",.34),("Fast",.16))):
            def speed(v=v):
                nonlocal pace
                pace=v;show_settings()
            button(page,n,40+i*140,218,128,42,speed,pace==v)
        label(page,"Narration",40,325,22)
        def toggle():
            nonlocal voice
            voice=not voice;show_settings()
        button(page,"Voice on" if voice else "Voice off",40,350,150,42,toggle,voice)
        label(page,"Local progress: "+("Greenhouse completed" if complete else "No lessons completed"),40,448,19)
        button(page,"Return to lessons",40,495,210,44,home,True)
    def load_scene():
        nonlocal bench,soil,teacher,scene_loaded
        if scene_loaded:return
        def model(name):
            n=app.loader.loadModel(Filename.fromOsSpecific(str(assets()/name)))
            if n.isEmpty():raise RuntimeError("Missing asset: "+name)
            n.reparentTo(app.render);return n
        bench=model("bench.egg");soil=bench.find("**/soil_surface")
        if soil.isEmpty():raise RuntimeError("Missing soil mesh")
        teacher=Actor(NodePath(gltf.load_model(str(assets()/"teacher.glb"))))
        teacher.reparentTo(app.render)
        # Table rear edge is y=.45. Teacher stands behind it, not through it.
        teacher.setPos(-.78,.93,-.98);teacher.setH(0);teacher.pose("explain",0)
        for f in list(range(1,121,3))+[120]:
            p=model(f"plant-{f:03}.egg");p.hide();plants.append(p)
        for _ in range(8):
            p=model("drop.egg");p.hide();drops.append(p)
        # Real background environment geometry from the existing floor and bench,
        # no image pretending to be a 3D scene.
        scene_loaded=True
    def open_lesson():
        nonlocal state,visual,shown,stage,guide_step,code_step,prediction,saved_code
        clear("loading");label(page,"Opening the greenhouse...",40,160,30)
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        load_scene()
        state=Plant();visual=0.;shown=-1;guide_step=0;code_step=0;prediction=None;saved_code=DEFAULT_CODE
        show_lesson(0)
    def camera(mode):
        nonlocal camera_mode
        camera_mode=mode
        if mode=="wide":
            teacher.show();teacher.play("explain")
        else:teacher.hide();teacher.stop()
    def set_cam():
        if camera_mode=="wide":
            app.camera.setPos(-.28,-3.55,.50);app.camera.lookAt(-.28,.28,-.08)
        else:
            app.camera.setPos(.10,-1.10,.20);app.camera.lookAt(0,.015,.07)
    def set_message(message):
        if status is not None:status["text"]=message
    def preserve_editor():
        nonlocal saved_code
        if editor is not None and stage==2:saved_code=editor.get()
    def show_lesson(n):
        nonlocal stage,editor,status,metrics,output,settings,guide_text
        preserve_editor();clear("lesson");stage=n
        label(page,"If / Else  |  Greenhouse controller",32,96,24)
        for i,name in enumerate(("Observe","Understand","Experiment","Challenge")):
            button(page,name,630+i*154,73,145,39,lambda i=i:show_lesson(i),n==i)
        panel(page,30,126,746,4,GREEN)
        panel(page,794,132,456,448,WHITE)
        button(page,"Overview",40,542,112,35,lambda:camera("wide"))
        button(page,"Plant close-up",160,542,138,35,lambda:camera("macro"))
        metrics=label(page,"",330,572,15,WHITE)
        panel(page,30,600,1220,100,WHITE)
        label(page,"Dua",48,626,18,GREEN)
        guide_text=label(page,"",48,649,17,INK,88)
        if n==0:
            camera("wide")
            title,body=GUIDE[guide_step]
            label(page,title,814,172,24,INK,28)
            label(page,body,814,221,18,MUTED,38)
            guide_text["text"]=body
            speak("guide"+str(guide_step))
            if guide_step==1:
                def predict(value):
                    nonlocal prediction
                    prediction=value
                    status["text"]="Correct. 20 < 40 is True." if value else "Try again: 20 is below 40."
                button(page,"Water on",814,350,194,44,lambda:predict(True),True)
                button(page,"Water off",1020,350,200,44,lambda:predict(False))
                status=label(page,"Choose a prediction.",814,423,17,GREEN,36)
            def next_guide():
                nonlocal guide_step
                if guide_step==1 and prediction is not True:
                    set_message("Choose the correct prediction first.");return
                if guide_step<2:guide_step+=1;show_lesson(0)
                else:show_lesson(1)
            button(page,"Replay narration",814,483,194,38,lambda:speak("guide"+str(guide_step)))
            button(page,"Next",1020,483,200,38,next_guide,True)
        elif n==1:
            camera("wide")
            label(page,"Read the condition",814,170,24)
            for i,(line,description) in enumerate(CODE_STEPS):
                panel(page,814,190+i*38,415,33,GREEN if i==code_step else LINE)
                label(page,line,825,213+i*38,19,WHITE if i==code_step else INK)
            guide_text["text"]=CODE_STEPS[code_step][1]
            label(page,CODE_STEPS[code_step][1],814,380,18,MUTED,37)
            speak("code"+str(code_step))
            def next_code():
                nonlocal code_step
                if code_step<3:code_step+=1;show_lesson(1)
                else:show_lesson(2)
            def previous_code():
                nonlocal code_step
                code_step=max(0,code_step-1);show_lesson(1)
            button(page,"Previous",814,483,150,40,previous_code,enabled=code_step>0)
            button(page,"Next line" if code_step<3 else "Try it",980,483,240,40,next_code,True)
        else:
            camera("macro")
            label(page,"Write your own rule" if n==2 else "Control the valve",814,168,23)
            label(page,"Python  |  controller.py",814,193,14,MUTED)
            panel(page,810,201,424,137,GREEN)
            editor=DirectEntry(parent=page,initialText=saved_code if n==2 else DEFAULT_CODE,scale=18,pos=(823,0,-225),width=30,numLines=6,frameColor=GREEN,text_fg=WHITE,focus=0)
            if n==2:
                settings={}
                for i,(name,lo,hi,val) in enumerate((("Initial moisture",0,100,state.moisture),("Light hours",0,16,state.light),("Temperature C",0,45,state.temperature))):
                    y=352+i*40;l=label(page,"",814,y+15,15)
                    def change(name=name,l=l):
                        if name in settings:l["text"]=f"{name}: {round(settings[name]['value'])}"
                    s=DirectSlider(parent=page,range=(lo,hi),value=val,pageSize=1,scale=1,pos=(1117,0,-(y+9)),frameSize=(-100,100,-7,7),thumb_frameSize=(-8,8,-10,10),command=change)
                    settings[name]=s;change()
                button(page,"Run",814,485,120,39,start,True)
                button(page,"Pause / Resume",944,485,152,39,toggle_pause)
                button(page,"Reset",1106,485,114,39,reset)
                status=label(page,"Set starting conditions, then Run.",814,552,15,MUTED,44)
                guide_text["text"]="Change the threshold or sensor values. Water on and water off are code decisions; growth depends on the environment."
                speak("experiment")
            else:
                label(page,"Turn water on below 50%, otherwise off.",814,365,17,MUTED,37)
                button(page,"Check six test cases",814,405,405,44,submit,True)
                status=label(page,"Edit the threshold and check your solution.",814,484,16,GREEN,37)
                guide_text["text"]="The boundary matters: at exactly 50%, the else branch must run. The checker tests both branches, not just one example."
                speak("challenge")
    def initial():
        return Plant(moisture=round(settings["Initial moisture"]["value"]),light=round(settings["Light hours"]["value"]),temperature=round(settings["Temperature C"]["value"]))
    def start():
        nonlocal source,state,playing,water,elapsed,visual,saved_code
        candidate=editor.get()
        try:compile_rule(candidate)
        except RuleError as e:set_message("Code error: "+str(e)[:120]);return
        saved_code=source=candidate;state=initial();elapsed=pace;visual=0.;water=False;playing=True
        editor["focus"]=0;camera("macro");set_message("Running. One day every "+str(pace)+" seconds.")
    def toggle_pause():
        nonlocal playing
        if state.day>=60:set_message("Day 60 reached. Run again to restart.");return
        if state.day==0 and not playing:set_message("Press Run to start your rule.");return
        playing=not playing;set_message("Running" if playing else "Paused. Resume continues the same plant.")
    def reset():
        nonlocal state,playing,water,elapsed,visual
        state=initial();playing=False;water=False;elapsed=0;visual=0.
        set_message("Reset to seed. Run to try again.")
    def submit():
        nonlocal complete
        try:result=challenge(editor.get())
        except RuleError as e:set_message("Code error: "+str(e)[:120]);return
        passed=sum(a==b for _,a,b in result)
        if passed==len(result):
            complete=True
            try:save_progress()
            except OSError:set_message("6 / 6 correct. Progress could not be saved.");return
            set_message("6 / 6 correct. Lesson complete!")
            guide_text["text"]="Excellent. Your rule works for dry soil, wet soil, and the exact threshold."
        else:
            n,a,b=next(x for x in result if x[1]!=x[2])
            set_message(f"{passed} / 6 correct. At {n}% expected {'ON' if b else 'OFF'}, got {'ON' if a else 'OFF'}.")
    def tick():
        nonlocal state,water,last_input,playing
        last_input=state.moisture;water=evaluate(source,state);state=advance(state,water)
        if state.day>=60:
            playing=False
            set_message("Finished. Growth "+str(round(state.growth*100))+"%. Run to compare another rule.")
    def update(task):
        nonlocal elapsed,visual,shown
        if screen!="lesson":return Task.cont
        dt=min(.1,ClockObject.getGlobalClock().getDt())
        if playing:
            elapsed+=dt
            if elapsed>=pace:elapsed-=pace;tick()
        visual+=(state.growth-visual)*min(1,dt*7)
        if abs(visual-state.growth)<.001:visual=state.growth
        idx=min(len(plants)-1,round(visual*(len(plants)-1)))
        if idx!=shown:
            for p in plants:p.hide()
            plants[idx].show();shown=idx
        plants[idx].setColorScale(1,.38+.62*state.health,.24+.76*state.health,1)
        wet=state.moisture/100;soil.setColorScale(.85-.35*wet,.81-.35*wet,.76-.36*wet,1)
        for i,p in enumerate(drops):
            if playing and water:
                phase=(task.time*2.6+i/len(drops))%1
                p.setPos((i%3-1)*.004,.035,.36-.302*phase);p.show()
            else:p.hide()
        if metrics is not None:
            metrics["text"]=f"Day {state.day}  |  Soil {state.moisture}%  |  Growth {round(state.growth*100)}%  |  Health {round(state.health*100)}%"
        if stage==2 and state.day:
            guide_text["text"]=f"At {last_input}% moisture, the rule selected water {'ON' if water else 'OFF'}. After the simulated day, soil is {state.moisture}%. Growth {round(state.growth*100)}%. Time is compressed."
        set_cam();return Task.cont
    app.taskMgr.add(update,"lesson-state")
    app.accept("escape",home)
    clear("loading");label(page,"BloomLogic",480,315,44,GREEN);label(page,"Preparing the lesson library",480,355,20,MUTED)
    app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
    home()
    if "--capture" in sys.argv or "--gui-test" in sys.argv:
        out=Path("build/runtime-review");out.mkdir(parents=True,exist_ok=True)
        def capture(name):
            for _ in range(5):app.taskMgr.step();app.graphicsEngine.renderFrame()
            assert app.win.saveScreenshot(Filename.fromOsSpecific(str(out/name)))
        capture("home.png");open_lesson();capture("guide.png")
        guide_step=1;show_lesson(0);capture("prediction.png")
        show_lesson(1);capture("code.png");show_lesson(2)
        settings["Initial moisture"]["value"]=42;settings["Light hours"]["value"]=15;settings["Temperature C"]["value"]=28
        start()
        for _ in range(60):tick()
        assert state.growth==1 and state.health>.9
        visual=1.;capture("grown.png")
        editor.enterText("if moisture < 0:\n    irrigate(True)\nelse:\n    irrigate(False)")
        settings["Initial moisture"]["value"]=20;start()
        for _ in range(60):tick()
        assert state.growth<.1 and state.health==0
        visual=state.growth;capture("dry.png")
        before=state;editor.enterText("import os");start();assert state==before
        show_lesson(3);editor.enterText(DEFAULT_CODE.replace("40","50"))
        assert all(a==b for _,a,b in challenge(editor.get()))
        capture("challenge.png")
        home();capture("return-home.png")
        app.destroy();return
    app.run()

if __name__=="__main__":
    try:
        if "--self-test" in sys.argv:sys.exit(self_test())
        run()
    except Exception:
        message=traceback.format_exc()
        try:
            p=profile_path().with_name("startup-error.txt");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(message)
        except OSError:pass
        if sys.platform=="win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,"BloomLogic could not start. See startup-error.txt in the BloomLogic folder under Local AppData.","BloomLogic",16)
        raise

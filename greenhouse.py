"""BloomLogic native Python learning studio. Blender assets render in Panda3D."""
import sys, json, traceback, os, hashlib, time, faulthandler, tempfile
from pathlib import Path
from codecity.model import Plant, advance, DEFAULT_CODE
from codecity.rules import evaluate, compile_rule, evaluate_compiled, RuleError
from codecity.session import Experiment, challenge, load_profile, write_profile
from codecity.curriculum import LESSONS, GUIDE, CODE_STEPS

def assets():
    return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))/"runtime"

def profile_path():
    return Path(os.environ.get("BLOOMLOGIC_PROFILE_DIR",str(Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"BloomLogic")))/"progress.json"

def milestone(message):
    p=profile_path().with_name("application.log")
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as log:
        log.write(f"{time.monotonic():.3f} {message}\n")
    print(message,flush=True)

def verify_props():
    for name in ("potted_plant_01","planter_pot_clay"):
        folder=assets()/"props"/name
        record=json.loads((folder/"provenance.json").read_text())
        assert record["license"]=="CC0-1.0"
        for path,digest in record["sha256"].items():
            assert hashlib.sha256((folder/"source"/path).read_bytes()).hexdigest()==digest,path

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
    passed,total,failures=challenge(DEFAULT_CODE.replace("40","50"))
    assert passed==total==101*17*46 and not failures
    passed,total,failures=challenge(DEFAULT_CODE)
    assert passed<total and failures
    verify_props()
    assert len(LESSONS)==14
    return 0

def run():
    from panda3d.core import loadPrcFileData,AmbientLight,DirectionalLight,Vec4,Vec3,TextNode,Filename,NodePath,ClockObject,AntialiasAttrib,WindowProperties,CardMaker
    safe="--safe-graphics" in sys.argv
    diagnostic="--headless-gui-test" in sys.argv
    config="window-title BloomLogic\nwin-size 1280 720\nshow-frame-rate-meter false\nsync-video false\n"
    config+=("load-display p3tinydisplay\nframebuffer-multisample 0\nmultisamples 0\n" if safe or diagnostic else "load-display pandagl\naux-display p3tinydisplay\nframebuffer-multisample 1\nmultisamples 4\n")
    if diagnostic:config+="window-type offscreen\naudio-library-name null\n"
    else:config+="audio-library-name p3openal_audio\n"
    loadPrcFileData("",config)
    milestone("before ShowBase; safe="+str(safe)+" headless="+str(diagnostic))
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import DirectFrame,DirectLabel,DirectButton,DirectEntry,DirectSlider
    from direct.actor.Actor import Actor
    from direct.task import Task
    import gltf
    app=ShowBase();milestone("ShowBase created");app.disableMouse()
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
    profile=load_profile(profile_path())
    experiment=Experiment.restore(profile["experiment"]) if profile["experiment"] is not None else Experiment()
    page=None;screen="loading";stage=0;guide_step=0;code_step=0;prediction=None;complete=profile["greenhouse_complete"]
    state=Plant();source=DEFAULT_CODE;playing=False;water=False;elapsed=0.;visual=0.;shown=-1;last_input=state.moisture
    pace=profile["pace"];scene_loaded=False;camera_mode="wide";saved_code=profile["draft"]
    plants=[];drops=[];teacher=None;bench=None;soil=None
    editor=None;status=None;metrics=None;output=None;settings={};guide_text=None;audio=None;voice=profile["voice"]
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
    def persist():
        try:write_profile(profile_path(),dict(greenhouse_complete=complete,voice=voice,pace=pace,experiment=experiment.snapshot(),draft=saved_code))
        except OSError:milestone("Unable to save local progress")
    def preserve_experiment():
        nonlocal saved_code
        if screen=="lesson" and stage==2 and editor is not None:
            saved_code=editor.get()[:2048];experiment.playing=False;persist()
    def quit_app():
        preserve_experiment();persist();app.userExit()
    def clear(mode):
        nonlocal page,screen,playing,water,editor,status,metrics,output,guide_text
        preserve_experiment()
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
        button(page,"Exit",1146,12,102,38,quit_app)
    def home():
        clear("home")
        label(page,"Explore Python through real life",32,108,32)
        label(page,"Choose an exhibit, follow the explanation, and make code change the world.",34,137,17,MUTED)
        label(page,("1" if complete else "0")+" / 14 lessons completed",1010,108,16,GREEN)
        panel(page,30,155,1220,116,GREEN)
        label(page,"If / Else",50,190,27,WHITE)
        label(page,"Greenhouse controller",50,218,19,WHITE)
        label(page,"Control irrigation, observe seed growth and test both branches.",50,246,16,(.82,.89,.81,1))
        button(page,"Resume experiment" if experiment.state.day>0 else "Start lesson",1030,191,193,45,lambda:open_lesson(experiment.state.day>0),primary=False)
        label(page,"Lesson library",32,301,22)
        symbols=(">_","x=","123","+/-","if","for","skip","[ ]","( )","set","key","while","def","Aa")
        for i,(title,exhibit,desc) in enumerate(LESSONS):
            x=30+(i%4)*307;y=319+(i//4)*89
            panel(page,x,y,294,79,(.92,.95,.88,1) if i==4 else WHITE)
            panel(page,x+10,y+12,44,43,GREEN if i==4 else LINE)
            label(page,symbols[i],x+16,y+40,16,WHITE if i==4 else GREEN)
            label(page,title,x+65,y+23,17)
            label(page,exhibit,x+65,y+46,14,MUTED)
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
                pace=v;persist();show_settings()
            button(page,n,40+i*140,218,128,42,speed,pace==v)
        label(page,"Narration",40,325,22)
        def toggle():
            nonlocal voice
            voice=not voice;persist();show_settings()
        button(page,"Voice on" if voice else "Voice off",40,350,150,42,toggle,voice)
        label(page,"Local progress: "+("Greenhouse completed" if complete else "No lessons completed"),40,448,19)
        button(page,"Return to lessons",40,495,210,44,home,True)
    def load_scene():
        nonlocal bench,soil,teacher,scene_loaded
        if scene_loaded:return
        milestone("loading scene")
        def model(name):
            n=app.loader.loadModel(Filename.fromOsSpecific(str(assets()/name)))
            if n.isEmpty():raise RuntimeError("Missing asset: "+name)
            n.reparentTo(app.render);return n
        bench=model("bench.egg");soil=bench.find("**/soil_surface");milestone("bench loaded")
        if soil.isEmpty():raise RuntimeError("Missing soil mesh")
        teacher=Actor(NodePath(gltf.load_model(str(assets()/"teacher.glb"))))
        teacher.reparentTo(app.render);milestone("teacher loaded")
        # Table rear edge is y=.45. Teacher stands behind it, not through it.
        teacher.setPos(-.78,.93,-.98);teacher.setH(0);teacher.pose("explain",0)
        for f in list(range(1,121,3))+[120]:
            p=model(f"plant-{f:03}.egg");p.hide();plants.append(p)
        for _ in range(8):
            p=model("drop.egg");p.hide();drops.append(p)
        milestone("plant samples loaded")
        # A real textured CC0 plant and pot, verified at packaging and placed on floor.
        verify_props()
        for name,pos,scale in (("potted_plant_01",(1.05,1.65,-.98),.88),("potted_plant_01",(-1.48,1.85,-.98),.75),("planter_pot_clay",(.95,.85,-.98),1.1)):
            folder=assets()/"props"/name
            record=json.loads((folder/"provenance.json").read_text())
            prop=NodePath(gltf.load_model(str(folder/"source"/record["entry"])))
            prop.reparentTo(app.render);prop.setPos(*pos);prop.setScale(scale)
        # Glazing and mullions at a distance behind the actual exhibits.
        def wall_card(name,x,z,w,h,col,y=2.8):
            cm=CardMaker(name);cm.setFrame(0,w,0,h)
            node=app.render.attachNewNode(cm.generate());node.setPos(x,y,z)
            node.setColor(*col);node.setLightOff();node.setTwoSided(True);return node
        wall_card("daylit backdrop",-4,-.98,8,3.4,(.66,.79,.70,1))
        wall_card("lower wall",-4,-.98,8,.44,(.57,.65,.58,1),2.78)
        for x in (-3,-1.8,-.6,.6,1.8,3):
            wall_card("greenhouse mullion",x,-.54,.048,2.96,(.28,.39,.33,1),2.76)
        for z in (-.54,.52,1.62,2.4):
            wall_card("horizontal rail",-4,z,8,.042,(.28,.39,.33,1),2.75)
        scene_loaded=True;milestone("scene ready")
    def open_lesson(resume=False):
        nonlocal state,visual,shown,stage,guide_step,code_step,prediction,saved_code
        clear("loading");label(page,"Opening the greenhouse...",40,160,30)
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        load_scene()
        state=Plant();visual=0.;shown=-1;guide_step=0;code_step=0;prediction=None
        show_lesson(2 if resume else 0)
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
    def show_lesson(n):
        nonlocal stage,editor,status,metrics,output,settings,guide_text,state,source,playing,water,elapsed,visual
        clear("lesson");stage=n
        if n==2:
            state=experiment.state;source=experiment.source;water=experiment.water;visual=state.growth;elapsed=0
        elif n==0:
            state=Plant(moisture=20 if guide_step in (1,2) else 55);visual=state.growth
        elif n==3:
            state=Plant();visual=0;water=False
        label(page,"If / Else  |  Greenhouse controller",32,96,24)
        for i,name in enumerate(("Observe","Understand","Experiment","Challenge")):
            button(page,name,630+i*154,73,145,39,lambda i=i:show_lesson(i),n==i)
        panel(page,30,126,746,4,GREEN)
        panel(page,794,132,456,448,WHITE)
        button(page,"Overview",40,542,112,35,lambda:camera("wide"))
        button(page,"Plant close-up",160,542,138,35,lambda:camera("macro"))
        panel(page,310,542,458,35,GREEN)
        metrics=label(page,"",320,564,14,WHITE)
        panel(page,30,600,1220,100,WHITE)
        label(page,"Dua",48,626,18,GREEN)
        guide_text=label(page,"",48,649,17,INK,66)
        if n==0:
            camera("wide")
            title,body=GUIDE[guide_step]
            label(page,title,814,172,24,INK,17)
            label(page,body,814,221,18,MUTED,22)
            guide_text["text"]=body
            speak("guide"+str(guide_step))
            if guide_step==2:
                state=Plant(moisture=20);source=DEFAULT_CODE;visual=0;elapsed=pace;playing=True;water=False
                camera("macro")
            if guide_step==1:
                def predict(value):
                    nonlocal prediction
                    prediction=value
                    status["text"]="Correct. 20 < 40 is True." if value else "Try again: 20 is below 40."
                button(page,"Water on",814,350,194,44,lambda:predict(True),True)
                button(page,"Water off",1020,350,200,44,lambda:predict(False))
                status=label(page,"Choose a prediction.",814,423,17,GREEN,23)
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
            label(page,CODE_STEPS[code_step][1],814,380,18,MUTED,22)
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
            editor=DirectEntry(parent=page,initialText=saved_code if n==2 else DEFAULT_CODE,scale=17,pos=(823,0,-225),width=23,numLines=6,frameColor=GREEN,text_fg=WHITE,focus=0,command=lambda _:insert_code("\n"))
            button(page,"Clear",1046,175,82,24,lambda:clear_editor(True))
            button(page,"Example",1136,175,92,24,restore_example)
            if n==2:
                settings={}
                for i,(name,lo,hi,val) in enumerate((("Initial moisture",0,100,experiment.initial.moisture),("Light hours",0,16,experiment.initial.light),("Temperature C",0,45,experiment.initial.temperature))):
                    y=352+i*40;l=label(page,"",814,y+15,15)
                    def change(name=name,l=l):
                        if name in settings:l["text"]=f"{name}: {round(settings[name]['value'])}"
                    s=DirectSlider(parent=page,range=(lo,hi),value=val,pageSize=1,scale=1,pos=(1117,0,-(y+9)),frameSize=(-100,100,-7,7),thumb_frameSize=(-8,8,-10,10),command=change)
                    settings[name]=s;change()
                button(page,"Run",814,485,120,39,start,True)
                button(page,"Pause / Resume",944,485,152,39,toggle_pause)
                button(page,"Reset",1106,485,114,39,reset)
                status=label(page,"Saved experiment paused. Resume or Run again." if state.day and state.day<60 else "Set starting conditions, then Run.",814,552,15,MUTED,27)
                guide_text["text"]="Change the threshold or sensor values. Water on and water off are code decisions; growth depends on the environment."
                speak("experiment")
            else:
                label(page,"Turn water on below 50%, otherwise off.",814,365,17,MUTED,23)
                button(page,"Check all sensor combinations",814,405,405,44,submit,True)
                status=label(page,"Edit the threshold and check your solution.",814,484,16,GREEN,25)
                guide_text["text"]="The boundary matters: at exactly 50%, the else branch must run. The checker tests every supported moisture, light and temperature combination."
                speak("challenge")
        if "--input-test" in sys.argv:milestone("lesson stage ready "+str(n))
    def insert_code(value):
        if editor is None:return
        text=editor.get();pos=editor.getCursorPosition()
        if value=="\n":
            line=text[:pos].rsplit("\n",1)[-1]
            indent=len(line)-len(line.lstrip(" "))
            value+=" "*(indent+(4 if line.rstrip().endswith(":") else 0))
        if len(text)+len(value)>2048:return
        editor.enterText(text[:pos]+value+text[pos:]);editor.setCursorPosition(pos+len(value));editor["focus"]=1
    def initial():
        return Plant(moisture=round(settings["Initial moisture"]["value"]),light=round(settings["Light hours"]["value"]),temperature=round(settings["Temperature C"]["value"]))
    def start():
        nonlocal source,state,playing,water,elapsed,visual,saved_code
        candidate=editor.get()
        if "--input-test" in sys.argv:milestone("Run clicked, input="+repr(candidate))
        try:experiment.start(candidate,initial())
        except RuleError as e:
            playing=False;experiment.playing=False;persist()
            if "--input-test" in sys.argv:milestone("Rule rejected "+str(e))
            set_message("Code error: "+str(e)[:85]);return
        saved_code=source=experiment.source;state=experiment.state;elapsed=pace;visual=0.;water=False;playing=True;persist()
        editor["focus"]=0;camera("macro");set_message("Running. One day every "+str(pace)+" seconds.")
    def toggle_pause():
        nonlocal playing
        if state.day>=60:set_message("Day 60 reached. Run again to restart.");return
        if state.day==0 and not playing:set_message("Press Run to start your rule.");return
        playing=not playing;experiment.playing=playing;persist();set_message("Running" if playing else "Paused. Resume continues the same plant.")
    def reset():
        nonlocal state,playing,water,elapsed,visual
        experiment.reset(initial());state=experiment.state;playing=False;water=False;elapsed=0;visual=0.;persist()
        set_message("Reset to seed. Run to try again.")
    def submit():
        nonlocal complete,state,source,visual,elapsed,playing,water
        try:passed,total,failures=challenge(editor.get())
        except RuleError as e:set_message("Code error: "+str(e)[:85]);return
        source=editor.get()
        if failures:
            n,l,t,a,b=failures[0];state=Plant(moisture=n,light=l,temperature=t)
            set_message(f"{passed}/{total} correct. Soil {n}%, light {l}h, {t} C: expected {'ON' if b else 'OFF'}, got {'ON' if a else 'OFF'}.")
        else:
            state=Plant(moisture=20);complete=True;persist()
            set_message(f"{total}/{total} correct. Lesson complete!")
            guide_text["text"]="Your rule works for every supported sensor combination, including the exact boundary."
        visual=0;elapsed=pace;playing=True;water=False;camera("macro")
    def tick():
        nonlocal state,water,last_input,playing
        if stage==2:
            if not experiment.step():playing=False;return
            state=experiment.state;water=experiment.water;last_input=experiment.last_input;playing=experiment.playing
            if state.day%5==0 or not playing:persist()
        else:
            last_input=state.moisture;water=evaluate(source,state);state=advance(state,water)
        if state.day>=60 or (stage==0 and state.day>=24):
            playing=False
            if stage==2:set_message("Finished. Growth "+str(round(state.growth*100))+"%. Run to compare another rule.")
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
            last_input=experiment.last_input
            guide_text["text"]=f"At {last_input}% moisture, the rule selected water {'ON' if water else 'OFF'}. After the simulated day, soil is {state.moisture}%. Growth {round(state.growth*100)}%. Time is compressed."
        set_cam();return Task.cont
    app.taskMgr.add(update,"lesson-state")
    app.accept("escape",home)
    app.accept("tab",lambda:insert_code("    ") if editor is not None and editor["focus"] else None)
    def clear_editor(force=False):
        if editor is not None and (force or editor["focus"]):
            editor.enterText("");editor.setCursorPosition(0);editor["focus"]=1
            if "--input-test" in sys.argv:milestone("editor cleared")
    def restore_example():
        if editor is not None:editor.enterText(DEFAULT_CODE);editor.setCursorPosition(len(DEFAULT_CODE));editor["focus"]=1
    app.accept("control-shift-backspace",clear_editor)
    app.accept("shift-control-backspace",clear_editor)
    clear("loading");label(page,"BloomLogic",480,315,44,GREEN);label(page,"Preparing the lesson library",480,355,20,MUTED)
    app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
    home();milestone("home ready")
    if any(x in sys.argv for x in ("--capture","--gui-test","--headless-gui-test")):
        out=Path(os.environ.get("BLOOMLOGIC_CAPTURE_DIR","build/runtime-review"));out.mkdir(parents=True,exist_ok=True)
        def capture(name):
            for _ in range(5):app.taskMgr.step();app.graphicsEngine.renderFrame()
            assert app.win.saveScreenshot(Filename.fromOsSpecific(str(out/name)))
            milestone("captured "+name)
        capture("home.png");open_lesson();teacher.pose("explain",int(teacher.getNumFrames("explain")*.5));capture("guide.png")
        guide_step=1;show_lesson(0);capture("prediction.png")
        guide_step=2;show_lesson(0)
        for _ in range(24):tick()
        assert state.growth==1
        visual=1;capture("guided-growth.png")
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
        passed,total,failures=challenge(editor.get());assert passed==total and not failures
        submit();assert complete
        capture("challenge.png")
        home();capture("return-home.png")
        milestone("GUI assertions passed");app.destroy();milestone("GUI shutdown complete");return
    if "--input-test" in sys.argv:
        def watch_input(task):
            if screen=="lesson" and stage==2 and state.day>=10:
                assert experiment.source==DEFAULT_CODE.replace("40","50"),repr(experiment.source)
                milestone("OS input test passed");app.destroy();sys.exit(0)
            if task.time>75:raise RuntimeError(f"OS input test timed out: screen={screen}, stage={stage}, day={state.day}, input={editor.get() if editor is not None else None!r}")
            return Task.cont
        app.taskMgr.add(watch_input,"input-test")
    app.run()

if __name__=="__main__":
    # Separate automated profiles from actual student progress.
    if any(x in sys.argv for x in ("--capture","--gui-test","--headless-gui-test","--input-test","--self-test")) and "BLOOMLOGIC_PROFILE_DIR" not in os.environ:
        os.environ["BLOOMLOGIC_PROFILE_DIR"]=tempfile.mkdtemp(prefix="bloomlogic-test-")
    # Windowed PyInstaller has no console; redirect diagnostics to a local file.
    if sys.stdout is None or sys.stderr is None:
        log=profile_path().with_name("application.log")
        log.parent.mkdir(parents=True,exist_ok=True)
        stream=log.open("a",encoding="utf-8",buffering=1)
        if sys.stdout is None:sys.stdout=stream
        if sys.stderr is None:sys.stderr=stream
    diagnostics=profile_path().with_name("traceback.log")
    diagnostics.parent.mkdir(parents=True,exist_ok=True)
    with diagnostics.open("a",encoding="utf-8") as trace:
        faulthandler.enable(file=trace)
        if any(x in sys.argv for x in ("--gui-test","--headless-gui-test","--capture","--input-test")):
            faulthandler.dump_traceback_later(45,repeat=True,file=trace)
        try:
            milestone("entrypoint")
            if "--self-test" in sys.argv:sys.exit(self_test())
            run()
        except Exception:
            message=traceback.format_exc()
            try:profile_path().with_name("startup-error.txt").write_text(message,encoding="utf-8")
            except OSError:pass
            if sys.platform=="win32" and len(sys.argv)==1:
                import ctypes
                ctypes.windll.user32.MessageBoxW(None,"BloomLogic could not start. See startup-error.txt in Local AppData/BloomLogic.","BloomLogic",16)
            raise
        finally:
            faulthandler.cancel_dump_traceback_later();faulthandler.disable()

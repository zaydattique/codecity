"""BloomLogic native Python learning studio. Blender assets render in Panda3D."""
import sys, json, traceback, os, hashlib, time, faulthandler, tempfile
from pathlib import Path
from codecity.model import Plant, advance, DEFAULT_CODE
from codecity.rules import evaluate, compile_rule, evaluate_compiled, RuleError, trace_rule
from codecity.session import Experiment, challenge, load_profile, write_profile
from codecity.curriculum import LESSONS, GUIDE, CODE_STEPS, CONCEPTS, EXAMPLES
from codecity.lesson import comparison, trace_day, DRY_RULE, WET_RULE, FAN_START, FAN_EXAMPLE, fan_check, STOP_AFTER_GROWTH, stop_after_growth

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
    for name in ["bench.egg","rhizobox.egg","architecture.egg","drop.egg"]+[f"plant-{f:03}.egg" for f in list(range(1,121,3))+[120]]:
        assert (root/name).is_file(),name
        assert loader.loadSync(Filename.fromOsSpecific(str(root/name)),LoaderOptions()) is not None,name
    teacher=Actor(NodePath(gltf.load_model(str(root/"teacher.glb"))))
    assert "explain" in teacher.getAnimNames()
    teacher.cleanup()
    for name in ("fan-housing.glb","fan-rotor.glb"):
        assert not NodePath(gltf.load_model(str(root/name))).isEmpty(),name
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
    benchmark="--benchmark" in sys.argv
    resolution=(1920,1080) if "--1080p" in sys.argv else (1280,720)
    config=f"window-title BloomLogic\nwin-size {resolution[0]} {resolution[1]}\nshow-frame-rate-meter false\nsync-video false\n"
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
    boot_start=time.perf_counter()
    app=ShowBase();milestone("ShowBase created");app.disableMouse()
    app.setBackgroundColor(.66,.73,.66,1)
    dr=app.camNode.getDisplayRegion(0)
    dr.setDimensions(.024,.606,.184,.82)
    app.camLens.setFov(42)
    app.camLens.setAspectRatio(1280*.582/(720*.636))
    app.render.setAntialias(AntialiasAttrib.MMultisample)
    amb=AmbientLight("soft fill");amb.setColor(Vec4(.49,.52,.47,1))
    sun=DirectionalLight("daylight");sun.setColor(Vec4(.76,.74,.65,1))
    al=app.render.attachNewNode(amb);sl=app.render.attachNewNode(sun);sl.setHpr(-35,-55,0)
    app.render.setLight(al);app.render.setLight(sl)
    # Shader generator enables contact shadows on normal OpenGL; safe mode stays fixed-function.
    advanced=not (safe or diagnostic) and app.win.getGsg().getSupportsBasicShaders()
    if advanced:
        sun.setShadowCaster(True,1024,1024)
        sun.getLens().setFilmSize(6,6);sun.getLens().setNearFar(3,11)
        # Preserve default back-face shadow state, add modest depth bias.
        from panda3d.core import RenderState,DepthOffsetAttrib
        sun.setInitialState(sun.getInitialState().compose(RenderState.make(DepthOffsetAttrib.make(-2))))
        sl.setPos(-3,-4,6);sl.lookAt(0,.7,-.2)
        app.render.setShaderAuto()
    milestone("advanced lighting "+str(advanced))
    # Logical 1280 x 720 UI; all hit regions follow the same transform.
    ui=app.pixel2d.attachNewNode("studio")
    def resize(window):
        if window is None:return
        w,h=window.getXSize(),window.getYSize()
        if w and h:
            ui.setScale(w/1280,1,h/720)
            app.camLens.setAspectRatio(w*.582/(h*.636))
    resize(app.win);app.accept("window-event",resize)
    BG=(.934,.939,.918,1);WHITE=(.995,.995,.978,1);GREEN=(.08,.25,.19,1)
    INK=(.075,.15,.12,1);MUTED=(.31,.39,.33,1);LINE=(.87,.90,.85,1);GOLD=(.94,.87,.65,1)
    from panda3d.core import TextNode,TextProperties,TextPropertiesManager
    # Existing Panda font is kept to avoid new unlicensed font assets.
    profile=load_profile(profile_path())
    experiment=Experiment.restore(profile["experiment"]) if profile["experiment"] is not None else Experiment()
    page=None;screen="loading";stage=0;guide_step=0;code_step=0;prediction=None;complete=profile["greenhouse_complete"]
    state=Plant();source=DEFAULT_CODE;playing=False;water=False;elapsed=0.;visual=0.;shown=-1;last_input=state.moisture
    pace=profile["pace"];scene_loaded=False;camera_mode="wide";saved_code=profile["draft"]
    plants=[];drops=[];teacher=None;bench=None;soil=None;box_model=None
    leaf_nodes={};camera_position=None;camera_focus=None;teacher_frame=0.;teacher_visible=False;teacher_gesture=False
    impact=None;water_sound=None
    greenhouse_root=app.render.attachNewNode("greenhouse-exhibit")
    compare_root=app.render.attachNewNode("comparison-exhibit");compare_root.hide()
    fan_root=app.render.attachNewNode("fan-exhibit");fan_root.hide()
    compare_meshes=[];fan_rotor=None;fan_status=None;fan_temp=28;fan_on=False;fan_source=FAN_START;fan_run=None;fan_slider=None
    comparison_day=60;reference=DRY_RULE;compare_labels=[];timeline=None;target_day_label=None
    active_trace=None;trace_key=None;trace_label=None;concept_index=-1;demo_moisture=20;concept_text=None;code_labels=[];prediction_result=None
    editor=None;status=None;metrics=None;output=None;settings={};guide_text=None;audio=None;voice=profile["voice"]
    def panel(parent,x,y,w,h,color):
        return DirectFrame(parent=parent,pos=(x,0,-y),frameSize=(0,w,-h,0),frameColor=color)
    def label(parent,text,x,y,size=18,color=INK,wrap=None):
        kw=dict(parent=parent,text=text,pos=(x,0,-y),text_scale=size,text_fg=color,text_align=TextNode.ALeft,frameColor=(0,0,0,0))
        if wrap:kw["text_wordwrap"]=wrap
        return DirectLabel(**kw)
    button_textures={}
    def rounded_mask(w,h):
        key=(w,h)
        if key in button_textures:return button_textures[key]
        from panda3d.core import PNMImage,Texture
        import math
        iw,ih=max(8,int(w)),max(8,int(h));radius=min(7,ih/3)
        image=PNMImage(iw,ih,4);image.fill(1);image.alphaFill(0)
        for y in range(ih):
            for x in range(iw):
                dx=max(radius-x-.5,0,x+.5-(iw-radius));dy=max(radius-y-.5,0,y+.5-(ih-radius))
                alpha=max(0,min(1,radius+.5-math.hypot(dx,dy)))
                image.setAlpha(x,y,alpha)
        texture=Texture("rounded-button");texture.load(image);button_textures[key]=texture;return texture
    def button(parent,text,x,y,w,h,fn,primary=False,enabled=True):
        b=DirectButton(parent=parent,text=text,pos=(x,0,-y),frameSize=(0,w,-h,0),text_scale=16,text_pos=(w/2,-h/2-5),text_fg=WHITE if primary else INK,frameColor=GREEN if primary else LINE,relief=1,command=fn)
        from panda3d.core import TransparencyAttrib
        b["frameTexture"]=rounded_mask(w,h);b.setTransparency(TransparencyAttrib.MAlpha)
        if not enabled:b["state"]="disabled";b["text_fg"]=MUTED
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
    def save_on_exit():
        preserve_experiment();persist()
    app.exitFunc=save_on_exit
    def quit_app():
        app.userExit()
    def clear(mode):
        nonlocal page,screen,playing,water,editor,status,metrics,output,guide_text,timeline,trace_label,trace_key,fan_status,target_day_label
        preserve_experiment()
        if editor is not None:editor["focus"]=0
        editor=status=metrics=output=guide_text=timeline=trace_label=fan_status=target_day_label=None;trace_key=None
        stop_audio();playing=False;water=False
        if water_sound is not None:water_sound.stop()
        if page is not None:page.destroy()
        page=DirectFrame(parent=ui,frameColor=(0,0,0,0),frameSize=(0,1280,-720,0))
        screen=mode
        dr.setActive(mode in ("lesson","compare","fan"))
        greenhouse_root.show() if mode=="lesson" else greenhouse_root.hide()
        compare_root.show() if mode=="compare" else compare_root.hide()
        fan_root.show() if mode=="fan" else fan_root.hide()
        if mode not in ("lesson","compare","fan"):panel(page,0,0,1280,720,BG)
        else:
            panel(page,0,0,1280,126,BG);panel(page,0,588,1280,132,BG)
            panel(page,0,126,30,462,BG);panel(page,776,126,504,462,BG)
        panel(page,0,0,1280,62,WHITE)
        panel(page,0,61,1280,1,LINE)
        panel(page,30,19,4,25,GREEN)
        label(page,"BloomLogic",44,39,27,GREEN)
        button(page,"Lessons",936,12,92,38,home)
        button(page,"Settings",1038,12,98,38,show_settings)
        button(page,"Exit",1146,12,102,38,quit_app)
    def home():
        clear("home")
        label(page,"Explore Python through real life",32,108,32)
        label(page,"Choose an exhibit, follow the explanation, and make code change the world.",34,137,17,MUTED)
        label(page,("1" if complete else "0")+" / 14 lessons completed",1010,108,16,GREEN)
        panel(page,30,155,1220,116,GREEN)
        panel(page,30,155,6,116,(.66,.80,.49,1))
        label(page,"If / Else",50,190,27,WHITE)
        label(page,"Greenhouse controller",50,218,19,WHITE)
        label(page,"Control irrigation, observe seed growth and test both branches.",50,246,16,(.82,.89,.81,1))
        button(page,"Resume experiment" if experiment.state.day>0 else "Start lesson",1030,191,193,45,lambda:open_lesson(experiment.state.day>0),primary=False)
        label(page,"Lesson library",32,301,22)
        symbols=(">_","x=","123","+/-","if","for","skip","[ ]","( )","set","key","while","def","Aa")
        for i,(title,exhibit,desc) in enumerate(LESSONS):
            x=30+(i%4)*307;y=319+(i//4)*89
            panel(page,x+2,y+3,294,79,(.84,.87,.81,1))
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
        nonlocal bench,soil,teacher,scene_loaded,box_model,impact,water_sound
        if scene_loaded:return
        milestone("loading scene")
        def model(name):
            n=app.loader.loadModel(Filename.fromOsSpecific(str(assets()/name)))
            if n.isEmpty():raise RuntimeError("Missing asset: "+name)
            n.reparentTo(greenhouse_root);return n
        bench=model("bench.egg");box_model=model("rhizobox.egg");soil=box_model.find("**/soil_surface");model("architecture.egg");milestone("bench loaded")
        if soil.isEmpty():raise RuntimeError("Missing soil mesh")
        # Thin and beveled surfaces need a small receive-side depth offset.
        bench.setDepthOffset(1);soil.setDepthOffset(1)
        if advanced:
            from panda3d.core import TextureStage,Texture
            # Normal and gloss maps use the exact same UV as the diffuse map.
            # Roughness is not a gloss map; convert it during the build.
            normal=TextureStage("soil-normal");normal.setMode(TextureStage.MNormal)
            gloss=TextureStage("soil-gloss");gloss.setMode(TextureStage.MGloss)
            soil.setTexture(normal,app.loader.loadTexture(str(next(assets().glob("soil-nor_gl.*")))),1)
            soil.setTexture(gloss,app.loader.loadTexture(str(assets()/"soil-gloss.png")),1)
            from panda3d.core import Material
            mat=Material("Substrate");mat.setShininess(12);mat.setSpecular((.15,.14,.12,1));soil.setMaterial(mat)
        teacher=Actor(NodePath(gltf.load_model(str(assets()/"teacher.glb"))))
        teacher.reparentTo(greenhouse_root);milestone("teacher loaded")
        # Table rear edge is y=.45. Teacher stands behind it, not through it.
        teacher.setPos(-.90,1.0,-.98);teacher.setH(-7);teacher.pose("explain",0)
        for f in list(range(1,121,3))+[120]:
            p=model(f"plant-{f:03}.egg");p.setDepthOffset(1);p.hide();plants.append(p)
            leaf_nodes[id(p)]=list(p.findAllMatches("**/leaf_*"))
        for _ in range(18):
            p=model("drop.egg");p.hide();drops.append(p)
        milestone("plant samples loaded")
        # A real textured CC0 plant and pot, verified at packaging and placed on floor.
        verify_props()
        for name,pos,scale in (("potted_plant_01",(1.05,1.65,-.98),.88),("potted_plant_01",(-1.48,1.85,-.98),.75),("planter_pot_clay",(.95,.85,-.98),1.1)):
            folder=assets()/"props"/name
            record=json.loads((folder/"provenance.json").read_text())
            prop=NodePath(gltf.load_model(str(folder/"source"/record["entry"])))
            prop.reparentTo(greenhouse_root);prop.setPos(*pos);prop.setScale(scale)
        # Original shallow splash rings sit exactly on substrate surface.
        from panda3d.core import LineSegs
        impact=greenhouse_root.attachNewNode("water-contact")
        import math
        for radius in (.012,.024):
            ring=LineSegs("contact ripple");ring.setThickness(1.5);ring.setColor(.58,.78,.79,1)
            for i in range(33):
                a=i*2*math.pi/32;p=(radius*math.cos(a),.035+radius*math.sin(a),.060)
                if i==0:ring.moveTo(*p)
                else:ring.drawTo(*p)
            impact.attachNewNode(ring.create())
        impact.hide()
        water_sound=app.loader.loadSfx(str(assets()/"water-contact.wav"));water_sound.setLoop(True);water_sound.setVolume(.15)
        scene_loaded=True;milestone("scene ready")
    def open_lesson(resume=False):
        nonlocal state,visual,shown,stage,guide_step,code_step,prediction,saved_code,concept_index,demo_moisture
        clear("loading");label(page,"Opening the greenhouse...",40,160,30)
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        load_scene()
        state=Plant();visual=0.;shown=-1;guide_step=0;code_step=0;prediction=None;concept_index=-1;demo_moisture=20
        show_lesson(2 if resume else 0)
    def camera(mode):
        nonlocal camera_mode,teacher_visible,teacher_gesture,teacher_frame
        camera_mode=mode;teacher_visible=mode=="wide"
        teacher.show() if teacher_visible else teacher.hide()
        teacher.stop();teacher_frame=0.;teacher_gesture=teacher_visible
    def set_cam():
        nonlocal camera_position,camera_focus
        if camera_mode=="wide":
            pos=Vec3(-.35,-3.75,.62);focus=Vec3(-.30,.30,-.05)
        else:
            pos=Vec3(.12,-1.16,.22);focus=Vec3(0,.015,.07)
        if camera_position is None or "--capture" in sys.argv or "--gui-test" in sys.argv:
            camera_position=pos;camera_focus=focus
        else:
            blend=min(1,ClockObject.getGlobalClock().getDt()*7)
            camera_position+=(pos-camera_position)*blend;camera_focus+=(focus-camera_focus)*blend
        app.camera.setPos(camera_position);app.camera.lookAt(camera_focus)
    def set_message(message):
        if status is not None:status["text"]=message
    def show_lesson(n):
        nonlocal stage,camera_position,camera_focus,editor,status,metrics,output,settings,guide_text,state,source,playing,water,elapsed,visual,timeline,trace_label,active_trace,target_day_label,concept_text,code_labels,demo_moisture,prediction_result
        clear("lesson");stage=n;active_trace=None;prediction_result=None;code_labels=[];camera_position=None;camera_focus=None
        if n==2:
            state=experiment.state;source=experiment.source;water=experiment.water;visual=state.growth;elapsed=0
        elif n==0:
            state=Plant(moisture=20 if guide_step in (1,3) else 60 if guide_step==2 else 55);visual=state.growth
        elif n==1:
            state=Plant(moisture=demo_moisture);visual=0;water=False
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
            if guide_step==3:
                state=Plant(moisture=20);source=DEFAULT_CODE;visual=0;elapsed=pace;playing=True;water=False
                camera("macro")
            if guide_step in (1,2):
                def predict(value):
                    nonlocal prediction,state,source,playing,water,elapsed,visual,prediction_result
                    initial_m=20 if guide_step==1 else 60
                    prediction=value
                    expected=trace_rule(DEFAULT_CODE,Plant(moisture=initial_m)).action
                    prediction_result="Correct" if value==expected else "Not quite"
                    state=Plant(moisture=initial_m);visual=0;elapsed=pace
                    source=WET_RULE if value else DRY_RULE;playing=True;water=False
                    camera("macro")
                    set_message(f"{prediction_result}. {initial_m} < 40 is {'True' if expected else 'False'}. Watch your choice.")
                    guide_text["text"]=f"Your choice: water {'ON' if value else 'OFF'}. Correct rule: water {'ON' if expected else 'OFF'}. The chosen action is simulated for six days."
                def correct_demo():
                    nonlocal state,source,playing,water,elapsed,visual
                    state=Plant(moisture=20 if guide_step==1 else 60);source=DEFAULT_CODE;visual=0;elapsed=pace;playing=True;water=False
                    camera("macro");set_message("Running the correct rule for six days.")
                    guide_text["text"]="The correct controller rechecks the current moisture every day. Compare this result with your prediction."
                button(page,"Water on",814,350,194,44,lambda:predict(True),True)
                button(page,"Water off",1020,350,200,44,lambda:predict(False))
                status=label(page,"Choose a prediction.",814,423,17,GREEN,23)
                button(page,"Try correct rule",814,443,194,32,correct_demo)
            def next_guide():
                nonlocal guide_step
                if guide_step<len(GUIDE)-1:guide_step+=1;show_lesson(0)
                else:show_lesson(1)
            def previous_guide():
                nonlocal guide_step
                guide_step=max(0,guide_step-1);show_lesson(0)
            button(page,"Replay voice",814,483,132,38,lambda:speak("guide"+str(guide_step)))
            button(page,"Back",954,483,90,38,previous_guide,enabled=guide_step>0)
            button(page,"Next",1052,483,168,38,next_guide,True)
        elif n==1:
            camera("macro")
            label(page,"Read and test the code",814,165,24)
            example=DEFAULT_CODE if concept_index<0 else EXAMPLES[concept_index]
            for i,line in enumerate(example.splitlines()):
                bg=panel(page,814,181+i*25,415,24,LINE)
                lbl=label(page,f"{i+1:2}  {line}",821,198+i*25,14)
                code_labels.append((bg,lbl))
            concept_text=label(page,"",814,360,16,MUTED,26)
            status=label(page,"",814,438,16,GREEN,26)
            def inspect_sensor(value):
                nonlocal demo_moisture,state,water,active_trace
                demo_moisture=value;state=Plant(moisture=value)
                active_trace=trace_rule(example,state)
                water=active_trace.action
                for i,(bg,lbl) in enumerate(code_labels,1):
                    active=i==active_trace.action_line
                    checked=any(l==i for l,_ in active_trace.conditions)
                    bg["frameColor"]=GREEN if active else GOLD if checked else LINE
                    lbl["text_fg"]=WHITE if active else INK
                status["text"]=" / ".join(f"Line {l}: {v}" for l,v in active_trace.conditions)+"; valve "+("ON" if water else "OFF")
                guide_text["text"]=f"Sensor {value}%. Executed action on line {active_trace.action_line}. The other action is skipped. This is one code check, not a simulated day."
            for i,v in enumerate((20,39,40,60)):
                button(page,f"{v}%",814+i*104,461,96,32,lambda v=v:inspect_sensor(v))
            def next_concept():
                nonlocal concept_index,code_step
                if concept_index<0 and code_step<3:code_step+=1
                else:concept_index+=1
                if concept_index>=len(CONCEPTS):
                    concept_index=len(CONCEPTS)-1;show_lesson(2)
                else:show_lesson(1)
            def previous_concept():
                nonlocal concept_index,code_step
                if concept_index>=0:concept_index-=1
                else:code_step=max(0,code_step-1)
                show_lesson(1)
            concept_text["text"]=CODE_STEPS[code_step][1] if concept_index<0 else CONCEPTS[concept_index][0]+": "+CONCEPTS[concept_index][1]
            speak("code"+str(code_step) if concept_index<0 else "concept"+str(concept_index))
            button(page,"Previous",814,510,126,38,previous_concept,enabled=code_step>0 or concept_index>=0)
            button(page,"Next concept" if concept_index<len(CONCEPTS)-1 else "Try it",950,510,270,38,next_concept,True)
            inspect_sensor(demo_moisture)
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
                guide_text["text"]="Run the rule, inspect executed lines and scrub to any simulated day."
                # Timeline uses exact deterministic state, not a decorative progress bar.
                panel(page,30,600,1220,100,WHITE)
                target_day_label=label(page,"Go to day "+str(state.day),48,625,15,GREEN)
                timeline=DirectSlider(parent=page,range=(0,60),value=state.day,pageSize=1,scale=1,pos=(350,0,-620),frameSize=(-180,180,-6,6),thumb_frameSize=(-7,7,-9,9))
                button(page,"Seek",550,605,90,30,seek_day,True)
                button(page,"Step",650,605,90,30,step_day)
                button(page,"Compare",750,605,125,30,show_comparison)
                button(page,"Restart",885,605,110,30,lambda:seek_day(0))
                trace_label=label(page,"",48,650,15,INK,94)
                guide_text.hide()
                speak("experiment")
            else:
                label(page,"Turn water on below 50%, otherwise off.",814,365,17,MUTED,23)
                button(page,"Check all sensor combinations",814,405,405,44,submit,True)
                status=label(page,"Edit the threshold and check your solution.",814,484,16,GREEN,25)
                button(page,"Independent fan exercise",814,533,405,34,show_fan,True)
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
    def seek_day(day=None):
        nonlocal state,playing,water,elapsed,visual,trace_key
        if timeline is None:return
        target=round(timeline["value"]) if day is None else day
        experiment.seek(target);state=experiment.state;playing=False;water=experiment.water;elapsed=0;visual=state.growth;trace_key=None
        timeline["value"]=state.day
        persist();set_message(f"Paused at day {state.day}. Resume or step.")
    def step_day():
        nonlocal playing,state,water,elapsed
        if state.day>=60:return
        if state.day==0 and (editor.get()!=experiment.source or initial()!=experiment.initial):
            try:experiment.start(editor.get(),initial())
            except RuleError as e:set_message("Code error: "+str(e)[:85]);return
        experiment.playing=True;experiment.step();experiment.playing=False
        state=experiment.state;water=experiment.water;playing=False;elapsed=0;persist();set_message(f"Day {state.day}. One rule check complete.")
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
        if state.day>=60 or (stage==0 and state.day>=(6 if guide_step in (1,2) else 24)):
            playing=False
            if stage==2:set_message("Finished. Growth "+str(round(state.growth*100))+"%. Run to compare another rule.")
    def pose_plant(node,health):
        stress=1-health
        # Each leaf is exported in local space at its stem attachment; bending does not scale the whole plant.
        for leaf in leaf_nodes.get(id(node),()):
            leaf.setR((-1 if "left" in leaf.getName() else 1)*58*stress)
        node.setColorScale(1,.48+.52*health,.34+.66*health,1)
    def update(task):
        nonlocal elapsed,visual,shown,trace_key,active_trace,teacher_frame
        if screen=="fan":
            if fan_on and fan_rotor is not None:fan_rotor.setR(fan_rotor.getR()+ClockObject.getGlobalClock().getDt()*420)
            return Task.cont
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
        pose_plant(plants[idx],state.health)
        if teacher_visible and teacher_gesture:
            teacher_frame=min(teacher.getNumFrames("explain")-1,teacher_frame+dt*30)
            teacher.pose("explain",int(teacher_frame))
        wet=state.moisture/100;soil.setColorScale(.85-.35*wet,.81-.35*wet,.76-.36*wet,1)
        for i,p in enumerate(drops):
            if (playing or stage==1) and water:
                phase=(task.time*2.6+i/len(drops))%1
                p.setPos((i%3-1)*.003,.035,.36-.302*phase*phase);p.show()
            else:p.hide()
        active_water=(playing or stage==1) and water
        if impact is not None:
            impact.show() if active_water else impact.hide()
            impact.setAlphaScale(.45+.35*(1-(task.time*3)%1))
        if water_sound is not None:
            if active_water and voice and water_sound.status()!=water_sound.PLAYING:water_sound.play()
            elif not active_water:water_sound.stop()
        if metrics is not None:
            metrics["text"]=f"Day {state.day}  |  Soil {state.moisture}%  |  Growth {round(state.growth*100)}%  |  Health {round(state.health*100)}%"
        if stage==2 and timeline is not None:
            target_day_label["text"]="Go to day "+str(round(timeline["value"]))
            key=(experiment.source,state.day,experiment.initial)
            if key!=trace_key:
                trace_key=key;active_trace=trace_day(experiment)
                if active_trace is None:trace_label["text"]="Day 0: no code has executed. Press Run or Step."
                else:
                    checks=" / ".join(f"Line {n}: {v}" for n,v in active_trace.conditions)
                    line=experiment.source.splitlines()[active_trace.action_line-1].strip()
                    trace_label["text"]=f"Day {state.day} | Sensor before: {experiment.last_input}% | {checks}\nExecuted line {active_trace.action_line}: {line} | Soil after: {state.moisture}% | Time compressed"
        set_cam();return Task.cont
    def make_comparison_models():
        if compare_meshes:return
        for x in (-.36,.36):
            root=compare_root.attachNewNode("sample");root.setX(x)
            physical_box=box_model.copyTo(root);substrate=physical_box.find("**/soil_surface")
            models=[]
            for p in plants:
                copy=p.copyTo(root);copy.hide();models.append(copy)
                leaf_nodes[id(copy)]=list(copy.findAllMatches("**/leaf_*"))
            compare_meshes.append((root,models,substrate))
    def show_comparison():
        nonlocal comparison_day,compare_labels,timeline
        clear("compare");make_comparison_models()
        label(page,"Compare irrigation outcomes",32,96,25)
        button(page,"Back to experiment",1030,73,210,39,lambda:show_lesson(2),True)
        label(page,"Same seed, same starting environment, different rules.",810,170,19,INK,22)
        label(page,"Reference rule",810,228,18)
        for i,(name,rule) in enumerate((("No water",DRY_RULE),("Always water",WET_RULE),("Default controller",DEFAULT_CODE),("Stop watering after day 20",STOP_AFTER_GROWTH))):
            def choose(rule=rule):
                nonlocal reference
                reference=rule;refresh_comparison()
            button(page,name,810,242+i*36,420,30,choose)
        compare_labels=[label(page,"",48,624,17,INK,38),label(page,"",410,624,17,INK,38)]
        label(page,"Compare day",810,404,18)
        slider=DirectSlider(parent=page,range=(0,60),value=comparison_day,pageSize=1,scale=1,pos=(1018,0,-435),frameSize=(-190,190,-7,7),thumb_frameSize=(-8,8,-10,10))
        def move():
            nonlocal comparison_day
            comparison_day=round(slider["value"]);refresh_comparison()
        slider["command"]=move
        label(page,"A: last executed rule. B: selected reference. Both use the identical simulation model.",810,494,16,MUTED,25)
        app.camera.setPos(0,-2.45,.42);app.camera.lookAt(0,0,.06)
        refresh_comparison()
    def refresh_comparison():
        left,right=comparison(experiment.source,experiment.initial,comparison_day,DEFAULT_CODE if reference==STOP_AFTER_GROWTH else reference)
        samples=(left.state,stop_after_growth(experiment.initial,comparison_day) if reference==STOP_AFTER_GROWTH else right.state)
        for i,(sample,(root,models,substrate)) in enumerate(zip(samples,compare_meshes)):
            wet=sample.moisture/100;substrate.setColorScale(.85-.35*wet,.81-.35*wet,.76-.36*wet,1)
            idx=round(sample.growth*(len(models)-1))
            for j,p in enumerate(models):p.show() if j==idx else p.hide()
            pose_plant(models[idx],sample.health)
            name="A: Your rule" if i==0 else "B: Water stopped" if reference==STOP_AFTER_GROWTH else "B: Reference"
            compare_labels[i]["text"]=f"{name} | Day {comparison_day}\nGrowth {round(sample.growth*100)}% | Health {round(sample.health*100)}%\nSoil {sample.moisture}%"
    def build_fan():
        nonlocal fan_rotor
        if fan_rotor is not None:return
        housing=NodePath(gltf.load_model(str(assets()/"fan-housing.glb")));housing.reparentTo(fan_root)
        fan_rotor=NodePath(gltf.load_model(str(assets()/"fan-rotor.glb")));fan_rotor.reparentTo(fan_root)
    def show_fan():
        nonlocal editor,status,fan_temp,fan_status,fan_on,trace_label,fan_run,fan_slider
        clear("fan");build_fan();fan_on=False
        label(page,"Independent practice | Ventilation controller",32,96,24)
        button(page,"Back to irrigation",1024,73,218,39,lambda:show_lesson(3),True)
        label(page,"Exhaust fan",54,155,21,GREEN)
        label(page,"Turn the fan on above 30 C; otherwise off.",810,165,20,INK,22)
        label(page,"Write your own if / else rule.",810,225,17,MUTED)
        panel(page,810,242,424,136,GREEN)
        editor=DirectEntry(parent=page,initialText=fan_source,scale=17,pos=(823,0,-265),width=23,numLines=6,frameColor=GREEN,text_fg=WHITE,focus=0,command=lambda _:insert_code("\n"))
        button(page,"Clear",1136,211,92,24,lambda:clear_editor(True))
        fan_status=label(page,"Temperature: 28 C",810,408,18)
        s=DirectSlider(parent=page,range=(0,45),value=fan_temp,pageSize=1,scale=1,pos=(1018,0,-428),frameSize=(-190,190,-7,7),thumb_frameSize=(-8,8,-10,10))
        def temp_change():
            nonlocal fan_temp
            nonlocal fan_on
            selected=round(s["value"])
            changed=selected!=fan_temp;fan_temp=selected;fan_status["text"]=f"Temperature: {fan_temp} C"
            if changed:
                fan_on=False
                if status is not None:set_message("Temperature changed. Run to evaluate.")
        s["command"]=temp_change;temp_change();fan_slider=s
        status=label(page,"Change temperature, then Run.",810,516,16,GREEN,25)
        trace_label=label(page,"Try 29, 30 and 31 C. The exact boundary matters.",48,648,17,INK,75)
        def run_fan(check=False):
            nonlocal fan_on,fan_source
            try:
                t=trace_rule(editor.get(),Plant(temperature=fan_temp),"ventilate")
                fan_source=editor.get();fan_on=t.action
                trace_label["text"]=f"Temperature {fan_temp} C | "+" / ".join(f"Line {n}: {v}" for n,v in t.conditions)+f" | Executed line {t.action_line}: fan {'ON' if fan_on else 'OFF'}"
                if check:
                    passed,total,first=fan_check(fan_source)
                    set_message(f"{passed}/{total} correct." if first is None else f"{passed}/{total}. First failing temperature: {first[0].temperature} C.")
                else:set_message("Fan running" if fan_on else "Fan stopped")
            except RuleError as e:fan_on=False;set_message("Code error: "+str(e)[:85])
        fan_run=run_fan
        button(page,"Run",810,454,150,36,run_fan,True)
        button(page,"Check rule",970,454,260,36,lambda:run_fan(True))
        button(page,"Hint",810,545,150,28,lambda:set_message("Use temperature > 30 and ventilate(True) / ventilate(False)."))
        app.camera.setPos(0,-2.9,.0);app.camera.lookAt(0,0,0)
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
    home_seconds=time.perf_counter()-boot_start
    if benchmark:
        from statistics import median
        import math, platform
        out=Path(os.environ.get("BLOOMLOGIC_CAPTURE_DIR","build/runtime-review"));out.mkdir(parents=True,exist_ok=True)
        load_start=time.perf_counter();open_lesson();show_lesson(2)
        scene_seconds=time.perf_counter()-load_start
        settings["Initial moisture"]["value"]=42;settings["Light hours"]["value"]=15;settings["Temperature C"]["value"]=28
        start();seek_day(60);visual=1.
        # Warm up the real scene, then time taskMgr.step (includes its normal graphics task).
        def measure(mode):
            camera(mode)
            for _ in range(8):app.taskMgr.step()
            durations=[]
            for _ in range(60):
                t=time.perf_counter();app.taskMgr.step();durations.append((time.perf_counter()-t)*1000)
            ordered=sorted(durations)
            return {"frames":len(durations),"median_ms":round(median(durations),3),"p95_ms":round(ordered[math.ceil(.95*len(ordered))-1],3),"p99_ms":round(ordered[math.ceil(.99*len(ordered))-1],3),"frames_over_50ms":sum(v>50 for v in durations),"max_ms":round(max(durations),3)}
        macro=measure("macro");wide=measure("wide")
        gsg=app.win.getGsg()
        result={"requested_resolution":resolution,"actual_resolution":[app.win.getXSize(),app.win.getYSize()],"platform":platform.platform(),"machine":platform.machine(),"logical_cpus":os.cpu_count(),"renderer":gsg.getDriverRenderer(),"vendor":gsg.getDriverVendor(),"driver":gsg.getDriverVersion(),"advanced_lighting":advanced,"home_seconds_after_python_entry":round(home_seconds,3),"first_scene_load_seconds":round(scene_seconds,3),"macro":macro,"overview":wide,"condition":"hosted runner; mature plant paused; 8 warmup frames per view; 60 sampled frames; VSync disabled"}
        assert state.day==60 and state.growth==1
        name="benchmark-"+str(resolution[1])+".json"
        (out/name).write_text(json.dumps(result,indent=2),encoding="utf-8")
        assert app.win.saveScreenshot(Filename.fromOsSpecific(str(out/("benchmark-"+str(resolution[1])+".png"))))
        milestone("benchmark complete "+name);app.destroy();return
    if "--resume-check" in sys.argv:
        # Independent new process, same explicit audit profile, never student data.
        assert complete and experiment.state.day==60 and not experiment.playing
        before=experiment.snapshot();open_lesson(True);assert stage==2 and state==experiment.state
        for _ in range(5):app.taskMgr.step()
        assert experiment.snapshot()==before and not playing
        milestone("fresh-process resume passed");app.destroy();return
    if any(x in sys.argv for x in ("--capture","--gui-test","--headless-gui-test")):
        out=Path(os.environ.get("BLOOMLOGIC_CAPTURE_DIR","build/runtime-review"));out.mkdir(parents=True,exist_ok=True)
        def capture(name):
            for _ in range(5):app.taskMgr.step();app.graphicsEngine.renderFrame()
            assert app.win.saveScreenshot(Filename.fromOsSpecific(str(out/name)))
            milestone("captured "+name)
        capture("home.png");open_lesson();teacher.pose("explain",int(teacher.getNumFrames("explain")*.5));capture("guide.png")
        guide_step=1;show_lesson(0);assert state.moisture==20;capture("prediction.png")
        guide_step=2;show_lesson(0);assert state.moisture==60;capture("prediction-moist.png")
        guide_step=3;show_lesson(0)
        for _ in range(24):tick()
        assert state.growth==1
        visual=1;capture("guided-growth.png")
        show_lesson(1);capture("code.png");assert active_trace.action
        demo_moisture=40;show_lesson(1);assert not active_trace.action;capture("code-else.png")
        show_lesson(2)
        settings["Initial moisture"]["value"]=42;settings["Light hours"]["value"]=15;settings["Temperature C"]["value"]=28
        start()
        for _ in range(60):tick()
        assert state.growth==1 and state.health>.9
        visual=1.;capture("grown.png");assert state.day==60 and state.growth==1
        assert leaf_nodes[id(plants[-1])],"Missing authored leaf pivots"
        pose_plant(plants[-1],.2)
        assert any(abs(leaf.getR())>30 for leaf in leaf_nodes[id(plants[-1])])
        pose_plant(plants[-1],1)
        seek_day(10);assert state.day==10 and not playing;capture("rewind.png");assert state.day==10
        seek_day(60);assert state.growth==1
        show_comparison();capture("compare.png")
        reference=STOP_AFTER_GROWTH;refresh_comparison();capture("mature-wilt.png")
        wilt=stop_after_growth(experiment.initial,60);assert wilt.growth==1 and wilt.health==0
        assert any(abs(leaf.getR())>45 for leaf in leaf_nodes[id(compare_meshes[1][1][-1])])
        reference=DRY_RULE;show_lesson(2);assert state.day==60
        editor.enterText("if moisture < 0:\n    irrigate(True)\nelse:\n    irrigate(False)")
        settings["Initial moisture"]["value"]=20;start()
        for _ in range(60):tick()
        assert state.growth<.1 and state.health==0
        visual=state.growth;capture("dry.png")
        # An always-watering controller stresses a plant after initial germination.
        editor.enterText(WET_RULE);settings["Initial moisture"]["value"]=20;start()
        for _ in range(60):tick()
        assert state.health==0 and state.growth>0
        visual=state.growth;capture("overwatered.png")
        before=state;editor.enterText("import os");start();assert state==before and not playing
        capture("invalid-code.png")
        show_lesson(3);editor.enterText(DEFAULT_CODE.replace("40","50"))
        passed,total,failures=challenge(editor.get());assert passed==total and not failures
        submit();assert complete
        capture("challenge.png");show_fan();capture("fan.png")
        editor.enterText(FAN_EXAMPLE);fan_slider["value"]=31;fan_temp=31;fan_run(True);assert fan_on
        rotor_before=fan_rotor.getR();capture("fan-on.png");assert fan_on and fan_rotor.getR()!=rotor_before
        fan_slider["value"]=30;fan_temp=30;fan_run();assert not fan_on
        rotor_before=fan_rotor.getR();capture("fan-off.png");assert not fan_on and fan_rotor.getR()==rotor_before;show_lesson(1);show_lesson(2)
        home();capture("return-home.png")
        assert load_profile(profile_path())["greenhouse_complete"]
        assert load_profile(profile_path())["experiment"]==experiment.snapshot()
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
    if any(x in sys.argv for x in ("--capture","--gui-test","--headless-gui-test","--input-test","--self-test","--benchmark","--resume-check")) and "BLOOMLOGIC_PROFILE_DIR" not in os.environ:
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
        if any(x in sys.argv for x in ("--gui-test","--headless-gui-test","--capture","--input-test","--benchmark","--resume-check")):
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

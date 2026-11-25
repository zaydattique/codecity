"""Generate offline English synthetic narration for the guided lesson during build."""
import subprocess
from pathlib import Path
from codecity.curriculum import GUIDE,CODE_STEPS
def main():
    lines={**{f"guide{i}":body for i,(_,body) in enumerate(GUIDE)},**{f"code{i}":body for i,(_,body) in enumerate(CODE_STEPS)},"experiment":"Change the threshold and run your rule. Watch the water and plant growth. Try dry soil and overwatering.","challenge":"Turn water on when moisture is below fifty percent. Otherwise, turn water off. Test both branches."}
    for key,body in lines.items():
        subprocess.run(["espeak-ng","-v","en-us+f3","-s","150","-w",str(Path("runtime")/f"voice-{key}.wav"),body],check=True)
if __name__=="__main__":main()

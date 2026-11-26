"""Derived gloss map and original synthesized irrigation sound for the offline exhibit."""
from pathlib import Path
import math,random,wave,struct
from PIL import Image,ImageOps
root=Path("runtime")
rough=next(root.glob("soil-rough.*"))
ImageOps.invert(Image.open(rough).convert("L")).save(root/"soil-gloss.png")
random.seed(63);rate=22050;prev=0;frames=[]
for i in range(rate*2):
    # Filtered noise and tiny droplet impulses; intentionally subtle.
    noise=random.uniform(-1,1);prev=.82*prev+.18*noise
    env=min(1,i/500,(rate*2-1-i)/500)
    pulse=(math.sin(i*.17)*.08 if i%1103<75 else 0)
    frames.append(struct.pack("<h",int(max(-1,min(1,(prev*.55+pulse)*env))*15000)))
with wave.open(str(root/"water-contact.wav"),"wb") as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b"".join(frames))

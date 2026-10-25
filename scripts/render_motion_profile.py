from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import math, json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W, H = 1000, 360
BG = (5, 14, 32)
CYAN = (43, 177, 255)
WHITE = (235, 244, 255)
MUTED = (143, 167, 198)
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"
FONT_M = "C:/Windows/Fonts/consola.ttf"

def font(size, kind="r"):
    p = {"b":FONT_B,"r":FONT_R,"m":FONT_M}[kind]
    if not Path(p).exists():
        p={"b":"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","r":"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","m":"/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"}[kind]
    return ImageFont.truetype(p, size)

def canvas():
    base=Image.new("RGB",(W,H),BG)
    haze=Image.new("RGBA",(W,H),(0,0,0,0)); h=ImageDraw.Draw(haze)
    h.ellipse((540,-240,1220,410),fill=(0,87,167,65))
    return Image.alpha_composite(base.convert("RGBA"),haze.filter(ImageFilter.GaussianBlur(92))).convert("RGB")

def grid(d, phase):
    for x in range(-40, W+40, 44):
        xx = (x + int(phase*8)) % (W+44)
        d.line((xx,0,xx,H), fill=(12,31,57), width=1)
    for y in range(0,H,44): d.line((0,y,W,y), fill=(12,31,57), width=1)

def rounded(d, box, radius=18, fill=(8,23,45), outline=(35,84,129), width=2):
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)

def wire_cube(d,cx,cy,size,phase,color=CYAN):
    # A rotating 3D cube, projected with perspective onto the profile panel.
    pts=[]; ca,sa=math.cos(phase),math.sin(phase); cb,sb=math.cos(phase*.67),math.sin(phase*.67)
    for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
        x1=x*ca-z*sa; z1=x*sa+z*ca
        y1=y*cb-z1*sb; z2=y*sb+z1*cb
        persp=3.3/(3.3+z2*.42)
        pts.append((cx+x1*size*.43*persp,cy+y1*size*.43*persp))
    for layer,w in [(color,3),((18,91,150),1)]:
        for i in range(4):
            d.line((*pts[i],*pts[(i+1)%4]),fill=layer,width=w)
            d.line((*pts[i+4],*pts[(i+1)%4+4]),fill=layer,width=w)
            d.line((*pts[i],*pts[i+4]),fill=layer,width=w)
    d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=(156,226,255))

def label(d,text,x,y,size=14,color=MUTED,kind="m"):
    d.text((x,y),text,font=font(size,kind),fill=color)

def glow_line(d,x,y,w,phase,color=CYAN):
    pulse=(math.sin(phase*2)+1)/2
    d.rounded_rectangle((x,y,x+w,y+3),2,fill=(18,57,91))
    d.rounded_rectangle((x+int((w-190)*((phase*.08)%1)),y,x+int((w-190)*((phase*.08)%1))+190,y+3),2,fill=color)

def frames_for(name, draw_fn, n=24, duration=90, colors=64):
    frames=[]
    for i in range(n):
        p=i/n*2*math.pi
        im=canvas(); d=ImageDraw.Draw(im)
        grid(d,i/n)
        draw_fn(im,d,p,i,n)
        frames.append(im)
    frames=[f.resize((800,288),Image.Resampling.LANCZOS) for f in frames]
    palette=frames[0].convert("P",palette=Image.Palette.ADAPTIVE,colors=colors)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    palette.save(ASSETS/f"{name}.gif",save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=1)
    palette.convert("RGB").save(ASSETS/f"{name}-poster.png",optimize=True)

def hero(im,d,p,i,n):
    # Use the supplied wide banner as a framed, moving inset.
    banner=Image.open(ASSETS/"Shivam Singh_ AI Innovation Banner.png").convert("RGB")
    banner.thumbnail((600,225))
    x=32+int(math.sin(p)*5); y=62+int(math.cos(p)*3)
    d.rounded_rectangle((x-5,y-5,x+banner.width+5,y+banner.height+5),14,fill=(7,22,42),outline=(38,132,205),width=2)
    im.paste(banner,(x,y))
    label(d,"SHIVAM SINGH",680,82,28,WHITE,"b")
    label(d,"AI  /  WEB  /  DIGITAL INNOVATION",680,124,15,CYAN)
    label(d,"Building useful products with thoughtful craft.",680,163,16,WHITE,"r")
    label(d,"PROFILE MOTION SYSTEM  •  2026",680,197,12,MUTED)
    wire_cube(d,835,278,106,p,color=CYAN)
    glow_line(d,680,231,270,p)
    label(d,"01  —  INTRODUCTION",32,22,13,CYAN)

def who(im,d,p,i,n):
    portrait=Image.open(ASSETS/"Studio Portrait with Folded Arms.png").convert("RGB")
    portrait=ImageEnhance.Color(portrait).enhance(0.86)
    portrait=portrait.resize((300,300))
    x=48+int(math.sin(p)*4); y=39+int(math.cos(p)*3)
    mask=Image.new("L",portrait.size,0); md=ImageDraw.Draw(mask); md.ellipse((0,0,300,300),fill=255)
    # circular crop using center portrait and clean rounded frame
    im.paste(portrait,(x,y),mask)
    d.ellipse((x-5,y-5,x+305,y+305),outline=CYAN,width=3)
    rounded(d,(390,45,955,315),18,(7,20,40),(32,88,133),2)
    label(d,"shivam@profile:~$ whoami",420,67,16,CYAN)
    label(d,"Shivam Singh",420,104,31,WHITE,"b")
    label(d,"AI-assisted Web Developer  /  CSE • AI & ML",420,151,17,MUTED,"r")
    for j,line in enumerate(["Frontend systems · React · TypeScript","AI-assisted workflows · product design","Creator · technology · digital experiences"]):
        label(d,"›  "+line,420,199+j*31,15,WHITE,"r")
    wire_cube(d,896,93,48,p*.8,color=(79,200,255))

def contributions(im,d,p,i,n):
    label(d,"02  —  CONTRIBUTION SIGNAL",34,24,13,CYAN)
    label(d,"Consistency, visualized.",34,55,30,WHITE,"b")
    label(d,"Public activity snapshot  •  values stay true; only the tracer moves",34,99,14,MUTED,"r")
    data={}
    try: data=json.loads((ROOT/"data/contributions.json").read_text(encoding="utf-8"))
    except Exception: pass
    # draw genuine historical calendar if workflow data is present, otherwise clean labeled placeholder
    values=data.get("weeks") or data.get("contributions") or data.get("days") or []
    flat=[]
    for item in values:
        if isinstance(item,list) and len(item)>=3 and isinstance(item[0],str): flat.append(item[2])
        elif isinstance(item,list): flat.extend(item)
        elif isinstance(item,dict): flat.append(item.get("count",0))
        elif isinstance(item,list) and len(item)>=3 and isinstance(item[0],str): flat.append(item[2])
    if not flat: flat=[0]*196
    maxv=max([int(v.get("count",0) if isinstance(v,dict) else v or 0) for v in flat] or [1])
    gx,gy=44,148; cell=16; gap=6
    for idx,v in enumerate(flat[:364]):
        col,row=divmod(idx,7)
        count=int(v.get("count",0) if isinstance(v,dict) else v or 0)
        level=min(4, int(count/max(1,maxv)*4))
        colors=[(13,30,49),(17,60,83),(18,99,131),(26,151,190),(59,202,248)]
        d.rounded_rectangle((gx+col*(cell+gap),gy+row*(cell+gap),gx+col*(cell+gap)+cell,gy+row*(cell+gap)+cell),3,fill=colors[level])
    tracer=int((i/n)*min(52,max(0,len(flat)//7)))*(cell+gap)
    d.line((gx+tracer,gy-9,gx+tracer,gy+7*(cell+gap)),fill=(170,235,255),width=2)
    label(d,"LOWER ACTIVITY",46,329,10,MUTED)
    label(d,"MORE ACTIVITY",822,329,10,MUTED)
    wire_cube(d,928,72,48,p,color=(72,197,255))

PROJECTS=[
 ("elementraui","ElementraUI","OPEN-SOURCE COMPONENT DISCOVERY","Components · themes · templates · motion resources",(42,179,255)),
 ("tz-roms","TZ ROMs","ANDROID ROM DISCOVERY","Multi-device ROM hub · Poco X6 Pro portal",(135,111,255)),
 ("physifer","PHYSIFER 2.0","EDUCATION & CREATOR PLATFORM","Website · social content · video editing",(255,161,66)),
 ("tzlabs","TZ Labs","TECHNOLOGY STUDIO","Technology projects and digital experiences",(42,219,188)),
 ("prayanone","PrayanOne","RAILWAY INFORMATION WEB PROJECT","Travel information · product interface",(65,157,255)),
 ("greenera","Greenera Organics","E-COMMERCE & DIGITAL OPERATIONS","Social media · storefront · website customization",(123,206,118)),
 ("apnabazaar","ApnaBazaar","INDEPENDENT WEB PROJECT","A portfolio project focused on everyday shopping",(255,105,135)),
]
def project(name,title,kicker,sub,color):
    def draw(im,d,p,i,n):
        label(d,"03  —  SELECTED WORK",34,24,13,CYAN)
        rounded(d,(32,66,968,324),20,(7,20,40),(33,76,116),2)
        d.rounded_rectangle((32,66,43,324),5,fill=color)
        label(d,"FEATURED PROJECT",68,91,12,color)
        label(d,title,68,125,32,WHITE,"b")
        label(d,kicker,68,181,14,color)
        label(d,sub,68,214,17,MUTED,"r")
        label(d,"OPEN PROJECT  ↗",68,277,14,WHITE)
        # rotating wireframe with glowing orbital ellipses to imply 3D object depth
        cx,cy=790,196
        d.ellipse((cx-115,cy-60,cx+115,cy+60),outline=(18,65,100),width=2)
        d.ellipse((cx-116,cy-38,cx+116,cy+38),outline=(16,62,97),width=2)
        wire_cube(d,cx,cy,130,p+len(title)*.1,color=color)
        d.ellipse((cx+int(math.cos(p)*112)-5,cy+int(math.sin(p)*43)-5,cx+int(math.cos(p)*112)+5,cy+int(math.sin(p)*43)+5),fill=color)
        glow_line(d,68,252,320,p,color=color)
    frames_for(f"project-{name}-motion",draw,n=32,duration=75)

def experience(im,d,p,i,n):
    label(d,"04  —  EXPERIENCE",34,24,13,CYAN)
    label(d,"From creative work to digital products.",34,57,29,WHITE,"b")
    entries=[("2020 — 2024","Fiverr","Graphic design & video editing"),("JAN 2026 — NOW","PHYSIFER","Social content & video editing"),("MAY — SEP 2026","GREENERA ORGANICS","Social media, e-commerce & site customization")]
    x0=95; d.line((x0,140,x0,301),fill=(34,104,155),width=3)
    for k,(date,org,desc) in enumerate(entries):
        yy=146+k*75; pulse=int((math.sin(p+k*1.4)+1)*2)
        d.ellipse((x0-8-pulse,yy-8-pulse,x0+8+pulse,yy+8+pulse),fill=CYAN,outline=(138,224,255),width=2)
        label(d,date,132,yy-20,12,CYAN)
        label(d,org,300,yy-23,20,WHITE,"b")
        label(d,org and desc,570,yy-18,15,MUTED,"r")

def toolkit(im,d,p,i,n):
    label(d,"05  —  TOOLKIT",34,24,13,CYAN)
    label(d,"Tools I reach for, grouped by the work.",34,56,28,WHITE,"b")
    groups=[("WEB","HTML · CSS · TypeScript · React · Vite · Tailwind"),("DATA","SQL · Excel · Sheets · dashboards · reporting"),("AI-ASSISTED","ChatGPT · Claude · Gemini · Cursor · prompt design"),("DIGITAL","SEO · Search Console · e-commerce · Amazon listings"),("CREATIVE","Canva · visual design · Filmora · video editing")]
    for j,(name,items) in enumerate(groups):
        x=34+(j%2)*477; y=111+(j//2)*81
        rounded(d,(x,y,x+440,y+62),12,(8,24,45),(31,83,127),1)
        label(d,name,x+17,y+10,12,CYAN)
        label(d,items,x+17,y+33,14,WHITE,"r")
    wire_cube(d,920,294,74,p,color=(85,205,255))

def channels(im,d,p,i,n):
    label(d,"06  —  CREATOR CHANNELS",34,24,13,CYAN)
    label(d,"Technology and stories, beyond the code.",34,58,28,WHITE,"b")
    names=[("Technoez Mobile","TECHNOLOGY"),("Shade Explains","GAMING EXPLAINERS"),("Dark Shade Gaming","GAMEPLAY"),("TZAILabs","AI CONTENT · UPCOMING")]
    for k,(a,b) in enumerate(names):
        x=38+k*237; y=145
        rounded(d,(x,y,x+218,y+125),16,(8,23,44),(33,86,132),2)
        cx=x+109; cy=y+42
        d.ellipse((cx-18,cy-18,cx+18,cy+18),fill=(175,32,48))
        d.polygon([(cx-6,cy-10),(cx+10,cy),(cx-6,cy+10)],fill=WHITE)
        label(d,a,x+14,y+73,15,WHITE,"b")
        label(d,b,x+14,y+99,10,CYAN)
        d.arc((x+1,y+1,x+217,y+124),int((p*45+k*25)%360),int((p*45+k*25)%360)+80,fill=(65,180,244),width=2)

def contact(im,d,p,i,n):
    label(d,"07  —  CONTACT",34,24,13,CYAN)
    label(d,"Let’s make something useful.",34,61,32,WHITE,"b")
    label(d,"Open to thoughtful conversations, freelance work, and collaborations.",34,112,17,MUTED,"r")
    for k,(a,b) in enumerate([("PORTFOLIO","me.technoezmobile.com"),("LINKEDIN","/in/itsxshivam"),("INSTAGRAM","@technoezmobile"),("YOUTUBE","@Technoez_Mobile")]):
        x=36+k*235
        rounded(d,(x,182,x+216,254),12,(8,24,45),(30,87,134),2)
        label(d,a,x+15,195,11,CYAN)
        label(d,b,x+15,221,14,WHITE,"b")
    wire_cube(d,895,303,74,p,color=CYAN)
    label(d,"BUILD WITH CURIOSITY  ·  SHIP WITH PURPOSE",36,301,12,MUTED)

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--contributions-only",action="store_true",help="Regenerate only the calendar GIF and reduced-motion poster")
    args=parser.parse_args()
    if args.contributions_only:
        frames_for("contributions-motion",contributions,n=36,duration=100)
        print("Refreshed the public contribution animation")
    else:
        frames_for("hero-motion",hero,n=36,duration=70,colors=160)
        frames_for("whoami-motion",who,n=32,duration=80,colors=160)
        frames_for("contributions-motion",contributions,n=36,duration=100)
        frames_for("experience-motion",experience,n=36,duration=90)
        frames_for("toolkit-motion",toolkit,n=36,duration=90)
        frames_for("channels-motion",channels,n=36,duration=85)
        frames_for("contact-motion",contact,n=36,duration=85)
        for spec in PROJECTS: project(*spec)
        # A short downloadable motion reel stitches the visual chapters into one video.
        import cv2, numpy as np
        reel=[]
        for name in ["hero-motion","whoami-motion","contributions-motion","project-elementraui-motion","experience-motion","toolkit-motion","channels-motion","contact-motion"]:
            gif=Image.open(ASSETS/f"{name}.gif")
            for index in range(0,gif.n_frames,max(1,gif.n_frames//12)):
                gif.seek(index)
                frame=gif.convert("RGB").resize((800,288))
                reel.append(cv2.cvtColor(np.array(frame),cv2.COLOR_RGB2BGR))
        video=cv2.VideoWriter(str(ASSETS/"profile-motion-reel.mp4"),cv2.VideoWriter_fourcc(*"mp4v"),12,(800,288))
        for frame in reel: video.write(frame)
        video.release()
        print("Rendered",len(list(ASSETS.glob("*-motion.gif"))),"looping motion panels and motion reel")

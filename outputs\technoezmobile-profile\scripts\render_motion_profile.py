"""Render the profile's animated glass cards, backgrounds, 3D orbs, and social buttons.

Uses Pillow + NumPy, with OpenCV only for the downloadable video reel. GitHub
profile READMEs support animated GIFs; this renderer keeps the text semantic in
README.md and supplies a still poster for reduced-motion preferences.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import colorsys, json, math, argparse
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W, H = 1000, 360
BG = (5, 11, 25)
CYAN = (43, 188, 255)
ICE = (207, 241, 255)
WHITE = (241, 247, 255)
MUTED = (152, 174, 201)
SPECTRUM = ["#00f0ff", "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#00f0ff"]
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"
FONT_M = "C:/Windows/Fonts/consola.ttf"
FONT_S = "C:/Windows/Fonts/georgia.ttf"
FONT_SI = "C:/Windows/Fonts/georgiai.ttf"

def font(size, kind="r"):
    p = {"b": FONT_B, "r": FONT_R, "m": FONT_M, "s": FONT_S, "i": FONT_SI}[kind]
    if not Path(p).exists():
        p = {"b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "r": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "m": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
             "s": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
             "i": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"}[kind]
    return ImageFont.truetype(p, size)

def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def canvas(phase):
    """Deep navy with three slowly drifting, blended aurora light fields."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = xx / W, yy / H
    out = np.empty((H, W, 3), dtype=np.float32)
    vignette = np.clip(1.08 - .35 * np.sqrt(((x-.5)/.75)**2 + ((y-.48)/.8)**2), .48, 1)
    base = np.array(BG, dtype=np.float32)
    out[:] = base
    clouds = [
        (.70 + .11*math.sin(phase*.62), .22 + .15*math.cos(phase*.53), .34, (10, 86, 215), .78),
        (.39 + .15*math.cos(phase*.47), .83 + .08*math.sin(phase*.71), .39, (48, 40, 178), .61),
        (.91 + .035*math.sin(phase*.55), .56 + .16*math.cos(phase*.41), .31, (0, 139, 187), .56),
        (.18 + .055*math.sin(phase*.39), .37 + .1*math.cos(phase*.57), .30, (91, 30, 157), .41),
    ]
    for cx, cy, radius, color, strength in clouds:
        dist = ((x-cx)**2 + ((y-cy)*1.16)**2) / (radius*radius)
        a = np.exp(-dist*2.4).astype(np.float32) * strength
        out += a[..., None] * np.array(color, dtype=np.float32)
    out *= vignette[..., None]
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    # A drifting technical perspective grid rather than a flat static checkerboard.
    horizon = int(H*.32)
    shift = int((phase*8) % 46)
    for x0 in range(-W, W*2, 76):
        bx = x0 + shift
        d.line((W*.52 + (bx-W*.52)*.16, horizon, bx, H), fill=(78, 155, 220, 18), width=1)
    for j in range(8):
        t = (j/8)**1.8
        y0 = int(horizon + (H-horizon)*t)
        d.line((0, y0, W, y0), fill=(78, 155, 220, 15), width=1)
    # Small motes drift at different speeds; the gentle sweep establishes motion across each whole panel.
    for j in range(36):
        px = int((j*137 + phase*(8 + j%7)) % W)
        py = int((j*59 + math.sin(phase*.7+j)*18) % H)
        a = 20 + int((math.sin(phase*1.3+j)+1)*18)
        r = 1 if j%4 else 2
        d.ellipse((px-r, py-r, px+r, py+r), fill=(135, 216, 255, a))
    scan_y = int((phase % (math.tau))*H/math.tau)
    d.line((0, scan_y, W, scan_y), fill=(133, 214, 255, 18), width=2)
    return im

def _rounded_path(box, radius, per_corner=18):
    x1, y1, x2, y2 = box
    out=[]
    for cx,cy,start in [(x2-radius,y1+radius,-90),(x2-radius,y2-radius,0),
                        (x1+radius,y2-radius,90),(x1+radius,y1+radius,180)]:
        for k in range(per_corner+1):
            a=math.radians(start + 90*k/per_corner)
            out.append((cx + radius*math.cos(a), cy + radius*math.sin(a)))
    return out

def rainbow_border(im, box, phase, radius=20, width=2, speed=1):
    """Traveling multi-hue perimeter with a fine glass rim and restrained bloom."""
    pts=_rounded_path(box,radius,24)
    glow=Image.new("RGBA",im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    hue_shift=(phase/math.tau*speed)%1
    count=len(pts)
    for i in range(count):
        p1,p2=pts[i],pts[(i+1)%count]
        hue=(i/count+hue_shift)%1
        col=tuple(int(c*0.86) for c in colorsys.hsv_to_rgb(hue,.78,1.0))
        gd.line((*p1,*p2),fill=(*col,100),width=width+6)
    glow=glow.filter(ImageFilter.GaussianBlur(5))
    im.alpha_composite(glow) if im.mode=="RGBA" else im.paste(Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB"))
    d=ImageDraw.Draw(im)
    for i in range(count):
        p1,p2=pts[i],pts[(i+1)%count]
        hue=(i/count+hue_shift)%1
        col=tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue,.8,1.0))
        d.line((*p1,*p2),fill=col,width=width)
    # A brighter traveling glint chases around the spectrum rim.
    head=int((phase/math.tau*speed%1)*count)
    for j in range(15):
        idx=(head+j)%count
        alpha=1-j/16
        p1,p2=pts[idx],pts[(idx+1)%count]
        c=tuple(int(ICE[k]*alpha + col* (1-alpha)) for k,col in enumerate((ICE[0],ICE[1],ICE[2])))
        d.line((*p1,*p2),fill=c,width=width+1)

def glass_panel(im, box, phase, radius=22, blur=12, tint=(5,16,34,145), rim=True):
    """Frosted liquid-glass pane: transmitted aurora, dark tint, curved specular and lower rim."""
    x1,y1,x2,y2=map(int,box); ww=x2-x1; hh=y2-y1
    crop=im.crop((x1,y1,x2,y2)).filter(ImageFilter.GaussianBlur(blur)).convert("RGBA")
    shade=Image.new("RGBA",crop.size,tint)
    pane=Image.alpha_composite(crop,shade)
    mask=Image.new("L",pane.size,0); md=ImageDraw.Draw(mask); md.rounded_rectangle((0,0,ww-1,hh-1),radius,fill=255)
    im.paste(pane.convert("RGB"),(x1,y1),mask)
    d=ImageDraw.Draw(im,"RGBA")
    d.rounded_rectangle(box,radius,fill=(8,18,36,25),outline=(202,231,255,70),width=1)
    # Upper curved highlight and lower cool refraction are the reference button's recognizable glass cues.
    d.arc((x1+8,y1+2,x2-8,y1+min(76,hh*.42)),185,355,fill=(255,255,255,118),width=2)
    d.line((x1+radius,y1+2,x2-radius,y1+2),fill=(255,255,255,62),width=1)
    d.arc((x1+6,y2-min(55,hh*.3),x2-6,y2+16),8,172,fill=(75,173,255,55),width=2)
    # A broad transparent reflection slides across the glass surface.
    sheen=Image.new("RGBA",(ww,hh),(0,0,0,0)); sd=ImageDraw.Draw(sheen)
    sx=int(((phase/math.tau)%1)*(ww+140))-110
    sd.polygon([(sx,0),(sx+32,0),(sx+158,hh),(sx+126,hh)],fill=(224,244,255,19))
    sheen.putalpha(ImageChops_multiply(sheen.getchannel("A"),mask))
    overlay=Image.new("RGBA",im.size,(0,0,0,0)); overlay.paste(sheen,(x1,y1))
    im.paste(Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB"))
    if rim:
        d=ImageDraw.Draw(im)
        d.rounded_rectangle(box,radius,outline=(89,179,255,95),width=1)

def ImageChops_multiply(a,b):
    from PIL import ImageChops
    return ImageChops.multiply(a,b)

def text(d, value, x, y, size=14, color=MUTED, kind="m", anchor=None):
    d.text((x,y),value,font=font(size,kind),fill=color,anchor=anchor)

def capsule(im, d, value, box, phase, color=CYAN, size=12):
    glass_panel(im,box,phase,radius=18,blur=6,tint=(5,18,39,170),rim=False)
    rainbow_border(im,box,phase,radius=18,width=1,speed=.74)
    d=ImageDraw.Draw(im)
    d.ellipse((box[0]+12,box[1]+(box[3]-box[1])/2-3,box[0]+18,box[1]+(box[3]-box[1])/2+3),fill=color)
    text(d,value,box[0]+27,box[1]+(box[3]-box[1])/2,size,WHITE,"m",anchor="lm")

def draw_sphere(im,d,cx,cy,r,phase,accent=(61,190,255)):
    """Rotating shaded icosphere with a real projected triangular wireframe and orbital rings."""
    glow=Image.new("RGBA",im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((cx-r*1.55,cy-r*1.55,cx+r*1.55,cy+r*1.55),fill=(*accent,62))
    im.paste(Image.alpha_composite(im.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(r*.55)).convert("RGBA")).convert("RGB"))
    d=ImageDraw.Draw(im)
    d.ellipse((cx-r*1.35,cy-r*.35,cx+r*1.35,cy+r*.35),outline=(*accent,78),width=2)
    d.ellipse((cx-r*1.12,cy-r*.68,cx+r*1.12,cy+r*.68),outline=(100,185,255),width=1)
    # A moving, volumetric sphere shader.
    size=int(r*2); coords=np.linspace(-1,1,size,dtype=np.float32); xx,yy=np.meshgrid(coords,coords)
    rr=xx*xx+yy*yy; mask=rr<=1; zz=np.sqrt(np.maximum(0,1-rr))
    lx,ly,lz=math.cos(phase*.5-.8),-.45,1.15
    diffuse=np.clip(xx*lx+yy*ly+zz*lz,0,1)
    spec=np.clip((xx*(lx*.66)+yy*(ly*.66)+zz*1.65),0,1)**30
    base=np.empty((size,size,3),dtype=np.float32)
    ac=np.array(accent,dtype=np.float32)
    base[:]=ac*.11+np.array((6,14,32),dtype=np.float32)
    base+=diffuse[...,None]*ac*.42+spec[...,None]*115
    base=np.clip(base,0,255).astype(np.uint8)
    alpha=(mask*255).astype(np.uint8)
    sphere=Image.fromarray(np.dstack((base,alpha)),"RGBA")
    im.paste(sphere,(int(cx-r),int(cy-r)),sphere)
    # Project a subdivided icosahedral mesh, not a flat longitude grid.
    line_layer=Image.new("RGBA",im.size,(0,0,0,0)); ld=ImageDraw.Draw(line_layer)
    ca,sa=math.cos(phase*.55),math.sin(phase*.55); cb,sb=math.cos(phase*.31),math.sin(phase*.31)
    phi=(1+math.sqrt(5))/2
    raw=[(-1,phi,0),(1,phi,0),(-1,-phi,0),(1,-phi,0),(0,-1,phi),(0,1,phi),(0,-1,-phi),(0,1,-phi),(phi,0,-1),(phi,0,1),(-phi,0,-1),(-phi,0,1)]
    verts=[]
    for v in raw:
        norm=math.sqrt(sum(q*q for q in v)); x,y,z=[q/norm for q in v]
        x1=x*ca-z*sa; z1=x*sa+z*ca
        y1=y*cb-z1*sb; z2=y*sb+z1*cb
        persp=3.5/(3.5+z2*.34)
        verts.append((cx+x1*r*.98*persp,cy+y1*r*.98*persp,z2))
    edges=set()
    for a in range(len(raw)):
        for b in range(a+1,len(raw)):
            dist=sum((raw[a][j]-raw[b][j])**2 for j in range(3))
            if dist < 4.01: edges.add((a,b))
    for a,b in edges:
        va,vb=verts[a],verts[b]
        depth=(va[2]+vb[2])/2
        alpha=35 if depth<0 else 120+int(35*depth)
        color=accent if depth<0 else ICE
        ld.line((va[0],va[1],vb[0],vb[1]),fill=(*color,alpha),width=1 if depth<0 else 2)
    for x,y,z in verts:
        if z>0:
            ld.ellipse((x-2,y-2,x+2,y+2),fill=(*ICE,220))
    im.paste(Image.alpha_composite(im.convert("RGBA"),line_layer).convert("RGB"))
    # Intersecting rings and a satellite make the volumetric spin legible at README size.
    d=ImageDraw.Draw(im)
    d.arc((cx-r*1.42,cy-r*.39,cx+r*1.42,cy+r*.39),int((phase*42)%360),int((phase*42)%360)+148,fill=ICE,width=3)
    a=phase*1.1
    sx=cx+math.cos(a)*r*1.34; sy=cy+math.sin(a)*r*.38
    d.ellipse((sx-5,sy-5,sx+5,sy+5),fill=ICE)

def frame_border(im,phase):
    rainbow_border(im,(6,6,W-7,H-7),phase,radius=18,width=2,speed=.62)

def chapter_rule(d,number,title,tag,phase):
    text(d,f"{number:02d}   /   {title.upper()}",48,27,11,ICE,"m")
    text(d,tag.upper(),951,28,9,MUTED,"m",anchor="ra")
    d.line((49,53,951,53),fill=(148,195,233,68),width=1)
    x=49+int((phase/math.tau%1)*902)
    d.line((max(49,x-78),53,min(951,x+78),53),fill=(113,216,255,185),width=2)
    d.ellipse((x-3,50,x+3,56),fill=ICE)

def hero(im,d,p,i,n):
    banner=Image.open(ASSETS/"Shivam Singh_ AI Innovation Banner.png").convert("RGB")
    banner=banner.resize((W,375),Image.Resampling.LANCZOS).crop((0,0,W,H))
    im.paste(banner,(0,0))
    # Moving glassy light, subtle spectral dust, and edge prism around the supplied frame art.
    overlay=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(overlay)
    sx=int((p/math.tau)*(W+360))-180
    od.polygon([(sx,0),(sx+52,0),(sx+285,H),(sx+228,H)],fill=(110,215,255,22))
    scan=int((i/n)*H)
    od.line((0,scan,W,scan),fill=(160,229,255,28),width=2)
    im.paste(Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB"))
    d=ImageDraw.Draw(im)
    text(d,"SHIVAM  /  PROFILE SYSTEM",28,19,11,ICE,"m")
    text(d,"01  ·  INTRODUCTION",W-28,19,11,ICE,"m",anchor="ra")

def identity(im,d,p,i,n):
    glass_panel(im,(26,24,974,336),p,radius=27,blur=18,tint=(3,11,27,150))
    # Portrait arch and orbit echo the reference's person-first identity panel.
    px,py=817,182
    for rad,col,w in [(137,(30,144,255),2),(148,(118,93,255),1),(160,(57,203,255),1)]:
        d.ellipse((px-rad,py-rad,px+rad,py+rad),outline=(*col,105),width=w)
    d.arc((px-166,py-166,px+166,py+166),int((p*38)%360),int((p*38)%360)+116,fill=ICE,width=3)
    point=(px+math.cos(p)*160,py+math.sin(p)*160)
    d.ellipse((point[0]-4,point[1]-4,point[0]+4,point[1]+4),fill=ICE)
    portrait=Image.open(ASSETS/"Studio Portrait with Folded Arms.png").convert("RGB")
    portrait=ImageEnhance.Color(portrait).enhance(1.04).resize((250,300),Image.Resampling.LANCZOS)
    pmask=Image.new("L",portrait.size,0); md=ImageDraw.Draw(pmask)
    md.ellipse((0,0,249,230),fill=255); md.rounded_rectangle((0,112,249,299),16,fill=255)
    im.paste(portrait,(px-125,py-151),pmask)
    d=ImageDraw.Draw(im); d.arc((px-126,py-151,px+126,py+99),180,360,fill=(232,246,255,210),width=2)
    d.line((px-125,py-26,px-125,py+145),fill=(115,208,255,185),width=1)
    d.line((px+125,py-26,px+125,py+145),fill=(115,208,255,185),width=1)
    d.arc((px-126,py+112,px+126,py+153),0,180,fill=(115,208,255,185),width=1)
    # Editorial serif name, terminal eyebrow and compact identity facts.
    text(d,"01   /   ABOUT",63,54,11,ICE,"m")
    text(d,"Hello, I’m",61,83,21,WHITE,"s")
    text(d,"Shivam Singh",59,112,43,WHITE,"s")
    text(d,"AI-ASSISTED WEB DEVELOPER",63,174,13,CYAN,"m")
    text(d,"Computer Science · AI & Machine Learning",63,207,16,WHITE,"r")
    text(d,"Building digital products, creator platforms, and practical web experiences.",63,236,14,MUTED,"r")
    capsule(im,d,"B.TECH  /  CLASS OF 2027",(63,263,331,300),p,color=(114,170,255),size=10)
    capsule(im,d,"WEB  ·  DIGITAL  ·  CREATOR",(344,263,649,300),p+1.5,color=(205,115,255),size=10)
    text(d,"RGPV  BHOPAL    /    BUILDER · CREATOR · LEARNER",64,319,10,MUTED,"m")
    rainbow_border(im,(26,24,974,336),p,radius=27,width=2,speed=.84)

def contributions(im,d,p,i,n):
    glass_panel(im,(24,22,976,338),p,radius=26,blur=16,tint=(4,13,29,158))
    chapter_rule(d,5,"Build log","real public activity · refreshed daily",p)
    text(d,"A year of building, one square at a time.",51,80,26,WHITE,"s")
    data={}
    try: data=json.loads((ROOT/"data/contributions.json").read_text(encoding="utf-8"))
    except Exception: pass
    days=data.get("days",[])
    if days:
        values=[(row[1],row[2]) for row in days if isinstance(row,list) and len(row)>=3]
    else:
        values=[(0,0)]*364
    while len(values)%7: values.append((0,0))
    cols=len(values)//7; cell=12; gap=4
    gx=54; gy=132
    max_count=max([v[0] for v in values] or [1])
    palette=[(15,31,52),(20,56,86),(22,92,137),(42,143,197),(109,206,255)]
    for k,(count,level) in enumerate(values):
        col,row=divmod(k,7)
        level=max(int(level),min(4,int(count/max(1,max_count)*4.2)))
        x=gx+col*(cell+gap); y=gy+row*(cell+gap)
        if x+cell<W-44:
            d.rounded_rectangle((x,y,x+cell,y+cell),3,fill=palette[min(4,level)])
    # The activity values remain fixed. Only a luminous tracer scans along the calendar.
    active=int((i/n)*max(1,cols))
    xx=gx+active*(cell+gap)
    d.line((xx,gy-11,xx,gy+7*(cell+gap)-4),fill=(142,222,255,185),width=2)
    d.ellipse((xx-4,gy-14,xx+4,gy-6),fill=ICE)
    total=data.get("total",sum(x[0] for x in values))
    active_days=sum(1 for c,_ in values if c>0)
    text(d,f"{total:,} PUBLIC CONTRIBUTIONS",54,286,12,CYAN,"m")
    text(d,f"{active_days} ACTIVE DAYS  ·  PUBLIC PROFILE DATA",54,307,10,MUTED,"m")
    text(d,"PRIVATE ACTIVITY EXCLUDED",946,310,9,MUTED,"m",anchor="ra")
    rainbow_border(im,(24,22,976,338),p,radius=26,width=2,speed=.62)

PROJECTS=[
 ("elementraui","ElementraUI","OPEN-SOURCE COMPONENT DISCOVERY","Components · themes · templates · motion resources",(38,174,255)),
 ("tz-roms","TZ ROMs","ANDROID ROM DISCOVERY","Multi-device ROM hub · Poco X6 Pro portal",(139,106,255)),
 ("physifer","PHYSIFER 2.0","EDUCATION & CREATOR PLATFORM","Website · social content · video editing",(255,163,94)),
 ("tzlabs","TZ Labs","TECHNOLOGY STUDIO","Technology projects and digital experiences",(46,220,198)),
 ("prayanone","PrayanOne","RAILWAY INFORMATION WEB PROJECT","Travel information · product interface",(79,170,255)),
 ("greenera","Greenera Organics","E-COMMERCE & DIGITAL OPERATIONS","Social media · storefront · website customization",(139,221,126)),
 ("apnabazaar","ApnaBazaar","INDEPENDENT WEB PROJECT","A portfolio project focused on everyday shopping",(255,115,156)),
]

def project(name,title,kicker,sub,color):
    def draw(im,d,p,i,n):
        text(d,f"PROJECT FILE   /   {name.upper()}",61,36,10,ICE,"m")
        text(d,"SHIVAM SINGH  ·  PORTFOLIO",951,36,9,MUTED,"m",anchor="ra")
        d.line((49,55,951,55),fill=(148,195,233,68),width=1)
        x=49+int((p/math.tau%1)*902)
        d.line((max(49,x-65),55,min(951,x+65),55),fill=(113,216,255,185),width=2)
        d.ellipse((x-3,52,x+3,58),fill=ICE)
        glass_panel(im,(26,67,974,329),p,radius=25,blur=18,tint=(4,13,29,157))
        d=ImageDraw.Draw(im)
        text(d,"CASE STUDY",61,94,10,color,"m")
        text(d,title,59,120,38,WHITE,"s")
        text(d,kicker,62,174,12,color,"m")
        text(d,sub,62,210,14,WHITE,"r")
        # Capsule follows TZ Labs LiquidGlassButton: rainbow mask, translucent face, top reflection and lower rim.
        capsule(im,d,"VIEW PROJECT  ↗",(61,261,286,302),p+1,color=color,size=11)
        draw_project_visual(im,d,name,p,color)
        rainbow_border(im,(26,67,974,329),p,radius=25,width=2,speed=.72)
    return lambda im,d,p,i,n:draw(im,d,p,i,n)

def draw_project_visual(im,d,name,phase,color):
    """Give each case study a project-specific animated miniature instead of a repeated orb."""
    x0,y0=636,95
    glass_panel(im,(x0,y0,933,306),phase,radius=20,blur=8,tint=(5,16,36,164),rim=False)
    d=ImageDraw.Draw(im,"RGBA")
    if name=="elementraui":
        text(d,"COMPONENT LIBRARY",658,115,9,color,"m")
        for j,(label,col) in enumerate([("BUTTON",(45,180,255)),("GLASS",(154,127,255)),("MOTION",(44,226,202))]):
            x=657+j*86
            d.rounded_rectangle((x,141,x+76,216),12,fill=(12,31,57,220),outline=(*col,170),width=1)
            d.rounded_rectangle((x+13,158,x+63,179),10,fill=(25,64,99,220),outline=(*col,180),width=1)
            d.ellipse((x+24,191,x+31,198),fill=(*col,220)); d.line((x+38,194,x+59,194),fill=ICE,width=2)
            text(d,label,x+38,204,7,MUTED,"m",anchor="ma")
        for k in range(5):
            xx=674+k*46+int(math.sin(phase+k)*3)
            d.ellipse((xx,247,xx+13,260),fill=(*[color,(64,178,255),(153,130,255),(74,223,206),(230,124,188)][k],235))
        text(d,"THEME TOKENS   ·   LIVE PREVIEWS",658,279,8,MUTED,"m")
    elif name=="tz-roms":
        # Phone shell and device tiles.
        d.rounded_rectangle((742,111,844,287),17,fill=(7,15,31,238),outline=(120,190,255,205),width=2)
        d.rounded_rectangle((750,127,836,272),9,fill=(12,36,63,235),outline=(74,157,220,100),width=1)
        d.rounded_rectangle((771,137,816,143),3,fill=(128,186,237,150))
        for k,label in enumerate(["POCO X6 PRO","DEVICE GUIDES","ROM RELEASES"]):
            yy=159+k*34
            d.rounded_rectangle((759,yy,827,yy+26),6,fill=(17,48,78,230),outline=(*color,130),width=1)
            text(d,label,793,yy+13,6,WHITE,"m",anchor="mm")
        for k,label in enumerate(["DEVICE","GUIDE","BUILD"]):
            yy=145+k*49
            d.rounded_rectangle((658,yy,722,yy+28),10,fill=(11,28,51,220),outline=(130,177,231,100),width=1)
            text(d,label,690,yy+14,7,MUTED,"m",anchor="mm")
            d.line((722,yy+14,742,yy+14),fill=(*color,180),width=2)
    elif name=="physifer":
        text(d,"CREATOR WORKFLOW",658,117,9,color,"m")
        d.rounded_rectangle((658,137,909,237),12,fill=(8,23,43,235),outline=(*color,135),width=1)
        d.ellipse((680,157,737,214),fill=(15,46,71,255),outline=(*color,210),width=2)
        d.polygon([(702,171),(702,200),(724,185)],fill=ICE)
        for k in range(29):
            xx=752+k*5
            h=8+int((math.sin(k*.76+phase*1.3)+1)*11)
            d.line((xx,188-h/2,xx,188+h/2),fill=(*color,175),width=2)
        d.line((670,223,899,223),fill=(122,175,213,100),width=1)
        for k in range(4):
            xx=672+k*58
            d.rounded_rectangle((xx,255,xx+48,277),7,fill=(14,38,62,220),outline=(105,168,218,100),width=1)
            text(d,["PLAN","EDIT","CAPTION","PUBLISH"][k],xx+24,266,6,WHITE,"m",anchor="mm")
    elif name=="tzlabs":
        text(d,"DIGITAL STUDIO",658,117,9,color,"m")
        # Three floating, translucent product surfaces with a moving prism glint.
        for k in range(3):
            xx=665+k*70; yy=153+(k%2)*22
            d.polygon([(xx,yy+12),(xx+44,yy),(xx+62,yy+8),(xx+18,yy+21)],fill=(30,82,119,180),outline=(*color,190))
            d.polygon([(xx,yy+12),(xx+18,yy+21),(xx+18,yy+63),(xx,yy+54)],fill=(8,34,61,220),outline=(115,190,240,120))
            d.polygon([(xx+18,yy+21),(xx+62,yy+8),(xx+62,yy+51),(xx+18,yy+63)],fill=(12,47,77,210),outline=(*color,150))
        sx=672+int((phase/math.tau%1)*192)
        d.line((sx,139,sx+24,278),fill=(225,248,255,100),width=2)
        text(d,"WEB   ·   SYSTEMS   ·   CREATIVE",658,283,8,MUTED,"m")
    elif name=="prayanone":
        text(d,"RAILWAY INFORMATION",658,117,9,color,"m")
        # Route map with moving station pulse.
        route=[(670,223),(724,178),(783,231),(846,169),(896,217)]
        d.line(route,fill=(44,116,178,145),width=12,joint="curve")
        d.line(route,fill=(*color,220),width=2,joint="curve")
        for k,(x,y) in enumerate(route):
            d.ellipse((x-8,y-8,x+8,y+8),fill=(9,27,48,255),outline=(184,228,255,225),width=2)
            d.ellipse((x-3,y-3,x+3,y+3),fill=(*color,255))
            d.rounded_rectangle((x-23,y+16,x+23,y+32),6,fill=(8,24,44,225),outline=(120,170,215,105),width=1)
            text(d,["START","MAP","TRAIN","INFO","ARRIVE"][k],x,y+24,5,WHITE,"m",anchor="mm")
        f=(phase/math.tau)%1; seg=min(3,int(f*4)); q=f*4-seg
        a,b=route[seg],route[seg+1]; xx=a[0]+(b[0]-a[0])*q; yy=a[1]+(b[1]-a[1])*q
        d.ellipse((xx-5,yy-5,xx+5,yy+5),fill=ICE)
    elif name=="greenera":
        text(d,"ORGANIC COMMERCE",658,117,9,color,"m")
        for k in range(3):
            xx=659+k*82
            d.rounded_rectangle((xx,145,xx+72,259),11,fill=(10,34,34,225),outline=(*color,150),width=1)
            d.rounded_rectangle((xx+19,164,xx+53,231),10,fill=(22,83,65,240),outline=(164,222,176,160),width=1)
            d.rounded_rectangle((xx+27,155,xx+45,166),4,fill=(150,214,173,230))
            d.ellipse((xx+25,185,xx+46,207),fill=(47,142,92,205),outline=(188,236,192,160),width=1)
            text(d,["CARE","SHOP","STORY"][k],xx+36,244,7,WHITE,"m",anchor="mm")
        d.arc((850,149,907,222),210,335,fill=(188,239,196,220),width=3)
        d.arc((865,156,917,235),35,150,fill=(*color,220),width=3)
    else:
        text(d,"SHOPPING EXPERIENCE",658,117,9,color,"m")
        for k in range(4):
            xx=660+(k%2)*126; yy=145+(k//2)*70
            d.rounded_rectangle((xx,yy,xx+111,yy+60),9,fill=(13,29,50,232),outline=(128,171,221,115),width=1)
            d.rounded_rectangle((xx+9,yy+8,xx+48,yy+50),7,fill=(*color,70),outline=(*color,145),width=1)
            d.ellipse((xx+20,yy+17,xx+37,yy+34),fill=(*color,190))
            d.line((xx+57,yy+19,xx+98,yy+19),fill=ICE,width=2)
            d.line((xx+57,yy+30,xx+91,yy+30),fill=(153,184,217,155),width=1)
            d.line((xx+57,yy+42,xx+79,yy+42),fill=(*color,180),width=2)
        x=872; y=218+int(math.sin(phase)*3)
        d.arc((x-19,y-20,x+19,y+24),180,360,fill=ICE,width=2)
        d.rounded_rectangle((x-24,y-5,x+24,y+33),5,fill=(15,46,74,220),outline=(*color,220),width=2)

def experience(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,153))
    chapter_rule(d,3,"Experience","digital work · creative practice",p)
    text(d,"Creative work, carried into digital products.",51,83,26,WHITE,"s")
    entries=[("2020 — 2024","Fiverr","Freelance · design & video",(65,157,255)),
             ("DATES NOT LISTED","Meesho","Supplier support executive",(110,178,255)),
             ("DATES NOT LISTED","Flipkart","Customer service associate",(157,139,255)),
             ("JAN 2026 — NOW","PHYSIFER","Social content & video editing",(178,119,255)),
             ("MAY — SEP 2026","GREENERA ORGANICS","Social media · e-commerce · site updates",(60,211,184))]
    x0=87; d.line((x0,133,x0,309),fill=(91,163,219,130),width=2)
    for k,(date,org,desc,color) in enumerate(entries):
        yy=139+k*42
        d.ellipse((x0-9,yy-9,x0+9,yy+9),fill=(5,18,38),outline=color,width=3)
        d.ellipse((x0-3,yy-3,x0+3,yy+3),fill=ICE)
        glass_panel(im,(126,yy-17,933,yy+17),p+k*.7,radius=13,blur=8,tint=(4,14,30,150),rim=False)
        d=ImageDraw.Draw(im)
        text(d,date,148,yy,9,color,"m",anchor="lm")
        text(d,org,320,yy-1,14,WHITE,"b",anchor="lm")
        text(d,desc,535,yy,11,MUTED,"r",anchor="lm")
        rainbow_border(im,(126,yy-17,933,yy+17),p+k*.55,radius=13,width=1,speed=.55)
    rainbow_border(im,(26,23,974,337),p,radius=25,width=2,speed=.68)

def toolkit(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,155))
    chapter_rule(d,4,"Toolkit","web · data · creative · operations",p)
    text(d,"The tools behind the work.",51,83,27,WHITE,"s")
    groups=[("01 / WEB","HTML · CSS · JavaScript · React · Vite"),
            ("02 / DATA","SQL · Excel · Sheets · dashboards · reporting"),
            ("03 / AI ASSISTED","ChatGPT · Claude · Gemini · Cursor"),
            ("04 / DIGITAL","SEO · Search Console · e-commerce · Amazon"),
            ("05 / CREATIVE","Canva · visual design · Filmora · editing")]
    for j,(head,items) in enumerate(groups):
        x=51+(j%2)*458; y=124+(j//2)*66
        glass_panel(im,(x,y,x+424,y+50),p+j*.36,radius=13,blur=6,tint=(5,17,37,170),rim=False)
        d=ImageDraw.Draw(im)
        text(d,head,x+13,y+9,10,CYAN,"m")
        text(d,items,x+13,y+30,12,WHITE,"r")
        rainbow_border(im,(x,y,x+424,y+50),p+j*.4,radius=13,width=1,speed=.5)
    draw_sphere(im,d,910,294,32,p,(100,167,255))
    rainbow_border(im,(26,23,974,337),p,radius=25,width=2,speed=.6)

def channels(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,155))
    chapter_rule(d,6,"Creator channels","technology · explainers · gameplay",p)
    text(d,"Technology, games, and stories.",51,83,27,WHITE,"s")
    names=[("Technoez Mobile","TECHNOLOGY",(28,166,255)),
           ("Shade Explains","GAMING EXPLAINERS",(157,104,255)),
           ("Dark Shade Gaming","GAMEPLAY",(255,94,127)),
           ("TZAILabs","AI CONTENT · UPCOMING",(45,220,206))]
    for k,(title,desc,col) in enumerate(names):
        x=45+k*229; y=144
        glass_panel(im,(x,y,x+209,y+146),p+k*.5,radius=19,blur=10,tint=(5,15,33,168),rim=False)
        d=ImageDraw.Draw(im)
        # Embedded play glyph rendered as a luminous glass control.
        d.ellipse((x+78,y+20,x+131,y+73),fill=(13,39,68),outline=col,width=2)
        d.polygon([(x+100,y+33),(x+100,y+60),(x+121,y+46)],fill=ICE)
        text(d,title,x+15,y+90,13,WHITE,"b")
        text(d,desc,x+15,y+119,9,col,"m")
        rainbow_border(im,(x,y,x+209,y+146),p+k*.43,radius=19,width=1,speed=.7)
    rainbow_border(im,(26,23,974,337),p,radius=25,width=2,speed=.65)

def contact(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,151))
    chapter_rule(d,7,"Connect","open to opportunities · projects · collaboration",p)
    text(d,"Let’s make something useful.",51,84,29,WHITE,"s")
    text(d,"Open to thoughtful conversations, freelance work, and collaborations.",53,116,14,MUTED,"r")
    labels=[("PORTFOLIO","me.technoezmobile.com",(40,174,255)),
            ("LINKEDIN","/in/itsxshivam",(90,159,255)),
            ("INSTAGRAM","@technoezmobile",(227,110,207)),
            ("YOUTUBE","@Technoez_Mobile",(251,93,117))]
    for k,(head,detail,col) in enumerate(labels):
        x=49+k*231; y=174
        glass_panel(im,(x,y,x+213,y+91),p+k*.4,radius=16,blur=8,tint=(5,17,37,170),rim=False)
        d=ImageDraw.Draw(im)
        text(d,head,x+15,y+20,10,col,"m")
        text(d,detail,x+15,y+54,12,WHITE,"b")
        rainbow_border(im,(x,y,x+213,y+91),p+k*.58,radius=16,width=1,speed=.62)
    text(d,"BUILD WITH CURIOSITY   /   SHIP WITH PURPOSE",52,298,11,ICE,"m")
    draw_sphere(im,d,908,289,31,p,(74,159,255))
    rainbow_border(im,(26,23,974,337),p,radius=25,width=2,speed=.72)

def shared_palette(frames, colors):
    """Build one palette from several animation phases so later frames keep real color detail."""
    sample=[]
    stride=max(1,len(frames)//6)
    for frame in frames[::stride]:
        sample.append(frame.convert("RGB").resize((240,86),Image.Resampling.LANCZOS))
    montage=Image.new("RGB",(240*len(sample),86))
    for ix,frame in enumerate(sample): montage.paste(frame,(ix*240,0))
    return montage.quantize(colors=min(256,colors),method=Image.Quantize.MEDIANCUT)

def render_gif(name, draw_fn, n=24, duration=100, colors=160, size=(800,288)):
    frames=[]
    for i in range(n):
        phase=math.tau*i/n
        im=canvas(phase); d=ImageDraw.Draw(im,"RGBA")
        draw_fn(im,d,phase,i,n)
        frame_border(im,phase)
        frames.append(im.resize(size,Image.Resampling.LANCZOS))
    palette=shared_palette(frames,colors)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(ASSETS/f"{name}.gif",save_all=True,append_images=indexed[1:],duration=duration,loop=0,optimize=True,disposal=1)
    # Keep the reduced-motion poster full-color; never reuse the lossy GIF palette.
    frames[0].save(ASSETS/f"{name}-poster.png",optimize=True)

def make_social_button(label, sub, icon, link_color, filename):
    sw,sh=500,130
    def draw_button(p,i,n):
        # Compact animated capsule translates the actual TZ Labs liquid-glass button material to README media.
        local=canvas(p).resize((sw,sh),Image.Resampling.LANCZOS)
        glass_panel(local,(8,8,sw-8,sh-8),p,radius=55,blur=11,tint=(4,14,31,161))
        d=ImageDraw.Draw(local,"RGBA")
        d.ellipse((31,36,92,97),fill=(11,34,61,215),outline=(*link_color,180),width=2)
        # Icons are purpose-built line glyphs, no external dependencies.
        cx,cy=61,66
        if icon=="play":
            d.polygon([(cx-8,cy-15),(cx+16,cy),(cx-8,cy+15)],fill=ICE)
        elif icon=="in":
            text(d,"in",cx,cy,25,ICE,"b",anchor="mm")
        elif icon=="camera":
            d.rounded_rectangle((cx-15,cy-12,cx+15,cy+12),5,outline=ICE,width=3); d.ellipse((cx-6,cy-6,cx+6,cy+6),outline=ICE,width=3); d.ellipse((cx+8,cy-9,cx+11,cy-6),fill=ICE)
        elif icon=="paper":
            d.polygon([(cx-17,cy-10),(cx+18,cy-17),(cx+8,cy+17),(cx+1,cy+2),(cx-9,cy+10),(cx-7,cy-1)],outline=ICE,fill=(44,114,177,185)); d.line((cx-7,cy-1,cx+9,cy-8),fill=ICE,width=2)
        elif icon=="diamond":
            d.polygon([(cx,cy-17),(cx+15,cy),(cx,cy+17),(cx-15,cy)],outline=ICE,fill=(25,78,134,160)); d.line((cx-15,cy,cx+15,cy),fill=ICE,width=2); d.line((cx,cy-17,cx,cy+17),fill=(173,222,255,180),width=2)
        elif icon=="mail":
            d.rounded_rectangle((cx-17,cy-12,cx+17,cy+12),4,outline=ICE,width=3); d.line((cx-15,cy-10,cx,cy+2,cx+15,cy-10),fill=ICE,width=2)
        elif icon=="github":
            d.ellipse((cx-14,cy-15,cx+14,cy+12),outline=ICE,width=3); d.arc((cx-11,cy-2,cx+11,cy+18),190,350,fill=ICE,width=3); d.ellipse((cx-6,cy-4,cx-3,cy-1),fill=ICE); d.ellipse((cx+3,cy-4,cx+6,cy-1),fill=ICE)
        else:
            d.rounded_rectangle((cx-15,cy-15,cx+15,cy+15),7,outline=ICE,width=2); d.ellipse((cx-6,cy-6,cx+6,cy+6),outline=ICE,width=2)
        text(d,label.upper(),112,47,16,WHITE,"b")
        text(d,sub,112,77,11,MUTED,"r")
        # Curved specular top and lower rim, matching the supplied BlueGlassButton layers.
        d.arc((118,17,468,83),185,355,fill=(255,255,255,113),width=2)
        d.line((128,14,468,14),fill=(219,241,255,65),width=1)
        rainbow_border(local,(8,8,sw-8,sh-8),p,radius=55,width=2,speed=.9)
        local=local.resize((400,104),Image.Resampling.LANCZOS)
        return local
    frames=[draw_button(math.tau*i/24,i,24) for i in range(24)]
    palette=shared_palette(frames,160)
    quant=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    quant[0].save(ASSETS/f"button-{filename}.gif",save_all=True,append_images=quant[1:],duration=95,loop=0,optimize=True,disposal=1)
    frames[0].save(ASSETS/f"button-{filename}-poster.png",optimize=True)

def build_all(contributions_only=False):
    if contributions_only:
        render_gif("contributions-motion",contributions,n=24,duration=115,colors=160)
        return
    render_gif("hero-motion",hero,n=24,duration=105,colors=160)
    render_gif("whoami-motion",identity,n=24,duration=105,colors=160)
    render_gif("contributions-motion",contributions,n=24,duration=115,colors=160)
    render_gif("experience-motion",experience,n=24,duration=110,colors=160)
    render_gif("toolkit-motion",toolkit,n=24,duration=110,colors=160)
    render_gif("channels-motion",channels,n=24,duration=105,colors=160)
    render_gif("contact-motion",contact,n=24,duration=105,colors=160)
    for spec in PROJECTS:
        name,title,kicker,sub,col=spec
        render_gif(f"project-{name}-motion",project(*spec),n=24,duration=105,colors=160)
    buttons=[("portfolio","PORTFOLIO","me.technoezmobile.com","diamond",(48,178,255)),
             ("linkedin","LINKEDIN","in / itsxshivam","in",(93,168,255)),
             ("instagram","INSTAGRAM","@technoezmobile","camera",(237,112,197)),
             ("youtube","YOUTUBE","@Technoez_Mobile","play",(250,85,117)),
             ("telegram","TELEGRAM","TZ Labs","paper",(41,184,232)),
             ("github","GITHUB","technoezmobile","github",(182,157,255)),
             ("email","EMAIL","contactme@technoezmobile.com","mail",(113,214,255))]
    for fn,label,sub,icon,col in buttons: make_social_button(label,sub,icon,col,fn)
    # An 8–9s MP4 stitches the same rendered motion language into a single reel.
    import cv2
    reel=[]
    names=["hero-motion","whoami-motion","contributions-motion","project-elementraui-motion","experience-motion","toolkit-motion","channels-motion","contact-motion"]
    for name in names:
        gif=Image.open(ASSETS/f"{name}.gif")
        for ix in range(0,gif.n_frames,max(1,gif.n_frames//6)):
            gif.seek(ix); frame=gif.convert("RGB").resize((800,288))
            reel.append(cv2.cvtColor(np.array(frame),cv2.COLOR_RGB2BGR))
    video=cv2.VideoWriter(str(ASSETS/"profile-motion-reel.mp4"),cv2.VideoWriter_fourcc(*"mp4v"),10,(800,288))
    for frame in reel: video.write(frame)
    video.release()
    print(f"Rendered {len(list(ASSETS.glob('*-motion.gif')))} animated panels and {len(buttons)} liquid-glass social buttons")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--contributions-only",action="store_true")
    build_all(parser.parse_args().contributions_only)

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

def font(size, kind="r"):
    p = {"b": FONT_B, "r": FONT_R, "m": FONT_M}[kind]
    if not Path(p).exists():
        p = {"b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "r": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "m": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"}[kind]
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
        (.70 + .11*math.sin(phase*.62), .22 + .15*math.cos(phase*.53), .29, (9, 72, 190), .72),
        (.39 + .15*math.cos(phase*.47), .83 + .08*math.sin(phase*.71), .36, (37, 31, 145), .55),
        (.91 + .035*math.sin(phase*.55), .56 + .16*math.cos(phase*.41), .27, (0, 112, 155), .48),
        (.18 + .055*math.sin(phase*.39), .37 + .1*math.cos(phase*.57), .27, (65, 22, 124), .35),
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
    """Shaded, rotating latitude/longitude orb with lens bloom and a 3D orbital ring."""
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
    # Perspective-projected longitude and latitude curves on a rotating sphere.
    line_layer=Image.new("RGBA",im.size,(0,0,0,0)); ld=ImageDraw.Draw(line_layer)
    ca,sa=math.cos(phase*.7),math.sin(phase*.7); cb,sb=math.cos(phase*.43),math.sin(phase*.43)
    def project(x,y,z):
        x1=x*ca-z*sa; z1=x*sa+z*ca
        y1=y*cb-z1*sb; z2=y*sb+z1*cb
        persp=3.1/(3.1+z2*.25)
        return (cx+x1*r*.98*persp,cy+y1*r*.98*persp,z2)
    for lat in [-1.0,-.58,-.2,.2,.58,1.0]:
        pts=[]
        for k in range(97):
            a=k*math.tau/96; q=math.sqrt(max(0,1-lat*lat))
            pts.append(project(q*math.cos(a),lat,q*math.sin(a)))
        for a,b in zip(pts,pts[1:]):
            if (a[2]+b[2])>-.1:
                ld.line((a[0],a[1],b[0],b[1]),fill=(*accent,82),width=1)
    for mer in np.linspace(0,math.pi,8,endpoint=False):
        pts=[]
        for k in range(97):
            lat=-math.pi/2+k*math.pi/96
            x=math.cos(lat)*math.cos(mer); z=math.cos(lat)*math.sin(mer); y=math.sin(lat)
            pts.append(project(x,y,z))
        for a,b in zip(pts,pts[1:]):
            if (a[2]+b[2])>-.1:
                ld.line((a[0],a[1],b[0],b[1]),fill=(*ICE,80),width=1)
    im.paste(Image.alpha_composite(im.convert("RGBA"),line_layer).convert("RGB"))
    # Foreground ring segment and an orbiting satellite make depth and rotation obvious.
    d=ImageDraw.Draw(im)
    d.arc((cx-r*1.36,cy-r*.40,cx+r*1.36,cy+r*.40),int((phase*42)%360),int((phase*42)%360)+148,fill=ICE,width=3)
    a=phase*1.1
    sx=cx+math.cos(a)*r*1.34; sy=cy+math.sin(a)*r*.38
    d.ellipse((sx-5,sy-5,sx+5,sy+5),fill=ICE)

def frame_border(im,phase):
    rainbow_border(im,(6,6,W-7,H-7),phase,radius=18,width=2,speed=.62)

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
    # Portrait card, with concentric orbital light and a small travelling locator.
    px,py=172,182
    for rad,col,w in [(142,(30,144,255),2),(150,(118,93,255),1),(160,(57,203,255),1)]:
        d.ellipse((px-rad,py-rad,px+rad,py+rad),outline=(*col,130),width=w)
    d.arc((px-165,py-165,px+165,py+165),int((p*38)%360),int((p*38)%360)+120,fill=ICE,width=3)
    point=(px+math.cos(p)*160,py+math.sin(p)*160)
    d.ellipse((point[0]-4,point[1]-4,point[0]+4,point[1]+4),fill=ICE)
    portrait=Image.open(ASSETS/"Studio Portrait with Folded Arms.png").convert("RGB")
    portrait=ImageEnhance.Color(portrait).enhance(.92).resize((254,254),Image.Resampling.LANCZOS)
    mask=Image.new("L",portrait.size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,253,253),30,fill=255)
    im.paste(portrait,(px-127,py-127),mask)
    d=ImageDraw.Draw(im); d.rounded_rectangle((px-129,py-129,px+129,py+129),30,outline=(215,240,255,210),width=2)
    # The main identity card follows the clear editorial layout of the reference profile.
    text(d,"IDENTITY CARD     /     TECHNoEZ MOBILE",368,65,12,ICE,"m")
    text(d,"Shivam Singh",364,103,34,WHITE,"b")
    text(d,"AI-ASSISTED WEB DEVELOPER",366,151,15,CYAN,"m")
    text(d,"Computer Science  ·  AI & Machine Learning",366,184,15,WHITE,"r")
    text(d,"Digital products, thoughtful interfaces, and creator work.",366,214,14,MUTED,"r")
    capsule(im,d,"CSE  /  CLASS OF 2027",(366,244,588,281),p,color=(114,170,255),size=11)
    capsule(im,d,"WEB  ·  AI  ·  DIGITAL",(603,244,813,281),p+1.5,color=(205,115,255),size=11)
    # Numeric identity mark and depth detail, not invented achievement stats.
    text(d,"CREATOR  ·  BUILDER  ·  LEARNER",366,305,11,MUTED,"m")
    text(d,"ID  001 /  TECH  ×  DESIGN",941,306,10,CYAN,"m",anchor="ra")
    rainbow_border(im,(26,24,974,336),p,radius=27,width=2,speed=.84)

def contributions(im,d,p,i,n):
    glass_panel(im,(24,22,976,338),p,radius=26,blur=16,tint=(4,13,29,158))
    text(d,"02  /  CONTRIBUTION SIGNAL",53,46,12,ICE,"m")
    text(d,"A year in motion.",51,75,29,WHITE,"b")
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
    text(d,f"{total} PUBLIC CONTRIBUTIONS",54,286,12,CYAN,"m")
    text(d,f"{active_days} ACTIVE DAYS  ·  DAILY REFRESH",54,307,10,MUTED,"m")
    text(d,"PUBLIC DATA  /  PRIVATE ACTIVITY EXCLUDED",946,310,9,MUTED,"m",anchor="ra")
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
        text(d,"03  /  SELECTED WORK",47,37,12,ICE,"m")
        glass_panel(im,(26,67,974,329),p,radius=25,blur=18,tint=(4,13,29,157))
        d=ImageDraw.Draw(im)
        text(d,"FEATURED PROJECT",61,93,11,color,"m")
        text(d,title,59,124,34,WHITE,"b")
        text(d,kicker,62,175,13,color,"m")
        text(d,sub,62,209,15,WHITE,"r")
        # Floating TzLabs-style glass action, with an always-visible thin spectrum rim.
        capsule(im,d,"EXPLORE PROJECT  ↗",(61,257,289,299),p+1,color=color,size=12)
        draw_sphere(im,d,781,196,86,p,color)
        d=ImageDraw.Draw(im)
        text(d,"HOLOGRAPHIC PREVIEW",781,300,9,MUTED,"m",anchor="ma")
        rainbow_border(im,(26,67,974,329),p,radius=25,width=2,speed=.72)
    return lambda im,d,p,i,n:draw(im,d,p,i,n)

def experience(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,153))
    text(d,"04  /  EXPERIENCE",52,47,12,ICE,"m")
    text(d,"Creative work, carried into digital products.",51,77,27,WHITE,"b")
    entries=[("2020 — 2024","Fiverr","Graphic design & video editing",(65,157,255)),
             ("JAN 2026 — NOW","PHYSIFER","Social content & video editing",(178,119,255)),
             ("MAY — SEP 2026","GREENERA ORGANICS","Social media, e-commerce & site customization",(60,211,184))]
    x0=87; d.line((x0,141,x0,299),fill=(91,163,219,130),width=2)
    for k,(date,org,desc,color) in enumerate(entries):
        yy=148+k*70
        d.ellipse((x0-9,yy-9,x0+9,yy+9),fill=(5,18,38),outline=color,width=3)
        d.ellipse((x0-3,yy-3,x0+3,yy+3),fill=ICE)
        glass_panel(im,(126,yy-27,933,yy+29),p+k*.7,radius=16,blur=8,tint=(4,14,30,150),rim=False)
        d=ImageDraw.Draw(im)
        text(d,date,148,yy,11,color,"m",anchor="lm")
        text(d,org,355,yy-1,17,WHITE,"b",anchor="lm")
        text(d,desc,568,yy,13,MUTED,"r",anchor="lm")
        rainbow_border(im,(126,yy-27,933,yy+29),p+k*.55,radius=16,width=1,speed=.55)
    rainbow_border(im,(26,23,974,337),p,radius=25,width=2,speed=.68)

def toolkit(im,d,p,i,n):
    glass_panel(im,(26,23,974,337),p,radius=25,blur=16,tint=(4,13,29,155))
    text(d,"05  /  TOOLKIT",52,47,12,ICE,"m")
    text(d,"The tools behind the work.",51,78,29,WHITE,"b")
    groups=[("01 / WEB","HTML · CSS · TypeScript · React · Vite · Tailwind"),
            ("02 / DATA","SQL · Excel · Sheets · dashboards · reporting"),
            ("03 / AI","ChatGPT · Claude · Gemini · Cursor · prompt design"),
            ("04 / DIGITAL","SEO · Search Console · e-commerce · Amazon listings"),
            ("05 / CREATIVE","Canva · visual design · Filmora · video editing")]
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
    text(d,"06  /  CREATOR CHANNELS",52,47,12,ICE,"m")
    text(d,"Technology, games, and stories.",51,78,29,WHITE,"b")
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
    text(d,"07  /  CONNECT",52,47,12,ICE,"m")
    text(d,"Let's make something useful.",51,79,31,WHITE,"b")
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

def render_gif(name, draw_fn, n=28, duration=95, colors=96, size=(800,288)):
    frames=[]
    for i in range(n):
        phase=math.tau*i/n
        im=canvas(phase); d=ImageDraw.Draw(im,"RGBA")
        draw_fn(im,d,phase,i,n)
        frame_border(im,phase)
        frames.append(im.resize(size,Image.Resampling.LANCZOS))
    palette=frames[0].convert("P",palette=Image.Palette.ADAPTIVE,colors=colors)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    palette.save(ASSETS/f"{name}.gif",save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=1)
    palette.convert("RGB").save(ASSETS/f"{name}-poster.png",optimize=True)

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
    palette=frames[0].convert("P",palette=Image.Palette.ADAPTIVE,colors=96)
    quant=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    palette.save(ASSETS/f"button-{filename}.gif",save_all=True,append_images=quant[1:],duration=95,loop=0,optimize=True,disposal=1)
    palette.convert("RGB").save(ASSETS/f"button-{filename}-poster.png",optimize=True)

def build_all(contributions_only=False):
    if contributions_only:
        render_gif("contributions-motion",contributions,n=28,duration=120,colors=96)
        return
    render_gif("hero-motion",hero,n=32,duration=105,colors=144)
    render_gif("whoami-motion",identity,n=32,duration=100,colors=144)
    render_gif("contributions-motion",contributions,n=32,duration=120,colors=96)
    render_gif("experience-motion",experience,n=28,duration=110,colors=96)
    render_gif("toolkit-motion",toolkit,n=28,duration=110,colors=96)
    render_gif("channels-motion",channels,n=28,duration=105,colors=96)
    render_gif("contact-motion",contact,n=28,duration=105,colors=96)
    for spec in PROJECTS:
        name,title,kicker,sub,col=spec
        render_gif(f"project-{name}-motion",project(*spec),n=28,duration=105,colors=96)
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

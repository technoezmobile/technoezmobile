"""Render the profile using authentic project media and readable navigation.

Source screenshots are copied from Shivam's portfolio; PHYSIFER frames come
from its checked-in hero sequence. Keep original source files untouched.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter
import math
import render_motion_profile as ui

ASSETS = ui.ASSETS

def save_animation(name, frames, duration=125, static_rects=()):
    # Full-size samples retain photographic color detail in the shared palette.
    sample = Image.new('RGB', (frames[0].width * 4, frames[0].height))
    for k, ix in enumerate((0, len(frames)//4, len(frames)//2, 3*len(frames)//4)):
        sample.paste(frames[ix], (k*frames[0].width, 0))
    palette = sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    # Preserve fixed photographic pixels across frames so dithering of the
    # moving rim cannot introduce noise into a static photograph or screenshot.
    for box in static_rects:
        fixed=indexed[0].crop(box)
        for frame in indexed[1:]: frame.paste(fixed,box)
    indexed[0].save(ASSETS/f'{name}.gif', save_all=True, append_images=indexed[1:],
                    duration=duration, loop=0, optimize=True, disposal=1)
    frames[0].save(ASSETS/f'{name}-poster.png', optimize=True)

def project_card(spec):
    name, title, kicker, sub, color = spec
    source = ASSETS / 'project-sources' / f'{name}.jpg'
    sequence = sorted((ASSETS/'project-sources'/'physifer').glob('*.webp')) if name == 'physifer' else []
    frames=[]
    for i in range(32):
        p = math.tau*i/32
        im = Image.new('RGB', (1000, 638), (8, 15, 29))
        d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((9,9,990,628), 24, fill=(13,23,40), outline=(77,99,125), width=1)
        ui.text(d, title, 30, 28, 29, ui.WHITE, 'b')
        ui.text(d, 'SHIVAM SINGH / SELECTED WORK', 964, 41, 12, ui.MUTED, 'm', anchor='ra')
        # Play the source sequence forward and backward for a seamless loop.
        sequence_ix=min(i,32-i)*2 if sequence else 0
        image = Image.open(sequence[min(sequence_ix,len(sequence)-1)] if sequence else source).convert('RGB')
        image = ImageOps.fit(image, (944, 486), method=Image.Resampling.LANCZOS)
        mask=Image.new('L',image.size,0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,943,485), 12, fill=255)
        im.paste(image,(28,82),mask)
        d=ImageDraw.Draw(im,'RGBA')
        d.rounded_rectangle((28,82,971,567),12,outline=(221,235,255,90),width=1)
        ui.text(d,kicker,31,600,14,ui.ICE,'m',anchor='lm')
        ui.text(d,'VIEW PROJECT  >',964,600,17,ui.WHITE,'b',anchor='rm')
        ui.rainbow_border(im,(10,10,989,627),p,radius=24,width=3,speed=1)
        frames.append(im.resize((800,510) if sequence else (900,574),Image.Resampling.LANCZOS))
    save_animation(f'project-{name}-motion',frames,static_rects=() if sequence else ((24,72,876,512),))

def button(label, slug):
    # Displayed at 230px: this 32px source label reads as a 15px bold label.
    frames=[]
    for i in range(32):
        p=math.tau*i/32
        im=Image.new('RGB',(480,112),(7,13,24))
        d=ImageDraw.Draw(im,'RGBA')
        d.rounded_rectangle((5,5,474,106),32,fill=(13,28,49),outline=(116,155,192,165),width=2)
        d.rounded_rectangle((12,10,467,51),26,fill=(57,91,125,42))
        d.line((43,12,436,12),fill=(219,238,255,100),width=2)
        ui.rainbow_border(im,(5,5,474,106),p,radius=32,width=3,speed=1)
        # Text is drawn last and stays fully opaque throughout the motion.
        d=ImageDraw.Draw(im,'RGBA')
        ui.text(d,label,224,56,32,(255,255,255),'b',anchor='mm')
        ui.text(d,'↗',427,56,31,(218,241,255),'r',anchor='mm')
        frames.append(im)
    save_animation(f'button-{slug}',frames)

def identity():
    portrait = Image.open(ASSETS/'Studio Portrait with Folded Arms.png').convert('RGB')
    # A proper rounded photo window preserves the portrait's proportions.
    portrait = ImageOps.fit(portrait,(276,276),method=Image.Resampling.LANCZOS,centering=(.5,.35))
    frames=[]
    for i in range(32):
        p=math.tau*i/32
        im=ui.canvas(p)
        d=ImageDraw.Draw(im,'RGBA')
        d.rounded_rectangle((12,12,988,348),24,fill=(4,12,26,239),outline=(163,195,225,70),width=1)
        d.line((45,17,953,17),fill=(217,240,255,42),width=1)
        mask=Image.new('L',portrait.size,0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,275,275),22,fill=255)
        im.paste(portrait,(688,42),mask)
        d=ImageDraw.Draw(im,'RGBA')
        d.rounded_rectangle((688,42,963,317),22,outline=(212,236,255,150),width=1)
        ui.text(d,'01  /  ABOUT ME',38,43,13,ui.CYAN,'m')
        ui.text(d,'Shivam Singh',36,79,47,ui.WHITE,'s')
        ui.text(d,'AI-assisted Web Developer',39,151,23,ui.ICE,'b')
        ui.text(d,'Computer Science · AI & Machine Learning',39,194,18,ui.WHITE)
        ui.text(d,'Web products. Digital experiences. Creator platforms.',39,226,17,(192,209,230))
        ui.text(d,'B.TECH / CLASS OF 2027',39,281,15,ui.CYAN,'m')
        ui.text(d,'RGPV, BHOPAL',39,309,13,(192,209,230),'m')
        ui.rainbow_border(im,(12,12,988,348),p,radius=24,width=2,speed=1)
        frames.append(im)
    save_animation('whoami-motion',frames,static_rects=((688,42,964,318),))

def channels():
    channel_names=[('Technoez Mobile','TECHNOLOGY','technoez'),('Shade Explains','GAME EXPLAINERS','shade-explains'),('Dark Shade Gaming','GAMING','dark-shade'),('TZAILabs','AI / UPCOMING','tzailabs')]
    frames=[]
    for i in range(32):
        p=math.tau*i/32
        im=Image.new('RGB',(1000,380),(7,14,27)); d=ImageDraw.Draw(im,'RGBA')
        ui.text(d,'Technology, games, and stories.',32,26,29,ui.WHITE,'s')
        for k,(title,desc,slug) in enumerate(channel_names):
            x=24+k*244
            logo=Image.open(ASSETS/'channel-sources'/f'{slug}.jpg').convert('RGB')
            logo=ImageOps.fit(logo,(202,202),method=Image.Resampling.LANCZOS)
            mask=Image.new('L',logo.size,0); ImageDraw.Draw(mask).rounded_rectangle((0,0,201,201),16,fill=255)
            im.paste(logo,(x+13,88),mask)
            d=ImageDraw.Draw(im,'RGBA')
            ui.text(d,title,x+114,315,17,ui.WHITE,'b',anchor='mm')
            ui.text(d,desc,x+114,345,12,ui.ICE,'m',anchor='mm')
            ui.rainbow_border(im,(x,74,x+228,366),p+k*math.pi/2,radius=20,width=2,speed=1)
        frames.append(im)
    save_animation('channels-motion',frames,static_rects=tuple((37+k*244,88,239+k*244,290) for k in range(4)))

def main():
    for spec in ui.PROJECTS: project_card(spec)
    for label,slug in [('PORTFOLIO','portfolio'),('LINKEDIN','linkedin'),('GITHUB','github'),('INSTAGRAM','instagram'),('YOUTUBE','youtube'),('TELEGRAM','telegram'),('EMAIL','email')]: button(label,slug)
    identity(); channels()
    # Full-color original banner is resized once; motion stays on its perimeter.
    banner=Image.open(ASSETS/'Shivam Singh_ AI Innovation Banner.png').convert('RGB').resize((1000,375),Image.Resampling.LANCZOS)
    frames=[]
    for i in range(32):
        frame=banner.copy(); ui.rainbow_border(frame,(3,3,996,371),math.tau*i/32,radius=14,width=3,speed=1); frames.append(frame)
    save_animation('hero-motion',frames,static_rects=((16,16,984,359),))
    # Remove the decorative wireframe spheres from the supporting panels.
    import render_support_sections
    render_support_sections.main()
    print('Rendered authentic project cards, channel art, portrait, banner and readable buttons.')

if __name__=='__main__': main()

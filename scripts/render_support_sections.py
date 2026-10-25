"""Roomy editorial supporting sections for the profile; accurate, readable content."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFilter
import json,math,datetime
import render_motion_profile as ui
from render_profile_photography import save_animation
AS=ui.ASSETS
WHITE=(242,247,255);MUTED=(172,191,214);CYAN=(78,208,255)
def text(im,s,x,y,n=22,c=WHITE,k='r',anchor=None):ui.text(ImageDraw.Draw(im),s,x,y,n,c,k,anchor)
def base(h,number,title,subtitle,p):
    im=Image.new('RGB',(1000,h),(7,13,24));d=ImageDraw.Draw(im,'RGBA')
    # Quiet light field is confined behind the content instead of crossing text.
    glow=Image.new('RGBA',im.size,(0,0,0,0));g=ImageDraw.Draw(glow)
    g.ellipse((600+20*math.sin(p),-180,1150,240),fill=(25,102,171,75))
    im=Image.alpha_composite(im.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(80))).convert('RGB')
    text(im,f'{number} / SHIVAM SINGH',32,30,15,CYAN,'m')
    text(im,title,29,73,43,WHITE,'s');text(im,subtitle,32,139,21,MUTED)
    ui.rainbow_border(im,(5,5,994,h-6),p,radius=24,width=2,speed=1)
    return im
def pane(im,box,p,r=20):
    d=ImageDraw.Draw(im,'RGBA');d.rounded_rectangle(box,r,fill=(18,31,49,245),outline=(96,128,163,90),width=1)
    ui.rainbow_border(im,box,p,radius=r,width=1,speed=1)
def logo(im,name,x,y,size=42):
    path=AS/'tool-icons'/f'{name}.png'
    if path.exists():
        icon=Image.open(path).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS);im.paste(icon,(x,y),icon)
    elif name=='sql':
        d=ImageDraw.Draw(im);d.ellipse((x,y,x+size,y+12),outline=WHITE,width=2);d.line((x,y+6,x,y+size-8),fill=WHITE,width=2);d.line((x+size,y+6,x+size,y+size-8),fill=WHITE,width=2);d.arc((x,y+size-14,x+size,y+size-1),0,180,fill=WHITE,width=2);d.arc((x,y+12,x+size,y+25),0,180,fill=WHITE,width=2)
    else:text(im,name,x,y,23,CYAN,'b')
def thumb(im,source,box):
    x,y,w,h=box;photo=ImageOps.fit(Image.open(source).convert('RGB'),(w,h),method=Image.Resampling.LANCZOS)
    mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),12,fill=255);im.paste(photo,(x,y),mask)
def experience(p):
    im=base(820,'03','Experience, with context.','Creative production, e-commerce, and digital operations.',p)
    entries=[('JAN 2026 - PRESENT','PHYSIFER','Social content management','Video editing and creative production','physifer'),('MAY - SEP 2026','Greenera Organics','Social media and e-commerce support','Website customization and updates','greenera'),('2020 - 2024','Fiverr','Freelance design and video editing','Client-focused creative production','fiverr'),('EARLIER ROLES','Meesho + Flipkart','Supplier support / customer service','Additional experience in digital operations','operations')]
    d=ImageDraw.Draw(im);d.line((41,220,41,726),fill=(53,81,112),width=2)
    for k,(date,org,a,b,kind) in enumerate(entries):
        y=193+k*148;pane(im,(73,y,966,y+133),p+k*.5)
        d=ImageDraw.Draw(im);d.ellipse((34,y+24,48,y+38),fill=CYAN if k==0 else (79,110,142))
        text(im,date,95,y+14,14,CYAN,'m');text(im,org,94,y+39,27,WHITE,'b')
        text(im,a,96,y+81,20,WHITE);text(im,b,96,y+108,17,MUTED)
        if kind=='physifer':thumb(im,AS/'project-sources'/'physifer'/'frame_0000.webp',(746,y+16,199,101))
        elif kind=='greenera':thumb(im,AS/'project-sources'/'greenera.jpg',(746,y+16,199,101))
        elif kind=='fiverr':logo(im,'fiverr',814,y+40,58)
        else:text(im,'M / F',845,y+66,28,MUTED,'m',anchor='mm')
    return im
def toolkit(p):
    im=base(870,'04','A practical toolkit.','Tools I use across web, AI-assisted work, data, and content.',p)
    groups=[('WEB / BUILDS',[('html5','HTML'),('css','CSS'),('javascript','JavaScript'),('react','React'),('vite','Vite')]),('AI / WORKFLOWS',[('openai','ChatGPT'),('claude','Claude'),('googlegemini','Gemini'),('cursor','Cursor')]),('DATA / CREATIVE',[('sql','SQL'),('microsoftexcel','Excel'),('googlesheets','Google Sheets'),('canva','Canva'),('wondersharefilmora','Filmora')])]
    for k,(head,items) in enumerate(groups):
        x=28+k*324;pane(im,(x,195,x+296,744),p+k*.7)
        text(im,head,x+20,218,17,CYAN,'m')
        for j,(slug,label) in enumerate(items):
            y=280+j*88;d=ImageDraw.Draw(im);d.rounded_rectangle((x+18,y-7,x+78,y+53),13,fill=(31,49,71))
            logo(im,slug,x+29,y+4,38);text(im,label,x+94,y+21,22,WHITE,'b',anchor='lm')
    text(im,'DIGITAL OPERATIONS',32,785,16,CYAN,'m')
    text(im,'SEO  /  Search Console  /  E-commerce  /  Reporting',32,818,22,WHITE)
    return im
def buildlog(p):
    data=json.loads((ui.ROOT/'data'/'contributions.json').read_text(encoding='utf-8'))
    days=data.get('days',[]);total=sum(int(x[1]) for x in days);active=sum(x[1]>0 for x in days);best=max((x[1] for x in days),default=0)
    im=base(690,'05','The build log.','A transparent view of public GitHub activity.',p)
    stats=[(str(total),'PUBLIC CONTRIBUTIONS'),(str(active),'ACTIVE DAYS'),(str(best),'BEST PUBLIC DAY')]
    for k,(val,label) in enumerate(stats):
        x=28+k*324;pane(im,(x,195,x+296,328),p+k*.6)
        text(im,val,x+22,211,50,WHITE,'b');text(im,label,x+23,283,14,CYAN,'m')
    pane(im,(28,353,972,615),p)
    text(im,'PUBLIC CONTRIBUTION CALENDAR',49,374,16,WHITE,'m')
    if days:
        dates=[datetime.date.fromisoformat(x[0]) for x in days];start=dates[0]-datetime.timedelta(days=(dates[0].weekday()+1)%7)
        colors=[(29,45,63),(23,75,95),(23,116,142),(40,168,190),(117,230,236)]
        gx,gy,step,cell=51,435,16,12;lastmonth=None
        for row,day in zip(days,dates):
            diff=(day-start).days;col,weekrow=divmod(diff,7);x=gx+col*step;y=gy+weekrow*step
            level=max(0,min(4,int(row[2])))
            ImageDraw.Draw(im).rounded_rectangle((x,y,x+cell,y+cell),3,fill=colors[level])
            if day.month!=lastmonth:
                if day.day<=7 and x<925:text(im,day.strftime('%b'),x,412,12,MUTED,'m')
                lastmonth=day.month
        text(im,dates[0].isoformat()+'  to  '+dates[-1].isoformat(),50,575,14,MUTED,'m')
    text(im,'Counts stay accurate. Only the frame moves.',32,640,18,MUTED)
    text(im,'PUBLIC ACTIVITY ONLY',966,644,13,CYAN,'m',anchor='ra')
    return im
LINKS=[('portfolio','Portfolio','me.technoezmobile.com','web'),('linkedin','LinkedIn','in/itsxshivam','linkedin'),('instagram','Instagram','@technoezmobile','instagram'),('youtube','YouTube','@Technoez_Mobile','youtube'),('telegram','Telegram','TZ Labs / tzlabss','telegram'),('email','Email','contactme@technoezmobile.com','mail')]
def connect(p):
    im=base(750,'07','Let’s build something useful.','Web projects, creative collaborations, and thoughtful conversations.',p)
    pane(im,(28,195,972,344),p)
    text(im,'OPEN TO',50,218,16,CYAN,'m')
    text(im,'Web development / Freelance projects',49,252,30,WHITE,'b')
    text(im,'Technology content and creative work',51,300,21,MUTED)
    for k,(slug,title,detail,icon) in enumerate(LINKS):
        x=28+(k%2)*486;y=371+(k//2)*104;pane(im,(x,y,x+458,y+86),p+k*.4,r=18)
        if slug=='email':
            d=ImageDraw.Draw(im);d.rounded_rectangle((x+20,y+25,x+52,y+49),4,outline=WHITE,width=2);d.line((x+21,y+26,x+36,y+38,x+51,y+26),fill=WHITE,width=2)
        elif slug=='portfolio':
            d=ImageDraw.Draw(im);d.ellipse((x+20,y+23,x+52,y+55),outline=WHITE,width=2);d.ellipse((x+29,y+23,x+43,y+55),outline=WHITE,width=2);d.line((x+21,y+39,x+51,y+39),fill=WHITE,width=2)
        else:logo(im,icon,x+20,y+23,31)
        text(im,title,x+70,y+15,23,WHITE,'b');text(im,detail,x+71,y+51,17,MUTED)
        text(im,'>',x+429,y+42,25,CYAN,'r',anchor='mm')
    text(im,'Choose a link below to start a conversation.',32,710,18,MUTED)
    return im
def main(only=None):
    fns={'experience-motion':experience,'toolkit-motion':toolkit,'contributions-motion':buildlog,'contact-motion':connect}
    for name,fn in fns.items():
        if only and name!=only:continue
        frames=[fn(math.tau*i/32) for i in range(32)]
        # Moving rims stay outside the photographed/text-heavy panel interiors.
        if name=='contact-motion':
            save_animation('contact-overview-motion',frames)
            for k,(slug,*_) in enumerate(LINKS):
                x=28+(k%2)*486;y=371+(k//2)*104
                save_animation('contact-link-'+slug,[f.crop((x-2,y-2,x+461,y+89)) for f in frames])
            header=[]
            for i in range(32):
                p=math.tau*i/32
                small=base(366,'07','Let’s build something useful.','Web projects, creative collaborations, and thoughtful conversations.',p)
                pane(small,(28,195,972,344),p)
                text(small,'OPEN TO',50,218,16,CYAN,'m');text(small,'Web development / Freelance projects',49,252,30,WHITE,'b');text(small,'Technology content and creative work',51,300,21,MUTED)
                header.append(small)
            save_animation(name,header)
        else:save_animation(name,frames,static_rects=())
        print('Rendered',name,frames[0].size,flush=True)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--contributions-only',action='store_true')
    main('contributions-motion' if parser.parse_args().contributions_only else None)

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path(__file__).resolve().parent
BG = "#FFFFFF"
INK = "#18212B"
BLUE = "#2463A6"
PALE = "#EAF2FA"
GRAY = "#F1F3F5"
MID = "#667085"

try:
    FONT = ImageFont.truetype("arial.ttf", 30)
    SMALL = ImageFont.truetype("arial.ttf", 24)
    TINY = ImageFont.truetype("arial.ttf", 21)
    BOLD = ImageFont.truetype("arialbd.ttf", 34)
    TITLE = ImageFont.truetype("arialbd.ttf", 44)
except OSError:
    FONT = SMALL = TINY = BOLD = TITLE = ImageFont.load_default()


def canvas(w, h, title):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((w/2, 34), title, fill=INK, font=TITLE, anchor="ma")
    d.line((50, 95, w-50, 95), fill=BLUE, width=5)
    return im, d


def wrapped(draw, text, font, max_width):
    lines=[]
    for para in text.split("\n"):
        words=para.split(); line=""
        for word in words:
            trial=(line+" "+word).strip()
            if draw.textbbox((0,0),trial,font=font)[2] <= max_width: line=trial
            else:
                if line: lines.append(line)
                line=word
        lines.append(line)
    return lines


def box(draw, xy, title, sub="", fill=PALE, font=BOLD, subfont=SMALL, radius=22):
    x1,y1,x2,y2=xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=INK, width=3)
    lines=wrapped(draw,title,font,x2-x1-40)
    sublines=wrapped(draw,sub,subfont,x2-x1-40) if sub else []
    allh=len(lines)*font.size + len(sublines)*subfont.size + (12 if sublines else 0)
    y=(y1+y2-allh)/2
    for line in lines:
        draw.text(((x1+x2)/2,y),line,fill=INK,font=font,anchor="ma"); y+=font.size+3
    if sublines:
        y+=7
        for line in sublines:
            draw.text(((x1+x2)/2,y),line,fill=MID,font=subfont,anchor="ma"); y+=subfont.size+3


def arrow(draw, a, b, label=None, color=INK):
    draw.line((a,b), fill=color, width=4)
    ang=math.atan2(b[1]-a[1],b[0]-a[0]); length=17
    pts=[b,(b[0]-length*math.cos(ang-0.55),b[1]-length*math.sin(ang-0.55)),(b[0]-length*math.cos(ang+0.55),b[1]-length*math.sin(ang+0.55))]
    draw.polygon(pts,fill=color)
    if label:
        mx=(a[0]+b[0])/2; my=(a[1]+b[1])/2
        draw.rounded_rectangle((mx-68,my-20,mx+68,my+19),radius=7,fill=BG)
        draw.text((mx,my),label,fill=BLUE,font=TINY,anchor="mm")


def flowchart():
    w,h=1700,2200; im,d=canvas(w,h,"3.4.1  SYSTEM FLOWCHART")
    cx=850; bw=760; left=cx-bw//2
    def terminal(x,y,label):
        d.rounded_rectangle((x-205,y-45,x+205,y+45),radius=45,fill=GRAY,outline=INK,width=3)
        d.text((x,y),label,fill=INK,font=SMALL,anchor="mm")
    def decision(y,label):
        pts=[(cx,y-70),(cx+205,y),(cx,y+70),(cx-205,y)]
        d.polygon(pts,fill=GRAY,outline=INK); d.line(pts+[pts[0]],fill=INK,width=3)
        d.text((cx,y),label,fill=INK,font=SMALL,anchor="mm")
    terminal(cx,145,"Start: collection request")
    box(d,(left,260,left+bw,390),"Validate request","Check channel handle and max_videos constraints")
    decision(510,"Request valid?")
    box(d,(45,465,390,555),"Return 422","Validation error",fill=GRAY,font=SMALL,subfont=TINY)
    decision(710,"API key configured?")
    box(d,(1310,665,1655,755),"Return config error","Live collection cannot start",fill=GRAY,font=SMALL,subfont=TINY)
    steps=[
        (865,"Resolve channel","Find channel ID and uploads playlist"),
        (1035,"Read uploads pages","Follow next-page tokens to the requested limit"),
        (1205,"Fetch video details","Batch video IDs in requests of up to 50"),
        (1375,"Normalize statistics","Keep unavailable public counts as null"),
        (1545,"Persist records","Upsert metadata and append dated snapshots"),
        (1715,"Return result","Report collection totals and any warnings"),
    ]
    for y,t,s in steps: box(d,(left,y-60,left+bw,y+60),t,s)
    terminal(cx,1870,"End")
    arrow(d,(cx,190),(cx,260))
    arrow(d,(cx,390),(cx,440))
    arrow(d,(cx-205,510),(390,510),"No")
    arrow(d,(cx,580),(cx,640),"Yes")
    arrow(d,(cx+205,710),(1310,710),"No")
    arrow(d,(cx,780),(cx,805),"Yes")
    for (y1,_,_),(y2,_,_) in zip(steps,steps[1:]): arrow(d,(cx,y1+60),(cx,y2-60))
    arrow(d,(cx,1775),(cx,1825))
    im.save(OUT/"system_flowchart.png")


def dfd():
    w,h=2000,1450; im,d=canvas(w,h,"3.4.2  DATA FLOW DIAGRAM")
    d.text((w/2,130),"LEVEL 0 — CONTEXT",fill=BLUE,font=BOLD,anchor="mm")
    # context diagram
    box(d,(80,245,500,430),"User / Analyst","Collection requests, analytics and export requests",fill=GRAY,font=BOLD,subfont=TINY)
    box(d,(690,220,1320,455),"YouTube Engagement\nAnalytics System","Validate · collect · store · analyze · export",fill=PALE,font=BOLD,subfont=SMALL)
    box(d,(1500,245,1920,430),"YouTube Data API v3","Public channel, video metadata and statistics",fill=GRAY,font=BOLD,subfont=TINY)
    arrow(d,(500,300),(690,300),"requests")
    arrow(d,(690,385),(500,385),"results / CSV")
    arrow(d,(1320,300),(1500,300),"API requests")
    arrow(d,(1500,385),(1320,385),"public data")
    d.line((70,520,1930,520),fill="#C8CDD3",width=2)
    d.text((w/2,570),"LEVEL 1 — SYSTEM PROCESSES AND DATA STORES",fill=BLUE,font=BOLD,anchor="mm")
    # External entity and core processing chain.
    box(d,(55,770,335,930),"User / Analyst","",fill=GRAY,font=SMALL)
    box(d,(430,700,720,850),"1. Validate\nrequest","Pydantic schemas",fill=PALE,font=SMALL,subfont=TINY)
    box(d,(830,700,1120,850),"2. Collect\npublic data","YouTube client + pagination",fill=PALE,font=SMALL,subfont=TINY)
    box(d,(1230,700,1520,850),"3. Normalize\ndata","Python / pandas",fill=PALE,font=SMALL,subfont=TINY)
    box(d,(830,950,1120,1090),"YouTube Data API v3","Channel, uploads and video details",fill=GRAY,font=SMALL,subfont=TINY)
    # persistent data stores
    d.rectangle((1210,1030,1510,1150),fill="#FFF7E6",outline=INK,width=3)
    d.line((1210,1070,1510,1070),fill=INK,width=2)
    d.text((1360,1050),"D1  Videos",fill=INK,font=SMALL,anchor="mm")
    d.text((1360,1110),"one row per video",fill=MID,font=TINY,anchor="mm")
    d.rectangle((1570,1030,1930,1150),fill="#FFF7E6",outline=INK,width=3)
    d.line((1570,1070,1930,1070),fill=INK,width=2)
    d.text((1750,1050),"D2  Metric snapshots",fill=INK,font=SMALL,anchor="mm")
    d.text((1750,1110),"dated, nullable observations",fill=MID,font=TINY,anchor="mm")
    box(d,(430,1170,850,1325),"4. Analytics and CSV export","Reads stored observations",fill=PALE,font=SMALL,subfont=TINY)
    # Data flows: user -> validation -> collection -> normalization -> storage.
    arrow(d,(335,820),(430,770),"request")
    arrow(d,(720,770),(830,770),"valid request")
    arrow(d,(1120,770),(1230,770),"collected records")
    # Two parallel paths represent the outbound API request and inbound response.
    d.line((900,850,900,930),fill=INK,width=3); arrow(d,(900,930),(900,950),"API request")
    d.line((1045,950,1045,920,1080,920,1080,870),fill=INK,width=3); arrow(d,(1080,870),(1080,850),"API response")
    arrow(d,(1360,850),(1360,1030),"video metadata")
    arrow(d,(1450,850),(1620,1030),"statistics")
    # Stored data is read by analytics and export processing.
    d.line((1210,1120,1000,1120,1000,1240,900,1240),fill=INK,width=3)
    arrow(d,(900,1240),(850,1240),"read")
    d.line((1750,1150,1750,1370,640,1370),fill=INK,width=3)
    arrow(d,(640,1370),(640,1325),"read")
    d.line((430,1240,335,1240,335,930),fill=INK,width=3)
    arrow(d,(335,930),(335,910),"analytics / CSV")
    im.save(OUT/"data_flow_diagram.png")


def class_diagram():
    w,h=2000,1450; im,d=canvas(w,h,"3.4.3  DOMAIN AND SCHEMA CLASS DIAGRAM")
    def cls(x,y,width,height,name,stereotype,attrs):
        d.rectangle((x,y,x+width,y+height),fill=BG,outline=INK,width=3)
        d.rectangle((x,y,x+width,y+58),fill=PALE,outline=INK,width=3)
        d.text((x+width/2,y+29),name,fill=INK,font=BOLD,anchor="mm")
        d.text((x+width/2,y+82),stereotype,fill=BLUE,font=TINY,anchor="mm")
        yy=y+118
        for a in attrs:
            d.text((x+22,yy),a,fill=INK,font=SMALL,anchor="la"); yy+=41
    cls(120,235,760,500,"Video","SQLAlchemy model · videos",[
        "+ video_id: str [PK]", "+ channel_id: str", "+ channel_title: str",
        "+ title: str", "+ published_at: datetime", "+ duration_seconds: int | null",
        "+ thumbnail_url: str | null", "+ url: str", "+ snapshots: list[MetricSnapshot]"])
    cls(1120,235,760,500,"MetricSnapshot","SQLAlchemy model · video_metric_snapshots",[
        "+ id: int [PK]", "+ video_id: str [FK]", "+ collected_at: datetime",
        "+ views: int | null", "+ likes: int | null", "+ comments: int | null", "+ video: Video"])
    # relationship one-to-many
    y=490; d.line((880,y,1120,y),fill=INK,width=4)
    d.text((900,y-28),"1",fill=INK,font=BOLD,anchor="mm")
    d.text((1100,y-28),"0..*",fill=INK,font=BOLD,anchor="mm")
    d.text((1000,y+34),"has snapshots",fill=MID,font=TINY,anchor="mm")
    cls(80,850,560,410,"CollectionRequest","Pydantic request schema",[
        "+ channel_handle: str", "+ max_videos: int", "+ constraint: 1–5000"])
    cls(720,850,560,410,"VideoOut","Pydantic response schema",[
        "+ video_id: str", "+ title: str", "+ published_at: datetime", "+ views / likes / comments: int | null", "+ engagement_rate: float | null"])
    cls(1360,850,560,410,"CollectionSummary","Pydantic response schema",[
        "+ channel_id: str", "+ discovered: int", "+ processed: int", "+ snapshots: int", "+ collected_at: datetime", "+ warnings: list[str]"])
    d.text((w/2,1350),"A snapshot belongs to exactly one video; a video may have multiple dated snapshots.",fill=MID,font=SMALL,anchor="mm")
    im.save(OUT/"class_diagram.png")


def use_case():
    w,h=2000,1300; im,d=canvas(w,h,"3.4.4  USE CASE DIAGRAM")
    # system boundary
    d.rounded_rectangle((500,170,1510,1190),radius=24,outline=BLUE,width=4)
    d.text((1000,205),"YouTube Engagement Analytics System",fill=BLUE,font=BOLD,anchor="mm")
    # stick actor
    def actor(x,y,label):
        d.ellipse((x-32,y-105,x+32,y-41),outline=INK,width=5)
        d.line((x,y-41,x,y+70),fill=INK,width=5)
        d.line((x-65,y+5,x+65,y+5),fill=INK,width=5)
        d.line((x,y+70,x-55,y+135),fill=INK,width=5)
        d.line((x,y+70,x+55,y+135),fill=INK,width=5)
        d.text((x,y+165),label,fill=INK,font=BOLD,anchor="mm")
    actor(250,650,"User / Analyst")
    actor(1760,650,"YouTube Data API v3")
    usecases=[
        (760,330,"Check API health"),(1240,330,"View channel and videos"),
        (760,500,"Run data collection"),(1240,500,"View analytics"),
        (760,670,"Review historical growth"),(1240,670,"Export CSV datasets"),
        (1000,850,"Refresh Power BI dashboard")]
    for x,y,label in usecases:
        d.ellipse((x-190,y-58,x+190,y+58),fill=PALE,outline=INK,width=3)
        d.text((x,y),label,fill=INK,font=SMALL,anchor="mm")
    # User associations use lanes outside the oval text areas.
    user_bus=445
    d.line((315,650,user_bus,650),fill=MID,width=2)
    d.line((user_bus,330,user_bus,855),fill=MID,width=2)
    for x,y,_ in (usecases[0],usecases[2],usecases[4]):
        d.line((user_bus,y,x-190,y),fill=MID,width=2)
    right_bus=1480
    d.line((user_bus,650,user_bus,245),fill=MID,width=2)
    d.line((user_bus,245,right_bus,245),fill=MID,width=2)
    d.line((right_bus,330,right_bus,670),fill=MID,width=2)
    for x,y,_ in (usecases[1],usecases[3],usecases[5]):
        d.line((right_bus,y,x+190,y),fill=MID,width=2)
    # Refresh is reached from below the other use cases.
    d.line((315,650,445,650,445,960,1000,960,1000,908),fill=MID,width=2)
    # The external API participates only in the collection use case; route outside the ovals.
    d.line((950,500,975,500,975,245,1585,245,1585,650,1660,650),fill=BLUE,width=3)
    d.text((1590,285),"API requests / public data",fill=BLUE,font=TINY,anchor="mm")
    # Export-to-dashboard dependency
    d.line((1240,728,1240,790),fill=BLUE,width=3)
    d.polygon([(1240,790),(1229,771),(1251,771)],fill=BLUE)
    d.text((1345,758),"CSV input",fill=BLUE,font=TINY,anchor="mm")
    im.save(OUT/"use_case_diagram.png")


if __name__ == "__main__":
    flowchart(); dfd(); class_diagram(); use_case()
    print("Generated 4 diagrams in", OUT)

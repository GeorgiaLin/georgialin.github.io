"""Export the raw audio transcription (Whisper, no 原稿, no corrections) as
editable Markdown, one file per episode: `[mm:ss] sentence` lines.
Re-parseable later: each content line starts with [mm:ss].
"""
import os, re, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "..", "transcribe_work")
OUT = os.path.join(RAW, "edit")
POD = os.path.join(ROOT, "_podcast")
SENT = set("。！？!?…")
FW = {",": "，", "?": "？", "!": "！", ";": "；", ":": "："}

def fullwidth(t):
    out=[]
    for i,ch in enumerate(t):
        if ch in FW:
            p=t[i-1] if i>0 else ""; n=t[i+1] if i+1<len(t) else ""
            out.append(ch if (p.isascii() and p.isalnum() and n.isascii() and n.isalnum()) else FW[ch])
        else: out.append(ch)
    return "".join(out)

def title(slug):
    f=os.path.join(POD,f"{slug}.md")
    if os.path.exists(f):
        m=re.search(r'^title:\s*"?(.*?)"?\s*$', open(f,encoding="utf-8").read().split("---",2)[1], re.M)
        if m: return m.group(1)
    return slug

def sentences(segs):
    out=[]; buf=""; t0=None
    for s in segs:
        txt=(s.get("text") or "").strip()
        if not txt: continue
        if t0 is None: t0=s["start"]
        buf+=txt
        if buf[-1] in SENT or len(buf)>=60:
            out.append((t0, fullwidth(buf))); buf=""; t0=None
    if buf: out.append((t0, fullwidth(buf)))
    return out

os.makedirs(OUT, exist_ok=True)
for rawp in sorted(glob.glob(f"{RAW}/*.raw.json")):
    slug=os.path.basename(rawp)[:-9]
    segs=json.load(open(rawp,encoding="utf-8"))["segments"]
    lines=[f"# {title(slug)}","",
           "> 纯音频转写（Whisper large-v3）。每行以 [mm:ss] 开头，请直接改错别字/断句，时间戳保留即可。","",]
    for t,txt in sentences(segs):
        mm=int(t)//60; ss=int(t)%60
        lines.append(f"[{mm:02d}:{ss:02d}] {txt}")
    open(os.path.join(OUT,f"{slug}.md"),"w",encoding="utf-8").write("\n".join(lines)+"\n")
    print(f"{slug}.md  ({len(segs)} segs -> {len(lines)-4} lines)")

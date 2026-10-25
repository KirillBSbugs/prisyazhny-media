import json, sys, pathlib
# python3 cover.py <case.json> <outdir>
D = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
C = D['cover']
css = open(pathlib.Path(__file__).parent / 'page.html').read()
fonts = css[css.index('@font-face'):css.index('*{margin')]
plane = '''<g transform="translate(540,700) rotate(32) scale(1.05)" fill="rgba(125,255,170,.55)" stroke="#9dffbe" stroke-opacity=".6" stroke-width="3">
<path d="M0,-260 C22,-260 30,-230 30,-200 L30,-40 L250,40 L250,80 L30,30 L24,170 L90,215 L90,245 L0,225 L-90,245 L-90,215 L-24,170 L-30,30 L-250,80 L-250,40 L-30,-40 L-30,-200 C-30,-230 -22,-260 0,-260Z"/>
<rect x="22" y="150" width="34" height="70" rx="12"/><rect x="-56" y="150" width="34" height="70" rx="12"/></g>'''
BARGE = """<g transform="translate(540,690) scale(1.35)" fill="#000" stroke="#9dffbe" stroke-width="5" stroke-linejoin="round"><path d="M-260,0 L260,0 L220,70 L-230,70Z" fill="rgba(125,255,170,.18)"/><rect x="90" y="-90" width="110" height="90"/><rect x="110" y="-70" width="28" height="24" fill="#9dffbe" fill-opacity=".5"/><rect x="152" y="-70" width="28" height="24" fill="#9dffbe" fill-opacity=".5"/><line x1="145" y1="-90" x2="145" y2="-150"/><text x="-120" y="48" fill="#9dffbe" stroke="none" font-family="JB" font-weight="700" font-size="34">Т-36</text></g>""" + "".join(f'<path d="M-20,{790+k*50} ' + " ".join(f"L{x},{790+k*50+ (14-k*2)*__import__('math').sin(x/90+k)}" for x in range(-20,1101,20)) + f'" fill="none" stroke="#9dffbe" stroke-opacity="{.55-k*.1}" stroke-width="3"/>' for k in range(4))
def river(on):
    if not on: return ''
    w = ''.join(f'<path d="M{i*170-40},{900+(i%2)*25} q40,-12 80,0 t80,0" fill="none" stroke="#9dffbe" stroke-opacity=".3" stroke-width="3"/>' for i in range(8))
    return f'<rect x="-10" y="820" width="1100" height="170" fill="rgba(125,255,170,.10)" stroke="#9dffbe" stroke-opacity=".45" stroke-width="3"/>{w}'
for p in ('1', '2'):
    c = C[p]
    log = ''.join(f'<div>{l}</div>' for l in c['log'])
    html = f'''<!doctype html><html><head><meta charset=utf-8><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:radial-gradient(ellipse 800px 900px at 540px 700px,#0c2414 0%,#040a06 55%,#000 100%);font-family:JB;color:#9dffbe;position:relative}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 2px,transparent 2px 5px)}}
.hud{{position:absolute;top:80px;left:70px;right:70px;display:flex;justify-content:space-between;font:700 36px JB}}
.rec::before{{content:'';display:inline-block;width:26px;height:26px;border-radius:50%;background:#ff4a3a;margin-right:14px;vertical-align:-3px;box-shadow:0 0 18px #ff4a3a}}
.brand{{position:absolute;top:190px;width:100%;text-align:center;font:700 32px JB;letter-spacing:6px;color:#6fdc94}}
.log{{position:absolute;top:1060px;left:150px;font:700 34px/1.5 JB;color:#7dffaa;text-shadow:0 0 12px rgba(125,255,170,.5)}}
.log div:last-child{{color:#ff5a48;text-shadow:0 0 12px rgba(255,90,72,.6)}}
.title{{position:absolute;top:1300px;width:100%;text-align:center;font-family:UB;font-weight:900}}
.t1{{font-size:104px;line-height:1;color:#e6ffee;text-shadow:0 0 30px rgba(125,255,170,.45)}}
.t2{{display:inline-block;margin-top:18px;font-size:100px;line-height:1.1;padding:6px 34px 16px;background:#ff4a3a;color:#0b0303;box-shadow:0 0 50px rgba(255,74,58,.45)}}
.chip{{position:absolute;top:1640px;left:50%;transform:translateX(-50%);font:700 34px JB;letter-spacing:4px;padding:14px 30px;border:3px solid #7dffaa;white-space:nowrap}}
.q{{position:absolute;top:1745px;width:100%;text-align:center;font:700 30px JB;letter-spacing:3px;color:#5fbf80}}
.vig{{position:absolute;inset:0;box-shadow:inset 0 0 280px 90px #000}}
</style></head><body>
<svg width=1080 height=1920 style="position:absolute;inset:0"><defs><filter id=g><feGaussianBlur stdDeviation=6 result=b/><feMerge><feMergeNode in=b/><feMergeNode in=SourceGraphic/></feMerge></filter></defs>
<g filter="url(#g)">{river(c.get('river'))}{BARGE if c.get('art')=='barge' else plane}</g>
<circle cx="540" cy="700" r="330" fill="none" stroke="#7dffaa" stroke-opacity=".18" stroke-width="3"/><circle cx="540" cy="700" r="200" fill="none" stroke="#7dffaa" stroke-opacity=".12" stroke-width="3"/>
<line x1="540" y1="340" x2="540" y2="1060" stroke="#7dffaa" stroke-opacity=".12" stroke-width="3"/><line x1="180" y1="700" x2="900" y2="700" stroke="#7dffaa" stroke-opacity=".12" stroke-width="3"/></svg>
<div class=scan></div><div class=vig></div>
<div class=hud><span class=rec>REC</span><span>{D['hud']} {c['tc'] or ''}</span></div>
<div class=brand>ТЫ — НА СМЕНЕ · СМЕНА №{D['n']}</div>
<div class=log>{log}</div>
<div class=title><div class=t1>{c['t1']}</div><div class=t2>{c['t2']}</div></div>
<div class=chip>{c['chip']}</div><div class=q>{c['q']}</div>
</body></html>'''
    (out / f'cover{p}.html').write_text(html)

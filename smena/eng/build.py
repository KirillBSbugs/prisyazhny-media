"""Build one part of a «Ты — на смене» episode.
python3 eng/build.py cases/03.json 1 work/03p1 [--still 2,10,20]
Produces work/<dir>/cfg.json, sfx.wav, silent.mp4 and out.mp4 (video + cockpit sound, no voice).
The voice is added afterwards with vidIQ compose (keepNativeAudio)."""
import json, sys, subprocess, pathlib, re
import numpy as np, wave

case, part, wd = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
wd.mkdir(parents=True, exist_ok=True)
D = json.load(open(case)); P = D['parts'][part]
acc = set(P.get('acc', []))
words = [{'w': w, 's': s, 'acc': w in acc} for w, s in P['words']]
# phrases: split after sentence-ending punctuation
phr, a = [], 0
for i, w in enumerate(words):
    if re.search(r'[.?!…]»?$', w['w']) or i == len(words) - 1:
        phr.append([a, i]); a = i + 1
cfg = {'n': D['n'], 'hud': D['hud'], 't0': D['t0'], 'foot': D['foot'], 'dur': P['dur'],
       'words': words, 'phr': phr, 'scenes': P['scenes']}
(wd / 'cfg.json').write_text(json.dumps(cfg, ensure_ascii=False))
eng = pathlib.Path(__file__).parent

if '--still' in sys.argv:
    ts = sys.argv[sys.argv.index('--still') + 1]
    subprocess.run(['node', str(eng / 'render.js'), str(wd / 'cfg.json'), '-', '--still', ts, str(wd / 'still')], check=True)
    sys.exit()

# ---------- cockpit sound layer ----------
SR = 44100; END = P['dur']; N = int(END * SR); tt = np.arange(N) / SR
rng = np.random.default_rng(int(D['n']) * 10 + int(part))
out = np.zeros(N)
def lp(x, a):
    y = np.empty_like(x); acc_ = 0.0
    for i in range(len(x)):
        acc_ += a * (x[i] - acc_); y[i] = acc_
    return y
def add(sig, t0):
    i = int(t0 * SR)
    if i >= N: return
    n = min(len(sig), N - i); out[i:i + n] += sig[:n]
env = np.interp(tt, [0, 1.5, END - 1.2, END], [0, 1, 1, 0])
hum = lp(rng.standard_normal(N), .02) * 1.4 + np.sin(2*np.pi*58*tt) * .05 + np.sin(2*np.pi*116*tt) * .025 + np.sin(2*np.pi*400*tt) * .004
out += hum * env * .30
drone = (np.sin(2*np.pi*43*tt) + .5*np.sin(2*np.pi*43.6*tt)) * np.interp(tt, [0, END*.6, END], [.02, .06, .03])
out += drone * env
def chime(t0, v=.10):
    for j, f in enumerate((1046, 784)):
        n = int(.4 * SR); k = np.arange(n) / SR
        add((np.sin(2*np.pi*f*k) + .3*np.sin(2*np.pi*f*2*k)) * np.minimum(1, k/.005) * np.exp(-k*7) * v, t0 + j*.28)
def static(t0, dur=.25, v=.10):
    n = int(dur * SR); k = np.arange(n) / SR; x = rng.standard_normal(n)
    add(x * (rng.random(n) > .35) * np.sin(np.pi*k/dur) * v, t0)
def thump(t0, v=.35):
    n = int(.5 * SR); k = np.arange(n) / SR
    add(np.sin(2*np.pi*(55 + 40*np.exp(-k*20))*k) * np.exp(-k*6) * v, t0)
def alarm(t0, reps=3, v=.05):
    for r in range(reps):
        n = int(.16 * SR); k = np.arange(n) / SR
        add(np.sign(np.sin(2*np.pi*880*k)) * .5 * np.exp(-k*10) * v, t0 + r*.32)
for i, sc in enumerate(P['scenes']):
    if i: static(sc['t'] - .05)
    v = sc['v']
    if v.get('stamp'): thump(sc['t'] + .5 + v.get('sd', 0)); chime(sc['t'] + .55 + v.get('sd', 0), .05)
    if v.get('stamp2'): thump(sc['t'] + .5 + v['sd2']); chime(sc['t'] + .55 + v['sd2'], .05)
    if v['type'] == 'option': chime(sc['t'] + .05, .06)
    if v['type'] in ('endq', 'endp2'): chime(sc['t'] + .1, .09)
if part == '1':
    for q in np.arange(1.0, 26.5, 5.0): alarm(q)
else:
    alarm(0.6)
out = np.tanh(out * 1.2) * .8
pcm = (np.stack([out, out], 1) * 32767).astype(np.int16)
with wave.open(str(wd / 'sfx.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

subprocess.run(['node', str(eng / 'render.js'), str(wd / 'cfg.json'), str(wd / 'silent.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wd / 'silent.mp4'), '-i', str(wd / 'sfx.wav'),
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(wd / 'out.mp4')], check=True)
print('done', wd / 'out.mp4')

import math, random, wave, struct, sys
VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'pc'
SR = 44100
DUR = 7.0
buf = [0.0] * int(SR * DUR)
random.seed(3)

def add(t0, dur, fn):
    i0 = int(t0 * SR)
    for k in range(int(dur * SR)):
        i = i0 + k
        if 0 <= i < len(buf):
            buf[i] += fn(k / SR)

def tone(t0, f0, f1, dur, vol, decay, shape='sine'):
    phase = [0.0]
    def fn(t):
        f = f0 + (f1 - f0) * min(1, t / dur)
        phase[0] += 2 * math.pi * f / SR
        s = math.sin(phase[0])
        if shape == 'square':
            s = 1.0 if s > 0 else -1.0
            s *= 0.5
        return vol * s * math.exp(-t * decay) * min(1, t * 400)
    add(t0, dur, fn)

def noise(t0, dur, vol, decay, cutoff=0.3, rise=False):
    y = [0.0]
    def fn(t):
        a = cutoff if not rise else 0.02 + 0.5 * (t / dur) ** 2
        y[0] += a * (random.uniform(-1, 1) - y[0])
        env = math.sin(math.pi * t / dur) if rise else math.exp(-t * decay)
        return vol * y[0] * env * 3
    add(t0, dur, fn)

def kick(t0, vol=0.9):
    phase = [0.0]
    def fn(t):
        f = 48 + 110 * math.exp(-t * 30)
        phase[0] += 2 * math.pi * f / SR
        return vol * math.sin(phase[0]) * math.exp(-t * 7)
    add(t0, 0.45, fn)

def impact(t0, vol=1.0):
    kick(t0, vol)
    noise(t0, 0.5, 0.35 * vol, 9, 0.5)

def chime(t0, freqs, gap, vol=0.16):
    for n, f in enumerate(freqs):
        tone(t0 + n * gap, f, f, 0.6, vol, 6)
        tone(t0 + n * gap, f * 2, f * 2, 0.4, vol * 0.3, 9)

# Scene 1: chat messages, or keystrokes in a terminal.
if VARIANT == 'server':
    for k in range(8):
        noise(0.10 + k * 0.045, 0.04, 0.3, 70, 0.6)
        tone(0.10 + k * 0.045, 160, 120, 0.06, 0.15, 30)
    chime(0.55, [880, 1320], 0.06, 0.13)
    tone(0.85, 600, 700, 0.15, 0.12, 10)
    tone(1.05, 300, 1200, 0.4, 0.14, 2)
    chime(1.45, [1568, 2093], 0.05, 0.16)
elif VARIANT == 'confused':
    for k in range(7):
        noise(0.10 + k * 0.05, 0.025, 0.3, 120, 0.95)
    chime(0.45, [880, 1320], 0.06, 0.13)
    for k, t in enumerate((0.62, 0.76, 0.90, 1.04, 1.18, 1.32, 1.46, 1.58)):
        tone(t, 500 + (k % 4) * 120, 300 + (k % 3) * 90, 0.12, 0.16, 14, 'square')
    tone(1.0, 400, 700, 0.25, 0.12, 6)
    tone(1.2, 450, 800, 0.25, 0.12, 6)
elif VARIANT == 'term':
    for k in range(9):
        noise(0.10 + k * 0.033, 0.025, 0.35, 120, 0.95)
    tone(0.45, 1320, 1320, 0.15, 0.16, 18)
    tone(0.60, 990, 990, 0.08, 0.08, 30)
    tone(0.92, 300, 200, 0.15, 0.14, 12, 'square')
    for t in (1.10, 1.32, 1.54):
        tone(t, 200, 180, 0.14, 0.2, 16, 'square')
else:
    for t in (0.20, 1.10, 1.32, 1.54):
        tone(t, 900, 1400, 0.07, 0.22, 25)
    for t in (1.15, 1.37, 1.59):
        tone(t, 200, 180, 0.12, 0.18, 18, 'square')
    chime(0.42, [660, 990], 0.08, 0.16)
noise(0.78, 0.03, 0.5, 60, 0.9)
tone(0.78, 420, 70, 0.4, 0.4, 5)
tone(1.78, 110, 105, 0.32, 0.22, 6, 'square')

# Transition and answer.
noise(1.98, 0.35, 0.45, 0, rise=True)
impact(2.30, 0.7)
impact(2.42, 0.7)
impact(2.60, 1.0)

# Beat from the big hit to the end: kick on the beat, hats in between, a simple bass line.
bass = [55, 55, 65.4, 49]
b = 0
t = 3.10
while t < DUR - 0.05:
    kick(t, 0.75)
    noise(t + 0.25, 0.06, 0.12, 60, 0.9)
    tone(t, bass[b % 4], bass[b % 4], 0.45, 0.25, 4)
    b += 1
    t += 0.5

for t in (3.0, 3.3, 3.6):
    tone(t, 1250, 1250, 0.08, 0.16, 30)
    tone(t, 1875, 1875, 0.06, 0.06, 40)
chime(3.95, [1047, 1319, 1568], 0.06, 0.13)
noise(4.95, 0.3, 0.4, 0, rise=True)
impact(5.10, 0.7)
chime(5.60, [784, 1047, 1319, 1568], 0.07, 0.14)

peak = max(abs(x) for x in buf) or 1
gain = 0.89 / peak
with wave.open('ad-' + VARIANT + '.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    frames = bytearray()
    for x in buf:
        v = int(max(-1, min(1, x * gain)) * 32767)
        frames += struct.pack('<hh', v, v)
    w.writeframes(bytes(frames))
print('peak', round(peak, 2))

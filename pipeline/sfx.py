"""Natural sound effects, synthesised from noise. No instruments, no music, ever.

Allowed sounds: wind, rumble, boom/explosion, wood snaps, water/gurgle, fire crackle, waves.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000


class Track:
    def __init__(self, seconds, seed=11):
        self.N = int(seconds * SR)
        self.out = np.zeros(self.N)
        self.rng = np.random.default_rng(seed)

    # helpers
    def lp(self, x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
    def bp(self, x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
    def i(self, t): return min(max(int(t * SR), 0), self.N)

    def add(self, t0, seg):
        a = self.i(t0); e = min(a + len(seg), self.N)
        self.out[a:e] += seg[:e - a]

    def norm(self, x):
        return x / (np.abs(x).max() + 1e-9)

    # sounds
    def wind(self, level_points):
        """level_points: list of (time, level 0..1) across the whole track."""
        t = np.arange(self.N) / SR
        w = self.bp(self.lp(self.rng.standard_normal(self.N), 500), 80, 900)
        gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.047 * t + 1)
        xs, ys = zip(*level_points)
        self.out += self.norm(w) * 0.10 * gust * np.interp(t, xs, ys)

    def whoosh(self, t0, t1, amp=0.25, f0=300, f1=2500):
        n = self.i(t1) - self.i(t0)
        if n <= 0: return
        x = self.rng.standard_normal(n); seg = np.zeros(n)
        edges = np.linspace(0, n, 9).astype(int)
        for k in range(8):
            fc = f0 + (f1 - f0) * k / 8
            y = self.bp(x, fc * 0.6, min(fc * 1.6, 20000))
            seg[edges[k]:edges[k + 1]] = y[edges[k]:edges[k + 1]]
        env = np.linspace(0, 1, n) ** 2
        m = min(int(0.05 * SR), n); env[-m:] *= np.linspace(1, 0, m)
        self.add(t0, self.norm(seg) * amp * env)

    def boom(self, t0, amp=0.9, tail=3.5):
        n = int(tail * SR); tt = np.arange(n) / SR
        x = self.norm(self.lp(self.rng.standard_normal(n), 180, 4))
        env = np.exp(-tt * 1.4) * (1 - np.exp(-tt * 200))
        crack = self.norm(self.bp(self.rng.standard_normal(n), 800, 5000) * np.exp(-tt * 18))
        thump = np.sin(2 * np.pi * (45 - 15 * np.minimum(tt, 1)) * tt) * np.exp(-tt * 3)
        self.add(t0, amp * (0.7 * x * env + 0.25 * crack + 0.5 * thump))

    def rumble(self, t0, t1, amp=0.25):
        n = self.i(t1) - self.i(t0)
        if n <= 0: return
        x = self.norm(self.lp(self.rng.standard_normal(n), 90, 4))
        env = np.minimum(np.linspace(0, 6, n), 1) * np.linspace(1, 0, n) ** 1.5
        self.add(t0, amp * x * env)

    def snaps(self, t0, t1, count=60, amp=0.22):
        for c in self.rng.uniform(t0, t1, count):
            n = int(0.09 * SR); tt = np.arange(n) / SR
            x = self.norm(self.bp(self.rng.standard_normal(n), 1200, 6000) * np.exp(-tt * 60))
            self.add(c, x * amp * self.rng.uniform(0.3, 1))

    def gurgle(self, t0, t1, amp=0.18):
        n = self.i(t1) - self.i(t0)
        if n <= 0: return
        x = self.bp(self.rng.standard_normal(n), 150, 700); tt = np.arange(n) / SR
        mod = (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * tt + 3 * np.sin(2 * np.pi * 0.7 * tt))) ** 3
        env = np.minimum(np.linspace(0, 4, n), 1) * np.minimum(np.linspace(4, 0, n), 1)
        self.add(t0, self.norm(x) * amp * mod * env)
        for c in self.rng.uniform(t0 + 0.2, t1 - 0.3, 22):
            m = int(0.06 * SR); q = np.arange(m) / SR
            self.add(c, self.norm(self.bp(self.rng.standard_normal(m), 300, 1200) * np.exp(-q * 50)) * amp * 0.6)

    def crackle(self, t0, t1, amp=0.15):
        """Fire crackle: dense tiny clicks over soft hiss."""
        n = self.i(t1) - self.i(t0)
        if n <= 0: return
        hiss = self.norm(self.bp(self.rng.standard_normal(n), 2000, 8000)) * 0.15
        self.add(t0, hiss * amp)
        self.snaps(t0, t1, int((t1 - t0) * 25), amp * 0.8)

    def waves(self, t0, t1, amp=0.2):
        n = self.i(t1) - self.i(t0)
        if n <= 0: return
        tt = np.arange(n) / SR
        x = self.norm(self.lp(self.rng.standard_normal(n), 1200))
        swell = (0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * tt)) ** 2
        env = np.minimum(np.linspace(0, 3, n), 1) * np.minimum(np.linspace(3, 0, n), 1)
        self.add(t0, x * amp * swell * env)

    def finish(self, peak=0.85, fade=1.0):
        out = self.out / (np.abs(self.out).max() + 1e-9) * peak
        m = int(fade * SR); out[-m:] *= np.linspace(1, 0, m)
        return out

"""Median voice pitch per clip -> FEMALE / MALE / UNCLEAR. Catches a voice that switches between clips.
Female speech usually sits around 165-255 Hz, male around 85-155 Hz.

usage: python -I voice_check.py clip1.mp4 clip2.mp4 ...
"""
import subprocess, sys
import numpy as np

SR = 16000
results = []
for path in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
                          "-af", "highpass=f=70,lowpass=f=1000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    win, hop, f0s = 1024, 320, []
    for s in range(0, len(x) - win, hop):
        fr = x[s:s + win] * np.hanning(win)
        if np.sqrt(np.mean(fr ** 2)) < 0.02:
            continue
        ac = np.correlate(fr, fr, "full")[win - 1:]
        lo, hi = SR // 400, SR // 70
        lag = lo + int(np.argmax(ac[lo:hi]))
        if ac[lag] > 0.45 * ac[0]:
            f0s.append(SR / lag)
    med = float(np.median(f0s)) if f0s else 0.0
    verdict = "FEMALE" if med >= 165 else ("MALE" if 0 < med < 160 else "UNCLEAR")
    results.append(verdict)
    print(f"{path}: median {med:.0f} Hz over {len(f0s)} voiced frames -> {verdict}")
known = {r for r in results if r != "UNCLEAR"}
print("CONSISTENT" if len(known) <= 1 else "VOICE SWITCHES BETWEEN CLIPS - remake the odd ones out")

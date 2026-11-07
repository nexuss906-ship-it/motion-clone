"""Join clips in order, optionally lay a separate voice-over (ElevenLabs mode) and burn word-timed subtitles.

usage:
  python -I assemble.py --out final.mp4 clip1.mp4 clip2.mp4 ... [--words words.json] [--voiceover vo.mp3]
                        [--sfx-volume 0.3] [--no-subs] [--sub-y 0.855] [--font C:/Windows/Fonts/seguibl.ttf]

Flow-audio mode: each clip carries its own voice. Subtitles come from --words (transcribe.py output for these clips).
ElevenLabs mode: pass --voiceover; clip audio is kept quietly as SFX bed. Subtitles come from --words, which must be
                 a transcript of the voice-over file itself ({"<vo path>": [...]}) - its timings are absolute.
"""
import argparse, json, subprocess, re, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("clips", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--words")
ap.add_argument("--voiceover")
ap.add_argument("--sfx-volume", type=float, default=0.3)
ap.add_argument("--no-subs", action="store_true")
ap.add_argument("--sub-y", type=float, default=0.855)  # below hashtag/caption zone, above the bottom UI
ap.add_argument("--font", default="C:/Windows/Fonts/seguibl.ttf")
ap.add_argument("--fontsize", type=int, default=0)
a = ap.parse_args()

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())

def size(p):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip().split(",")[:2]
    return int(w), int(h)

durs = [dur(c) for c in a.clips]
W, H = size(a.clips[0])
tmp = Path(tempfile.mkdtemp(prefix="assemble_"))

# subtitle chunks: 2-3 words, broken at punctuation, each held until the next starts
chunks = []
if a.words and not a.no_subs:
    data = json.load(open(a.words))
    norm = {Path(k).name: v for k, v in data.items()}
    if a.voiceover:
        streams = [(0.0, norm[Path(a.voiceover).name])]
    else:
        offs = [sum(durs[:i]) for i in range(len(a.clips))]
        streams = [(offs[i], norm[Path(c).name]) for i, c in enumerate(a.clips)]
    for off, ws in streams:
        cur = []
        for i, w in enumerate(ws):
            cur.append(w)
            if len(cur) == 3 or re.search(r"[.,!?;:]$", w["w"]) or i == len(ws) - 1:
                chunks.append([off + cur[0]["s"], off + cur[-1]["e"], " ".join(x["w"] for x in cur)])
                cur = []
    for i in range(len(chunks)):
        nxt = chunks[i + 1][0] if i + 1 < len(chunks) else chunks[i][1] + 0.6
        chunks[i][1] = min(nxt, chunks[i][1] + 0.6)

fs = a.fontsize or int(W * 0.072)
font = a.font.replace(":", "\\:")
draws = []
for i, (s, e, t) in enumerate(chunks):
    tf = tmp / f"c{i:03d}.txt"
    tf.write_text(t.rstrip(",;:").upper(), encoding="utf8")
    tfp = str(tf).replace("\\", "/").replace(":", "\\:")
    draws.append(f"drawtext=fontfile='{font}':textfile='{tfp}':fontsize={fs}:fontcolor=white:borderw={max(4, fs // 11)}:"
                 f"bordercolor=black@0.95:shadowx=0:shadowy={fs // 13}:shadowcolor=black@0.45:"
                 f"x=(w-text_w)/2:y=h*{a.sub_y}:enable='between(t,{s:.2f},{e:.2f})'")

n = len(a.clips)
parts = [f"[{i}:v]scale={W}:{H},setsar=1,fps=24[v{i}];[{i}:a]aresample=48000[a{i}]" for i in range(n)]
fc = ";".join(parts) + ";" + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]"
fc += ";[vc]" + (",".join(draws) + "," if draws else "") + "format=yuv420p[v]"
inputs = sum((["-i", c] for c in a.clips), [])
if a.voiceover:
    inputs += ["-i", a.voiceover]
    fc += f";[ac]volume={a.sfx_volume}[sfx];[{n}:a]apad[vo];[vo][sfx]amix=inputs=2:duration=shortest:normalize=0[a]"
else:
    fc += ";[ac]anull[a]"
(tmp / "fc.txt").write_text(fc, encoding="utf8")

# newer ffmpeg builds take a filter script via -/filter_complex; older ones via -filter_complex_script
for flag in ("-/filter_complex", "-filter_complex_script"):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, flag, str(tmp / "fc.txt"), "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", a.out], capture_output=True, text=True)
    if r.returncode == 0:
        break
else:
    raise SystemExit(r.stderr[-2000:])
print(f"{a.out}: {dur(a.out):.2f}s, {n} clips, {len(chunks)} subtitles")

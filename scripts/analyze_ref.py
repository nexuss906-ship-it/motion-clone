"""Study a reference video: technical info, cut points, pacing, contact sheets, and the spoken script with timings.

usage: python -I analyze_ref.py <video> <out_dir>
writes: <out_dir>/report.json, <out_dir>/sheet_NN.jpg (4 frames per second, 8x2 tiles = 4s per sheet),
        <out_dir>/stills/*.png (one larger still per detected shot)
"""
import json, subprocess, sys, re
from pathlib import Path

video, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
(out / "stills").mkdir(exist_ok=True)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="ignore")

probe = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", video]).stdout)
dur = float(probe["format"]["duration"])
vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])

# hard cuts
log = run(["ffmpeg", "-i", video, "-vf", "select='gt(scene,0.3)',showinfo", "-f", "null", "-"]).stderr
cuts = [round(float(x), 2) for x in re.findall(r"pts_time:([0-9.]+)", log)]
shots = [0.0] + cuts + [dur]
lens = [round(b - a, 2) for a, b in zip(shots, shots[1:]) if b - a > 0.05]

# contact sheets (4 fps) + one still per shot
w = 170 if int(vs["width"]) < int(vs["height"]) else 300
run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
     f"fps=4,scale={w}:-1,tile=8x2:padding=3:color=red", str(out / "sheet_%02d.jpg")])
for i, (a, b) in enumerate(zip(shots, shots[1:])):
    t = a + (b - a) / 2
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
         "-vf", "scale=480:-1", str(out / "stills" / f"shot_{i:02d}_{t:05.2f}s.png")])

# spoken script with word timings (optional: needs faster-whisper + numpy)
words, text = [], ""
if has_audio:
    try:
        import numpy as np
        from faster_whisper import WhisperModel
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
                              "-f", "s16le", "-"], capture_output=True).stdout
        audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(
            audio, word_timestamps=True, vad_filter=False)
        words = [{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2)} for s in segs for x in s.words]
        text = " ".join(x["w"] for x in words)
    except Exception as e:  # transcription is a nice-to-have
        text = f"(transcription unavailable: {e})"

speech = (words[-1]["e"] - words[0]["s"]) if len(words) > 1 else 0
report = {
    "file": video, "duration_s": round(dur, 2), "size": f'{vs["width"]}x{vs["height"]}',
    "orientation": "vertical 9:16" if int(vs["height"]) > int(vs["width"]) else "horizontal 16:9",
    "fps": vs["r_frame_rate"], "has_audio": has_audio,
    "hard_cuts_s": cuts, "shot_lengths_s": lens,
    "avg_shot_s": round(sum(lens) / len(lens), 2) if lens else dur,
    "pacing_note": ("mostly one continuous take - transitions are morphs/camera moves, not cuts"
                    if len(cuts) <= max(1, dur / 10) else "cut-driven edit"),
    "transcript": text, "words_per_second": round(len(words) / speech, 2) if speech else None,
    "words": words,
}
json.dump(report, open(out / "report.json", "w"), indent=1)
print(json.dumps({k: v for k, v in report.items() if k != "words"}, indent=1))
print("sheets:", sorted(p.name for p in out.glob("sheet_*.jpg")))

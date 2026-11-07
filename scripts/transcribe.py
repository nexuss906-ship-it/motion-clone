"""Transcribe clips with word timestamps (faster-whisper). Used to check what each clip actually says
(merge by spoken order, not file name) and to build subtitles.

usage: python -I transcribe.py <out.json> clip1.mp4 clip2.mp4 ...
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
out = {}
for path in sys.argv[2:]:
    # decode with ffmpeg ourselves: some PyAV versions break faster-whisper's own decoder
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=False)
    out[path] = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
    print(path, "|", " ".join(x["w"] for x in out[path]))
json.dump(out, open(sys.argv[1], "w"), indent=1)

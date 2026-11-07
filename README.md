# /motion-clone

A Claude Code skill that takes a **reference motion-graphics video** and recreates its exact look, motion, transitions and pacing for **your own content**. It either hands you copy-paste Google Flow (Omni Flash / Veo) prompts, or builds the whole video for you through a Flow MCP: generating, checking, merging and subtitling it.

## What it does
1. Asks for your **reference video** and studies it frame by frame: cuts, shot lengths, beats per second, transitions, typography, palette and voice pace.
2. Asks how you want it delivered: **copy-paste prompts** or **Flow MCP** (Claude creates, merges and gives you the final video).
3. Asks for **ElevenLabs** or **Flow** voice-over, then **male or female**. One voice is locked for the whole video, and a Flow narrator is a faceless character that never appears on screen.
4. Asks you to **paste your script** or just give the topic, and it crafts the script for you.
5. Shows the **timeline, script and scene-by-scene breakdown** and waits for your approval.
6. Builds single-line prompts with smooth eased motion, parallax, speed-ramp joins between parts and specific sound effects. No hex codes, no stray text, one cursor.
7. Checks every clip: the voice stays the same gender (a pitch check), clips are merged by what they actually say, and the frames are inspected. Then it assembles the video with word-timed subtitles.

## Install
```bash
git clone https://github.com/nexuss906-ship-it/motion-clone ~/.claude/skills/motion-clone
```
On Windows (PowerShell):
```powershell
git clone https://github.com/nexuss906-ship-it/motion-clone "$env:USERPROFILE\.claude\skills\motion-clone"
```
Restart Claude Code, then type **`/motion-clone`**.

## Requirements
- **ffmpeg / ffprobe** on your PATH
- **Python 3.10+** with `numpy` and `faster-whisper` (`pip install numpy faster-whisper`), used for transcripts, subtitles and the voice check
- **Prompts mode** needs nothing else: you paste the prompts into [Google Flow](https://labs.google/flow).
- **Flow MCP mode** needs a Google Flow MCP server connected to Claude Code (one that drives Flow in a Chrome window). `scripts/flow_download.py` uses Playwright from that server's environment.
- **ElevenLabs voice-over** needs the ElevenLabs connector in Claude.
- Optional: the `/viral-content` skill, used for writing scripts from a topic.

## Scripts
| Script | Purpose |
|---|---|
| `scripts/analyze_ref.py` | Studies the reference: cuts, pacing, contact sheets, transcript, words per second |
| `scripts/voice_check.py` | Median voice pitch per clip, flags a voice that switches between clips |
| `scripts/transcribe.py` | Word-timed transcripts of the clips (for merge order and subtitles) |
| `scripts/assemble.py` | Joins clips, optionally lays an ElevenLabs voice-over, burns subtitles |
| `scripts/flow_download.py` | Downloads your newest Flow clips (More options → Download → 720p) |

## Notes
- Flow submits on every line break, so the skill always writes each prompt as one line.
- If Flow shows *"We noticed some unusual activity"*, the skill stops automating and gives you the prompts instead. It never works around Flow's protections.

---
name: motion-clone
description: Recreate the exact look, motion, transitions and pacing of a reference motion-graphics video for the user's own content, then either hand over copy-paste Google Flow (Omni Flash / Veo) prompts or generate, merge, subtitle and deliver the finished video through the Flow MCP. Handles voice-over via ElevenLabs or a Flow voice (faceless, never on screen). Use when the user runs /motion-clone, uploads a reference video and wants "the same style / same motion graphics for my content", asks for OmniFlash or Flow prompts that match a reference, or wants a reel made like a reference video.
---

# Motion Clone

You turn **a reference video + the user's content** into a finished vertical video in the *same* style, motion, transitions and speed. The reference sets the look and the pace. The user's content sets the words and the elements on screen.

Two ways to deliver: **copy-paste prompts** (the user generates in Flow), or **Flow MCP** (you generate, download, check, merge and subtitle).

Scripts live in `<HERE>/scripts/` (`<HERE>` = this skill's folder). Run them with `python -I`. Keep working files in the session's folder, not in the skill folder.

---

## STEP 0: The intake (ask in this exact order, one step at a time)

Use `AskUserQuestion` where it fits; never ask something the user already answered.

1. **Reference video.** "Upload or give the path of your reference video." Do nothing else until you have it.
2. **Delivery.** "Do you want **(a) copy-paste prompts** you run in Flow yourself, or **(b) I connect to your Flow account through the Flow MCP (browser) and create, merge and give you the final video**?"
3. **Audio.** "Voice-over from **ElevenLabs** or from **Flow**?"
   - **ElevenLabs:** check the ElevenLabs connector is connected (`creative_list_voices`). If not, tell the user to connect it (Settings → Connectors). Clips are then made **silent except sound effects**, and the voice-over is laid on in the edit.
   - **Flow:** you will create a **faceless, invisible character** whose only job is the voice (see "Flow voice" below), and every prompt carries the strict voice-only clause.
4. **Gender.** "Male or female voice?" Lock exactly one voice for the whole video. Never mix.
5. **Script.** "Do you want to **paste your own script**, or **just give the topic** and we craft it for you?"
   - Topic only: write it with `/viral-content` (Quick Build). If Sandcastles is not connected, use framework mode and say so once.
6. **Length.** 30s, 45s or 60s (or the user's number). Default: match the reference's pace.

Then do STEP 1. Never generate anything before STEP 3 is approved.

---

## STEP 1: Study the reference exactly

```
python -I <HERE>/scripts/analyze_ref.py "<reference.mp4>" "<work>/ref"
```
This gives the duration, orientation, hard cuts, shot lengths, average shot length, whether it's a one-take morph edit or a cut edit, the transcript with word timings, words per second, 4 fps contact sheets (`sheet_NN.jpg`, 4s each) and one still per shot. **Read every sheet and every still.** Then write the **STYLE LOCK** and the **PACE LOCK**:

**STYLE LOCK** (one paragraph, pasted into every prompt):
- background (colour, texture, light, e.g. diagonal window-blind shadows, cloudy grey, pure white studio)
- element type (2D flat icons, hand-drawn ink, photoreal cut-out objects, 3D studio objects) and how they are lit or shadowed
- typography (lead-in line font and size relationship, headline font, case, colour, how words reveal)
- palette (named colours in words only, see the rules), and recurring details (sparkles, hairlines, grids, hashtags, flip cards)
- the reference's signature moves (icon morphs, flip cards, objects sliding in, foreground blur wipes, colour-tint flashes)
- give it a short NAME (e.g. "CLARITY KINETIC", "EDITORIAL LUXE", "SHADOW POSTER", "INK ICON MORPH") so the user can ask for it again

**PACE LOCK** ("maintain the same screenplay and speed"):
- beats per second: a new beat every N seconds (from shot lengths and sheet changes)
- transition type: morph / camera dive / pull-back / whip / cut, and how long it takes
- the reference's story structure (hook → problem → list → turn → payoff → CTA), mapped onto the user's content
- the voice pace in words per second, so the script fits the time

Tell the user in a short table what you found (look, motion, pace, transitions) before writing the script.

---

## STEP 2: Script

- Pasted script: keep it word for word, and only check that it fits the length (about 2.3–2.6 spoken words per second, or the reference's own rate).
- Crafted script: hook in the first 2 seconds, valuable specific points (numbered reasons work well), no filler, CTA at the end. Make every line *showable*: each phrase needs a visual that can be drawn on screen.

---

## STEP 3: Timeline + script + scene breakdown → get approval

Present one table per part (Flow clips are 8–10s; default 9–10s parts):

| Part | Time | Voice-over (exact) | Visual beat by beat | On-screen text (exact) |

Each spoken phrase gets its own on-screen element (e.g. "wrong location" → a map with a pin and an avatar bubble crossed out). End with: "Approve, or tell me what to change." **Wait for approval.** No generation and no final prompts before that.

---

## STEP 4: Build the prompts (rules learned the hard way)

Each part = **one single line**. **Flow submits on every line break**, so a multi-line paste starts several broken generations and burns credits. Every prompt contains, in this order:

1. `<STYLE NAME> style.` + the STYLE LOCK.
2. **Text rule:** "The only words that may appear on screen are the exact quoted texts in this prompt, spelled exactly; never print colour names, codes or random labels."
3. **Bans:** "Absolutely no rings, no circles as decoration, no curved arcs, no sound-wave or waveform graphics, no people, no faces, no hands, no fingers, no watermark, no logo." (Drop "people/hands" only if the user's content needs a person.) Only ever ONE mouse cursor.
4. **MOTION block** (the user's favourite, always include): "ultra smooth, fluid, After Effects quality, buttery 60fps, soft ease-in-out on every move, nothing pops, snaps, jitters or lags; the camera never stops (slow continuous push with gentle drift); three depth layers move at different speeds for parallax; every element arrives with a 0.6s eased glide and settles, outgoing elements drift out in the direction they were moving, never vanish abruptly; words glide up blur-to-sharp in 0.3s, never letter-by-letter." Plus the reference's own transition type from the PACE LOCK (morph, dive, pull-back, tint flash, foreground blur wipe), with "one continuous motion, no cut".
5. **Joins:** "OPENING first 0.4s: fast smooth speed-ramp push-in from motion blur." and "ENDING last 0.4s: fast speed-ramp whip push-in with motion blur, so it joins seamlessly onto the next clip." The last part gets "ENDING: the camera eases to a calm hold."
6. **Voice clause** (see the audio rules below).
7. `The voice says: "<exact line>"` then `SCENE:` with timecodes (0-3s …) and every on-screen text in quotes.
8. `Sound:` specific SFX (button clicks, UI ticks, whooshes, paper, metal, lock clunks…) + `No music.`

Never write hex colour codes (Flow printed "#E6176B" on screen). Describe colours in words.

### Flow voice (faceless character, voice only)
- Create the character in Flow → Characters: give it a portrait that is an **empty plate of the style's background** (e.g. a blank cream or grey frame cut from the reference, or a plain white studio). If the model leaks the character's image into scenes (it does: a sound-wave portrait once appeared as lines across 5 clips), an empty background plate shows nothing.
- "Select a voice" → pick ONE voice of the chosen gender (female: Erinome, Despina, Kore…; male: Charon, Orus, Iapetus…), describe the performance, and **Save new voice**. Saved voices are per project, so in a new project save it again or use the plain base voice.
- A voice cannot be the only ingredient ("An audio ingredient requires other ingredients"). Attach **the plate image + the voice** (or the character), nothing else.
- Strict prompt clause: "VOICE-OVER: only the attached <FEMALE/MALE> voice speaks, off-screen, one consistent <female/male> voice from start to end, never a <male/female> voice; the narrator never appears on screen: no person, face, body, mannequin or character image."

### ElevenLabs voice
- `creative_list_voices` → pick by the gender and mood; `creative_generate_speech` with `estimate_only` first and show the cost; then generate ONE take of the whole script; read `creative_get_flow_run_status` → `content_url` and download it.
- Clip prompts say: "No voice-over and no speech; sound effects only."
- In the edit: find line starts with `ffmpeg -af silencedetect`, then trim or speed-fit each scene (setpts/atempo, about 0.7–1.4×) so every visual lands on its line, and mix the voice at full volume with the clip SFX at about 0.3.

---

## STEP 5a: Prompt delivery
Give each part as its own fenced code block (one line), plus a short settings line: **Video · 9:16 (or the reference's ratio) · <N>s · x1**, which ingredients to attach, and "paste as one line". Save them to `<work>/prompts.txt`. Tell the user: "Send me the clips when they're done and I'll check, merge and subtitle them."

## STEP 5b: Flow MCP delivery
1. `flow_status` / `flow_open`. If not signed in, the user signs in themselves (never type credentials). If they want another account, they switch it in **the Flow Chrome window the MCP opened**, not their normal Chrome.
2. `flow_settings` (kind Video, ratio, length, **count 1**, 720p).
3. Generate **one part at a time at a human pace** with the Flow tools (attach ingredients, type the single-line prompt, Create). Wait for each to finish before the next.
4. **If Flow shows "We noticed some unusual activity"**: STOP. It is Flow's bot protection. Never retry, pace around it or work around it. Switch to STEP 5a and give the user the prompts.
5. Download: `flow_download_videos`, or if it can't find the button: `<flow venv python> -I <HERE>/scripts/flow_download.py <N> <work>/raw` (Flow moved Download into More options → Download → 720p).

---

## STEP 6: QA every clip (always, in both delivery modes)
```
python -I <HERE>/scripts/voice_check.py clip1.mp4 clip2.mp4 ...
python -I <HERE>/scripts/transcribe.py <work>/words.json clip1.mp4 clip2.mp4 ...
```
- **Voice:** every clip must give the same verdict (FEMALE/MALE). A switch means remaking that clip with the same voice.
- **Order:** merge by what each clip *says* ("One… Two…"), not by its file name, and tell the user if their numbering was off.
- **Frames:** make a 2 fps contact sheet per clip and look at every frame for misspelled text, stray labels or codes, people, hands, rings, the character image, and dead air.
- Fix small things in the edit (`delogo` or covering with a clean patch, trimming dead air while keeping the speed-ramp exits). For big things, rewrite that part's prompt and remake it.

## STEP 7: Assemble + subtitles
```
python -I <HERE>/scripts/assemble.py --out "<final>.mp4" p1.mp4 p2.mp4 ... --words <work>/words.json
python -I <HERE>/scripts/assemble.py --out "<final>.mp4" p1.mp4 ... --voiceover vo.mp3 --words vo_words.json   # ElevenLabs
```
Subtitles are 2–3 words, bold white with a black outline, uppercase, at 85.5% of the height (below the hashtag and caption zone). Check a few frames to confirm they don't cover on-screen text, and move them with `--sub-y` if they do. Send the final file with `SendUserFile`, and report what was checked and anything still off.

---

## Standing rules
- One voice for the whole video, always checked with `voice_check.py`.
- Never generate before the breakdown is approved. Never automate around Flow's protections.
- No hex codes, no decorative rings or circles, one cursor, single-line prompts.
- Keep the reference's speed: match its beat rate and transition type, not just its colours.
- Be honest in the report: what came out right, what's wrong, and what was fixed in the edit.

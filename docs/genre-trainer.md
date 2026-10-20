# Genre trainer

A public ear-training game: the backend generates a two-bar loop as data, the browser synthesizes it with
Tone.js, and the user guesses the genre (Hard) or the family (Easy). Nothing is stored server-side.

## Backend — `yanay_tevet_backend/genre_trainer/`

- One generator per genre in `generators/`, registered in `genre_generator_registry.py`, keyed by
  `enums/genre_type.py`. A generator is pools of layer dicts (`_cfg(...)` in `base_track_generator.py`)
  plus `_generate_layers()`, which picks from them and ends with `_apply_key_coherence` (transposes every
  melodic layer onto one root).
- A layer is 32 sixteenth-note steps (64 with `subdivision='32n'`) — two bars, looped. Optional per layer:
  velocities, `slides` (303 glides), `entry_loop`, `dropout_prob`, `loop_modulo`, `pan`, `sidechain`
  (overrides the role's duck depth), and `automation` of an effect parameter over each loop.
- Per genre: `BPM_RANGE`, `SWING`, `KEY_ROLES` (the part that defines the genre; the reveal stars it),
  `SIDECHAIN_DEPTH` and `SIDECHAIN_RELEASE` (in beats), `LEVEL_DB`, and `PROFILE` — what to listen for
  (drums, bass, signature sound, mood, which of them is the genre's `key_trait`) plus two hidden rhythm
  tags, `kick_pattern` and `bass_pattern`. The genres endpoint serves the profiles with the tempo taken
  from `BPM_RANGE`; a profile must describe what the generator actually plays.
- `generate(root_pc)` makes a track in a given key (the reveal's comparison track is made in the key of
  the track it is played against); every track reports its `root`. Selection lives in
  `managers/genre_catalog_manager.py`.
- `LEVEL_DB` is a measured output trim that keeps every genre near −18 dB RMS, so loudness is not a
  giveaway. It is cut-only (applied after the limiter, where a boost would clip). To re-measure, render
  three tracks of the genre with `GenreTrainerAudioService.renderWav` (in the browser console, via
  `ng.getComponent` on `app-genre-trainer-player`), take the RMS of the WAV with `LEVEL_DB` at 0, and set
  `LEVEL_DB = min(0, −18 − rms)`. Renders slow to a crawl while the tab is hidden.
- `tests/test_generators.py` is the rhythm grammar each genre must keep — psy kicks strictly
  four-on-the-floor, no bass on a kick step in four-on-the-floor genres (acid techno excepted), drum & bass
  and jungle keep the snare on 2 and 4, and so on. A pattern that breaks one of these teaches the ear the
  wrong cue, so a new pool entry has to pass them.
- Genre ids outlive their meaning: `hightek` is hi-tech psytrance, `psy_bass` is halftime psybass bass
  music, and `dark_psy` also covers forest psy. The frontend's labels (`shared/string-display/
  genre-type-display.ts`) say what they are now, along with the descriptions and the families.

## Frontend — `yanay-tevet-web/src/app/genre-trainer/`

- `GenreTrainerAudioService` owns playback: one track at a time on the global transport. Things that are
  easy to break:
  - **Loop counting** uses the transport's `loop` event. A repeat scheduled at `'2m'` never fires, because
    the transport wraps to 0 when it reaches `loopEnd`; an animation frame stops in a background tab.
  - **Sidechain** is a duck triggered by each hit of the layer with id `kick`, not a free-running LFO, so it
    stays on the kick whatever the pattern and however long the reverbs took to build.
  - **Slides**: the note before a slide chain is held to the chain's end, and each slide step calls
    `setNote` with portamento instead of retriggering.
  - `play()` is async (reverbs render impulse responses); a play or stop that arrives mid-build makes the
    older build dispose itself.
- `GenreTrainerService` holds the game state: adaptive next-genre pick (unseen, often-missed and
  often-confused genres come up more), per-genre stats and confusions in `localStorage`, and the reveal's
  comparison. `genre_trainer_stats_version` resets stats for genres whose meaning changed.
- On a miss the reveal explains it from the two profiles (in easy mode, against the guessed family's
  genre closest in tempo): a verdict (same family and overlapping tempo = Very close, one of them =
  Close), the traits side by side, and the trait that tells them apart — a tempo gap of 5 BPM or more,
  else a different kick pattern, else the real genre's own trait if it is melodic, else a different
  bass pattern, else the guessed genre's melodic trait. "Compare A/B" alternates the two tracks every two
  loops (`GenreTrainerAudioService.playAlternating`).

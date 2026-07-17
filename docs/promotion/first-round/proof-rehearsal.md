# LoveTypes Proof Rehearsal

- 產生日期：2026-07-18
- proof files：2
- rows：3
- active platforms：1
- profile pass：1 / 1
- post placeholder rejected：1 / 1
- post rehearsal real URL pass：1 / 1
- issues：0

## Rule

- This rehearsal runs check commands only; it never writes to trackers.
- Profile templates must pass because they are ready to use after external proof exists.
- Temporary post placeholder samples must fail even after current proof files contain real public URLs.
- Temporary post samples with platform-shaped URLs must pass import validation.

## Rows

### `post_placeholder_rehearsal` · youtube_shorts

- file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- expected：`reject`
- passed：`1`

### `post_rehearsal_real_url` · youtube_shorts

- file：`docs/promotion/first-round/proof-youtube_shorts-publish-lt-s01-iris-silence.txt`
- expected：`pass`
- passed：`1`

### `profile_template_current` · youtube_shorts

- file：`docs/promotion/first-round/proof-youtube_shorts.txt`
- expected：`pass`
- passed：`1`

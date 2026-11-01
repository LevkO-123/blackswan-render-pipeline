# Black Swan Python/FFmpeg rendering pipeline

Integration test adapted from existing local production renderer. Two native 2160x3840 Pexels sources are downloaded transiently and checked by SHA256; raw stock is not committed/distributed. Only transformed captioned test output is retained.

## Scope and cost
GitHub Actions is used ONLY for bounded software integration testing, not a bulk-content production farm. No cron, no paid generator, no Google credentials, no upload/publish integration. Standard public ubuntu-24.04 runner, ten-minute job, one-day artifact retention, maximum 80 MiB MP4, no media cache. Do not enable paid runners/storage. Current GitHub Actions terms restrict unrelated hosted-runner work; daily video production requires a separate authorized compute host.

## Reproduce
Python 3.12; pip install -r requirements.txt; python cloud_test.py.

Existing synthesis/edit graph/one-generation H264 encode and black/silence/decode QA preserved. Linux font switched to DejaVu Sans. Output 1080x1920, no upscale/fake8K. This 8.4-second fixture is NOT a new episode. Full human viewing/listening and YouTube Checks remain separate gates.

Source evidence: sources.json and https://www.pexels.com/license/ . No endorsement or standalone stock redistribution. Source audio excluded; existing original score is synthesized locally, not presented as a real engine.

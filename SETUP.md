# Setting up your animated GitHub profile README

This folder is a ready-to-push GitHub profile repo (`pateldarshil8/pateldarshil8`),
built following [avivashishta.com's guide](https://www.avivashishta.com/blog/build-animated-github-profile-readme.html).
Everything animates via self-contained SVG (SMIL/CSS keyframes) — no third-party
stats services, no GitHub token, no JavaScript.

## 0. What's already done for you

- `contrib-heatmap.svg` — generated from your **real** GitHub contribution
  data (fetched live, no token needed).
- `info-card.svg` — a neofetch-style card pre-filled with your background
  (MS Cybersecurity @ GWU, Security+/CC, GRC/NIST focus, prior internships).
  Edit `scripts/make_info_card.py` → `ROWS` to tweak the wording, then
  re-run it.
- `README.md` — lays out heatmap + portrait + card in the terminal style.
- `.github/workflows/update-profile-art.yml` — refreshes the heatmap daily.

**Not done yet — needs your photo:**
- `darshil-ascii.svg` — the ASCII portrait. Run steps 1–2 below with a
  headshot to generate it.

## 1. Create the special repo

```bash
gh repo create pateldarshil8 --public --clone
# then copy everything from this folder into that cloned repo
```

(The repo name must exactly match your username — that's what makes
GitHub render its README on your profile page.)

## 2. Generate the ASCII portrait (one-time, local only)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/prep_photo.py your-photo.jpg     # writes source-prepped.png
python scripts/make_ascii_svg.py                # writes darshil-ascii.svg
```

Use a well-lit, front-facing photo with decent contrast between you and
the background for the cleanest result — `rembg` handles background
removal automatically.

## 3. Commit and push

```bash
git add .
git commit -m "profile: animated terminal README"
git push
```

## 4. Verify the daily refresh

Go to the repo's **Actions** tab → run `Update profile art` manually once
(`workflow_dispatch`) to confirm it commits a fresh `contrib-heatmap.svg`.
After that it runs itself every day at ~06:17 UTC.

## Editing later

- **Change the info card text**: edit `ROWS` in `scripts/make_info_card.py`,
  re-run it, commit.
- **New photo**: repeat step 2.
- **Change username**: update `GH_USERNAME` in
  `.github/workflows/update-profile-art.yml` and the default in
  `scripts/fetch_contributions.py`.

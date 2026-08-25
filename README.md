# drachenhort-repo

Kodi addon repository serving updates for:

- [Twitch Center](https://github.com/drachenhort/twitch-center) (`script.twitch.center`)
- [Jellyfin (Plex-style)](https://github.com/drachenhort/jellyfin-kodi-plex) (`script.jellyfin.plex`)

## For users

Install `repository.drachenhort` once and Kodi will pick up updates for both
addons automatically:

1. Download the repository zip: `docs/repository.drachenhort/repository.drachenhort-1.0.0.zip`
   (from the raw GitHub URL or https://drachenhort.github.io/drachenhort-repo/repository.drachenhort/repository.drachenhort-1.0.0.zip)
2. In Kodi: Settings → Add-ons → Install from zip file → select the download.
3. Then install "Twitch Center" and "Jellyfin (Plex-style)" from
   Install from repository → drachenhort Kodi Addons.

## Structure

- `addons/twitch-center` and `addons/jellyfin-kodi-plex` — git submodules
  pointing at each addon's own repository (source of truth for the code).
- `repository.drachenhort/` — the repository addon itself, tells Kodi where
  to find `addons.xml`.
- `tools/build_repo.py` — reads each addon's `addon.xml` version, builds
  zips and the merged `docs/addons.xml` + `docs/addons.xml.md5`.
- `docs/` — generated output, served via GitHub Pages (Settings → Pages →
  branch `main`, folder `/docs`).

## Releasing an update

1. Bump the version in the addon's own repo (`addon.xml`), push, tag as
   usual.
2. In this repo: `git submodule update --remote addons/<name>` (or let the
   `Build Kodi repo` GitHub Action do it — it runs on push, on a daily
   schedule, and can be triggered manually).
3. `python3 tools/build_repo.py`
4. Commit `addons/` (submodule pointer bump) and `docs/`, push.

Kodi clients poll `addons.xml`/`addons.xml.md5` and offer the update once
the new zip is live.

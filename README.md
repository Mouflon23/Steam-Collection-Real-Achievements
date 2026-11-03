# Steam-Collection-Real-Achievements

## Python program to sort a Steam library by real achievements

Some games have achievements that will not appear on your profile after completion, because Steam flags them as "Profile Features Limited" (formerly "Steam is learning about this game"). This program finds which games of your library really count, and proposes the changes to apply on your collections.

---

## How it works

1. Your library is read from the local Steam files: the collections, and the client cache for the games not sorted yet.
2. The public Steam store API gives the achievements category of each app, by batches of 200.
3. Steam hides this category on many games, so the apps without it are checked one by one in the global achievement statistics.
4. The store page of each game with achievements tells if its profile features are limited.
5. Each game is assigned to a collection, and the changes are written in a report.
6. With `--apply`, the changes go through the Steam client itself, which saves and syncs the collections.

**Without `--apply`, this program does not change anything in Steam.** Results stay in a cache for 30 days, so a second run only looks up what is new, and a stopped run continues where it was.

To apply, Steam is restarted with its debug port (`-cef-enable-debugging`), then restarted normally: this port gives access to the client while it is open. The collections are backed up in `output` first. Demos and family library games are sorted too. Apps that are not in the library, like removed licenses, are skipped and left out of the next reports.

| Game | Collection |
| --- | --- |
| With achievements | `SUCCÉS` |
| With achievements, limited profile features | `PROFIL LIMITÉ / SIL` |
| Without achievements | `PAS DE SUCCÉS` |
| No information from Steam, not sorted yet | `AUCUN INFO DISPO` |

A game without information from Steam keeps its current collection. Games in `DONE`, `SUCCÉS NON FAISABLE / dropped` and `Masqués` are never moved. These names are at the top of `classify.py`.

---

## Usage

Tested on Windows 11 with Python 3.12. The first run sends thousands of requests, a few hours for a large library. No Steam API key is needed.

```bash
python -m venv venv
```

```bash
venv\Scripts\python -m pip install -r requirements.txt
```

```bash
venv\Scripts\python main.py
```

The report is written to `output\report.md`, and `output\report.json` holds the same changes for a program.

| Option | Use |
| --- | --- |
| `--apply` | Apply the changes in Steam, no game must be running |
| `--limit 400` | Try on the first 400 apps |
| `--refresh` | Ignore the cache |
| `--delay 1` | Slow down the store pages, 0.5 s by default |
| `--steam-path D:\Steam` | Steam folder, read from the registry by default |
| `--user 123456` | Folder in `userdata`, with several accounts on the computer |

```bash
venv\Scripts\python -m unittest discover -s tests
```

---

## Limits

- The local client cache also lists apps outside your library. They are in their own section of the report, and `--apply` checks them in the client.
- Steam client internals can change with an update. If `--apply` fails, nothing is lost: games are added before being removed, and the backup is in `output`.

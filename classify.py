import json
import os
from datetime import date, timedelta

ACHIEVEMENTS = 'SUCCÉS'
LIMITED = 'PROFIL LIMITÉ / SIL'
NO_ACHIEVEMENTS = 'PAS DE SUCCÉS'
UNKNOWN = 'AUCUN INFO DISPO'
# Collections filled by this program. A game must end up in only one of them.
SORTED_COLLECTIONS = (ACHIEVEMENTS, LIMITED, NO_ACHIEVEMENTS, UNKNOWN, 'NO SUCCESS OR PL/SIL')
# Games placed here by hand are never moved
PROTECTED_COLLECTIONS = ('DONE', 'SUCCÉS NON FAISABLE / dropped', 'Masqués')
# Store types sorted even outside the collections: games, demos, playtests, and apps without store data.
# The Steam client drops the ones that are not in the library when applying.
LIBRARY_TYPES = (0, 1, 12, None)
CACHE_MAX_AGE_DAYS = 30

def load_cache(file_path):
    if not os.path.isfile(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as file:
        return {int(app_id): entry for app_id, entry in json.load(file).items()}

def save_cache(file_path, cache):
    # Written to a temporary file first: stopping the program must not lose hours of requests
    temporary_path = f'{file_path}.tmp'
    with open(temporary_path, 'w', encoding='utf-8') as file:
        json.dump(cache, file, indent=1, ensure_ascii=False)
    os.replace(temporary_path, file_path)

def is_fresh(entry, today):
    return date.fromisoformat(entry['checked']) >= today - timedelta(days=CACHE_MAX_AGE_DAYS)

def classify(entry):
    """
    Choose the collection of a game from its cache entry.
    """
    if entry is None or entry.get('achievements') is None:
        return UNKNOWN
    if not entry['achievements']:
        return NO_ACHIEVEMENTS
    limited = entry.get('limited')
    if limited is None:
        return UNKNOWN
    return LIMITED if limited else ACHIEVEMENTS

def select_apps(cache, collections, app_ids):
    """
    Keep the apps to sort: everything already in a collection, and the others if they can be played.
    """
    in_collections = set().union(*collections.values())
    return [app_id for app_id in app_ids
            if app_id in in_collections or cache.get(app_id, {}).get('type') in LIBRARY_TYPES]

def plan_moves(cache, collections, app_ids):
    """
    List the changes to apply on the collections, without changing anything.
    """
    in_collections = set().union(*collections.values())
    protected = set().union(*(collections.get(name, set()) for name in PROTECTED_COLLECTIONS))

    moves = []
    for app_id in app_ids:
        if app_id in protected or cache.get(app_id, {}).get('in_library') is False:
            continue
        current = [name for name in SORTED_COLLECTIONS if app_id in collections.get(name, set())]
        entry = cache.get(app_id)
        target = classify(entry)
        # Having no information is not a reason to undo a previous sort
        if target == UNKNOWN and current:
            continue
        if current == [target]:
            continue
        moves.append({
            'appid': app_id,
            'name': (entry or {}).get('name') or f'App {app_id}',
            'from': [name for name in current if name != target],
            'to': target,
            'new_to_collections': app_id not in in_collections,
        })
    return moves

def count_targets(cache, app_ids):
    counts = {}
    for app_id in app_ids:
        target = classify(cache.get(app_id))
        counts[target] = counts.get(target, 0) + 1
    return counts

def format_report(moves, counts):
    lines = ['# Rapport de tri Steam', '', 'Rien n\'a été modifié dans Steam.', '', '## Classement selon Steam', '']
    lines += [f'- {name} : {count}' for name, count in sorted(counts.items())]
    lines += ['', f'## Changements proposés : {len(moves)}', '']

    groups = {}
    for move in moves:
        origin = ', '.join(move['from']) or ('hors collections' if move['new_to_collections'] else 'aucune collection triée')
        groups.setdefault((origin, move['to']), []).append(move)

    for (origin, target), group in sorted(groups.items(), key=lambda item: -len(item[1])):
        lines += [f'### {origin} → {target} ({len(group)})', '']
        if origin == 'hors collections':
            lines += ['Le cache local de Steam contient aussi des applications hors bibliothèque : '
                      '--apply ne garde que celles de ta bibliothèque, jeux de la famille compris.', '']
        lines += [f'- [{move["name"]}](https://store.steampowered.com/app/{move["appid"]}/)'
                  for move in sorted(group, key=lambda move: move['name'].lower())]
        lines.append('')
    return '\n'.join(lines)

def write_report(folder, moves, counts):
    with open(os.path.join(folder, 'report.json'), 'w', encoding='utf-8') as file:
        json.dump({'counts': counts, 'moves': moves}, file, indent=1, ensure_ascii=False)
    with open(os.path.join(folder, 'report.md'), 'w', encoding='utf-8') as file:
        file.write(format_report(moves, counts))

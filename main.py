import argparse
import os
import sys
import time
from datetime import date

import classify
import steamClient
import steamLibrary
import steamStore

OUTPUT_FOLDER = 'output'
CACHE_PATH = os.path.join(OUTPUT_FOLDER, 'appCache.json')
SAVE_EVERY = 25

def update_items(session, cache, app_ids, today, refresh):
    """
    Get the achievements of every app whose cache entry is missing or too old.
    """
    stale = [app_id for app_id in app_ids
             if refresh or app_id not in cache or not classify.is_fresh(cache[app_id], today)]
    print(f'{len(app_ids)} apps, {len(stale)} to look up on Steam.')
    for start in range(0, len(stale), steamStore.BATCH_SIZE):
        batch = stale[start:start + steamStore.BATCH_SIZE]
        items = steamStore.fetch_items(session, batch)
        for app_id in batch:
            # Without store data, achievements stays unknown instead of being guessed
            cache[app_id] = {'name': '', 'type': None, 'achievements': None,
                             **items.get(app_id, {}), 'checked': today.isoformat()}
        print(f'Store data: {start + len(batch)}/{len(stale)}')

def run_steps(label, pending, cache, step):
    """
    Run a long task for each app, saving the cache regularly so that it can be stopped.
    """
    print(f'{label}: {len(pending)} to read.')
    started = time.time()
    for done, app_id in enumerate(pending, start=1):
        step(app_id)
        if done % SAVE_EVERY == 0:
            classify.save_cache(CACHE_PATH, cache)
            remaining = (time.time() - started) / done * (len(pending) - done)
            print(f'{label}: {done}/{len(pending)}, about {remaining / 60:.0f} min left')

def update_hidden_achievements(session, cache, app_ids):
    """
    Check the apps without the achievements category, because Steam hides it on many games.
    """
    def step(app_id):
        cache[app_id]['achievements'] = steamStore.fetch_has_achievements(session, app_id)
        cache[app_id]['stats_checked'] = True

    pending = [app_id for app_id in app_ids
               if cache[app_id]['achievements'] is False and 'stats_checked' not in cache[app_id]]
    run_steps('Global statistics', pending, cache, step)

def update_limited(session, cache, app_ids, delay):
    """
    Open the store page of the games with achievements to find the limited ones.
    """
    def step(app_id):
        cache[app_id]['limited'] = steamStore.fetch_limited(session, app_id)
        time.sleep(delay)

    pending = [app_id for app_id in app_ids if cache[app_id]['achievements'] and 'limited' not in cache[app_id]]
    run_steps('Store pages', pending, cache, step)

def apply_to_steam(steam_path, user_id, cache, moves):
    """
    Restart Steam in debug mode, apply the moves through the client, then restart it normally.
    """
    if steamClient.running_game():
        print('A game is running, close it before applying.')
        return 1
    print(f'Backup: {steamClient.backup_collections(steam_path, user_id, OUTPUT_FOLDER)}')
    print('Restarting Steam in debug mode...')
    steamClient.restart_steam(steam_path, debug=True)
    try:
        steamClient.wait_for_library()
        result = steamClient.apply_moves(moves)
    finally:
        print('Restarting Steam normally...')
        steamClient.restart_steam(steam_path, debug=False)

    if 'error' in result:
        print(f'Nothing applied: {result["error"]}')
        return 1
    # Family games and removed licenses stay out of the next reports
    for app_id in result['notOwned']:
        cache[app_id]['owned'] = False
    classify.save_cache(CACHE_PATH, cache)
    for name, count in result['added'].items():
        print(f'+{count} in {name}')
    for name, count in result['removed'].items():
        print(f'-{count} from {name}')
    print(f'{len(result["notOwned"])} games skipped because they are not in your own library.')
    return 0

def main():
    parser = argparse.ArgumentParser(description='Sort a Steam library by real achievements, without changing it.')
    parser.add_argument('--steam-path', help='Steam folder, read from the registry by default')
    parser.add_argument('--user', help='folder name in Steam userdata, only needed with several accounts')
    parser.add_argument('--refresh', action='store_true', help=f'ignore the cache, kept {classify.CACHE_MAX_AGE_DAYS} days')
    parser.add_argument('--limit', type=int, help='only look at the first apps, to try the program')
    parser.add_argument('--delay', type=float, default=0.5, help='seconds between two store pages')
    parser.add_argument('--apply', action='store_true', help='apply the changes in Steam, it restarts Steam twice')
    args = parser.parse_args()
    if args.apply and args.limit:
        parser.error('--apply needs the whole library, without --limit')

    steam_path = args.steam_path or steamLibrary.find_steam_path()
    user_id = args.user or steamLibrary.find_user_id(steam_path)
    collections = steamLibrary.read_collections(steamLibrary.cloud_storage_path(steam_path, user_id))
    app_ids = sorted(set().union(*collections.values()) | steamLibrary.read_cached_app_ids(steam_path))
    if args.limit:
        app_ids = app_ids[:args.limit]

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    today = date.today()
    session = steamStore.create_session()
    cache = classify.load_cache(CACHE_PATH)

    try:
        update_items(session, cache, app_ids, today, args.refresh)
        classify.save_cache(CACHE_PATH, cache)
        app_ids = classify.select_apps(cache, collections, app_ids)
        update_hidden_achievements(session, cache, app_ids)
        update_limited(session, cache, app_ids, args.delay)
    except (KeyboardInterrupt, steamStore.SteamUnavailable) as error:
        classify.save_cache(CACHE_PATH, cache)
        print(f'Stopped: {error or "interrupted"}. Run again to continue from the cache.')
        return 1

    classify.save_cache(CACHE_PATH, cache)
    moves = classify.plan_moves(cache, collections, app_ids)
    counts = classify.count_targets(cache, app_ids)
    classify.write_report(OUTPUT_FOLDER, moves, counts)
    if args.apply:
        print(f'{len(moves)} changes to apply, see {OUTPUT_FOLDER}\\report.md')
        return apply_to_steam(steam_path, user_id, cache, moves) if moves else 0
    print(f'{len(moves)} changes proposed, nothing was changed in Steam. See {OUTPUT_FOLDER}\\report.md')
    return 0

if __name__ == '__main__':
    sys.exit(main())

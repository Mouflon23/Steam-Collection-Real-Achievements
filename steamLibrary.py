import json
import os

def find_steam_path():
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as key:
        return winreg.QueryValueEx(key, 'SteamPath')[0]

def cloud_storage_path(steam_path, user_id):
    return os.path.join(steam_path, 'userdata', user_id, 'config', 'cloudstorage', 'cloud-storage-namespace-1.json')

def find_user_id(steam_path):
    userdata = os.path.join(steam_path, 'userdata')
    users = [name for name in os.listdir(userdata) if os.path.isfile(cloud_storage_path(steam_path, name))]
    if len(users) != 1:
        raise SystemExit(f'Expected one Steam account in {userdata}, found: {users}. Use --user.')
    return users[0]

def read_collections(file_path):
    """
    Read the Steam collections as a dictionary of collection name => set of appIDs.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        entries = json.load(file)

    collections = {}
    for key, entry in entries:
        if not key.startswith('user-collections.') or entry.get('is_deleted') or 'value' not in entry:
            continue
        collection = json.loads(entry['value'])
        collections[collection['name']] = set(collection.get('added', []))
    return collections

def read_cached_app_ids(steam_path):
    """
    List the apps known to the Steam client: games, but also DLC, soundtracks, trailers...
    It can hold apps that are not owned, the public API cannot tell without a profile in public mode.
    """
    library_cache = os.path.join(steam_path, 'appcache', 'librarycache')
    return {int(name) for name in os.listdir(library_cache) if name.isdigit()}

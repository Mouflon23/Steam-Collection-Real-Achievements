import json
import os
import shutil
import subprocess
import time
from datetime import datetime
import requests
import websocket

from steamLibrary import cloud_storage_path

DEBUG_URL = 'http://127.0.0.1:8080/json'
DEBUG_TARGET = 'SharedJSContext'
WAIT_SECONDS = 300

# Runs inside the Steam client: the client saves the collections and syncs them itself.
# Games are added before being removed, so that a stop in between does not lose any.
APPLY_SCRIPT = '''(async () => {
  const moves = %s;
  const names = %s;
  const collections = {};
  for (const name of names) {
    const found = collectionStore.GetUserCollectionsByName(name);
    if (found.length !== 1) return { error: `${found.length} collections named ${name}` };
    collections[name] = found[0];
  }
  const owned = collectionStore.myGamesCollection.apps;
  const toAdd = {}, toRemove = {}, notOwned = [];
  for (const move of moves) {
    const app = appStore.GetAppOverviewByAppID(move.appid);
    if (!app || (move.new_to_collections && !owned.has(move.appid))) {
      notOwned.push(move.appid);
      continue;
    }
    (toAdd[move.to] = toAdd[move.to] || []).push(app);
    for (const name of move.from) (toRemove[name] = toRemove[name] || []).push(app);
  }
  const added = {}, removed = {};
  for (const [name, apps] of Object.entries(toAdd)) {
    collections[name].AsDragDropCollection().AddApps(apps);
    await collections[name].Save();
    added[name] = apps.length;
  }
  for (const [name, apps] of Object.entries(toRemove)) {
    collections[name].AsDragDropCollection().RemoveApps(apps);
    await collections[name].Save();
    removed[name] = apps.length;
  }
  return { added, removed, notOwned };
})()'''

READY_SCRIPT = "typeof collectionStore !== 'undefined' && collectionStore.myGamesCollection.apps.size > 0"

def backup_collections(steam_path, user_id, folder):
    source = os.path.dirname(cloud_storage_path(steam_path, user_id))
    destination = os.path.join(folder, f'backup-collections-{datetime.now():%Y%m%d-%H%M%S}')
    shutil.copytree(source, destination)
    return destination

def running_game():
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as key:
        return winreg.QueryValueEx(key, 'RunningAppID')[0]

def is_steam_running():
    output = subprocess.run(['tasklist', '/NH', '/FI', 'IMAGENAME eq steam.exe'], capture_output=True, text=True).stdout
    return 'steam.exe' in output.lower()

def restart_steam(steam_path, debug):
    """
    Restart Steam, with the debug port only when asked: it gives access to the client.
    """
    executable = os.path.join(steam_path, 'steam.exe')
    if is_steam_running():
        subprocess.run([executable, '-shutdown'])
        deadline = time.time() + 60
        while is_steam_running():
            if time.time() > deadline:
                raise SystemExit('Steam did not close.')
            time.sleep(1)
        time.sleep(3)
    arguments = [executable, '-cef-enable-debugging'] if debug else [executable]
    subprocess.Popen(arguments, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

def evaluate(expression):
    targets = requests.get(DEBUG_URL, timeout=5).json()
    target = next(target for target in targets if target['title'] == DEBUG_TARGET)
    connection = websocket.create_connection(target['webSocketDebuggerUrl'], timeout=120, suppress_origin=True)
    try:
        connection.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {
            'expression': expression, 'awaitPromise': True, 'returnByValue': True}}))
        while True:
            message = json.loads(connection.recv())
            if message.get('id') == 1:
                break
    finally:
        connection.close()
    result = message['result']
    if 'exceptionDetails' in result:
        raise RuntimeError(result['exceptionDetails'].get('exception', {}).get('description', result['exceptionDetails']))
    return result['result'].get('value')

def wait_for_library():
    """
    Wait for the debug port, then for the library: the collections are empty until it is loaded.
    """
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        try:
            if evaluate(READY_SCRIPT):
                return
        except (requests.RequestException, StopIteration, websocket.WebSocketException, RuntimeError, OSError):
            pass
        time.sleep(3)
    raise SystemExit('The Steam library did not load in debug mode.')

def collection_names(moves):
    return sorted({move['to'] for move in moves} | {name for move in moves for name in move['from']})

def apply_moves(moves):
    return evaluate(APPLY_SCRIPT % (json.dumps(moves), json.dumps(collection_names(moves))))

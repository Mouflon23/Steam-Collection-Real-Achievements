import json
import re
import time
import requests

ITEMS_URL = 'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/'
GLOBAL_ACHIEVEMENTS_URL = 'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/'
STORE_PAGE_URL = 'https://store.steampowered.com/app/{}/'
# Above this size the URL gets too long and Steam answers 400
BATCH_SIZE = 200
ACHIEVEMENTS_CATEGORY = 22
RETRIES = 5
FIRST_BACKOFF_SECONDS = 30
TRANSIENT_STATUS = (403, 429, 500, 502, 503, 504)

class SteamUnavailable(Exception):
    pass

def create_session():
    session = requests.Session()
    # Pass the age check, otherwise mature games redirect to a page without any information
    session.cookies.update({'birthtime': '0', 'lastagecheckage': '1-0-1990', 'wants_mature_content': '1'})
    return session

def get_with_retry(session, url, sleep=time.sleep, accept=lambda response: False, **kwargs):
    """
    GET a URL, waiting longer after each failure because Steam throttles with 403 and 429.
    A response validated by accept is returned whatever its status.
    """
    last_error = None
    for attempt in range(RETRIES):
        try:
            response = session.get(url, timeout=30, **kwargs)
            if accept(response):
                return response
            if response.status_code not in TRANSIENT_STATUS:
                response.raise_for_status()
                return response
            last_error = f'status {response.status_code}'
        except requests.ConnectionError as error:
            last_error = error
        except requests.Timeout as error:
            last_error = error
        if attempt < RETRIES - 1:
            wait = FIRST_BACKOFF_SECONDS * 2 ** attempt
            print(f'Steam is not answering ({last_error}). Waiting {wait}s...')
            sleep(wait)
    raise SteamUnavailable(f'{url}: {last_error}')

def fetch_items(session, app_ids):
    """
    Get the store information of up to BATCH_SIZE apps.
    An app missing from the result has no store data: delisted or not available in this country.
    achievements False is not proof: Steam hides this category on many games, see fetch_has_achievements.
    """
    request = {
        'ids': [{'appid': app_id} for app_id in app_ids],
        'context': {'language': 'french', 'country_code': 'FR'},
        'data_request': {'include_basic_info': True},
    }
    response = get_with_retry(session, ITEMS_URL, params={'input_json': json.dumps(request)})

    items = {}
    for item in response.json()['response'].get('store_items', []):
        if item.get('success') != 1:
            continue
        categories = item.get('categories', {}).get('feature_categoryids', [])
        items[item['appid']] = {
            'name': item.get('name', ''),
            'type': item.get('type', 0),
            'achievements': ACHIEVEMENTS_CATEGORY in categories,
        }
    return items

def has_no_stats(response):
    # This is how the API answers for an app without achievements, a throttled request has another body
    return response.status_code == 403 and response.text.strip() == '{}'

def fetch_has_achievements(session, app_id):
    """
    Ask the global achievement statistics, which do not depend on what the store chooses to show.
    """
    response = get_with_retry(session, GLOBAL_ACHIEVEMENTS_URL, accept=has_no_stats, params={'gameid': app_id})
    if has_no_stats(response):
        return False
    return len(response.json().get('achievementpercentages', {}).get('achievements', [])) > 0

def page_is_limited(html):
    """
    Tell from a store page if the game is "Profile Features Limited" (it replaced "Steam is learning").
    Return None if this is not a game page: Steam redirects when it refuses to show it.
    The CSS class is used because the visible text depends on the language.
    """
    if 'apphub_AppName' not in html:
        return None
    return re.search(r'class="[^"]*\blearning_about\b', html) is not None

def fetch_limited(session, app_id):
    return page_is_limited(get_with_retry(session, STORE_PAGE_URL.format(app_id)).text)

import json
import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import classify
from classify import ACHIEVEMENTS, LIMITED, NO_ACHIEVEMENTS, UNKNOWN
from steamLibrary import read_collections
import steamClient
import steamStore

class ClassifyTest(unittest.TestCase):

    def test_rules(self):
        self.assertEqual(classify.classify(None), UNKNOWN)
        self.assertEqual(classify.classify({'achievements': False}), NO_ACHIEVEMENTS)
        self.assertEqual(classify.classify({'achievements': True, 'limited': False}), ACHIEVEMENTS)
        self.assertEqual(classify.classify({'achievements': True, 'limited': True}), LIMITED)
        self.assertEqual(classify.classify({'achievements': True, 'limited': None}), UNKNOWN)

    def test_limited_game_without_achievements_has_no_achievements(self):
        self.assertEqual(classify.classify({'achievements': False, 'limited': True}), NO_ACHIEVEMENTS)

    def test_cache_expires(self):
        today = date(2026, 11, 1)
        self.assertTrue(classify.is_fresh({'checked': '2026-10-02'}, today))
        self.assertFalse(classify.is_fresh({'checked': '2026-10-01'}, today))

class PlanMovesTest(unittest.TestCase):

    def plan(self, cache, collections, app_ids):
        return {move['appid']: move for move in classify.plan_moves(cache, collections, app_ids)}

    def test_well_sorted_game_does_not_move(self):
        cache = {1: {'name': 'A', 'achievements': False}}
        self.assertEqual(self.plan(cache, {NO_ACHIEVEMENTS: {1}}, [1]), {})

    def test_misplaced_game_moves(self):
        cache = {1: {'name': 'A', 'achievements': True, 'limited': False}}
        move = self.plan(cache, {NO_ACHIEVEMENTS: {1}}, [1])[1]
        self.assertEqual((move['from'], move['to']), ([NO_ACHIEVEMENTS], ACHIEVEMENTS))

    def test_game_in_two_sorted_collections_leaves_the_wrong_one(self):
        cache = {1: {'name': 'A', 'achievements': False}}
        move = self.plan(cache, {NO_ACHIEVEMENTS: {1}, ACHIEVEMENTS: {1}}, [1])[1]
        self.assertEqual((move['from'], move['to']), ([ACHIEVEMENTS], NO_ACHIEVEMENTS))

    def test_missing_information_keeps_previous_sort(self):
        self.assertEqual(self.plan({}, {ACHIEVEMENTS: {1}}, [1]), {})

    def test_protected_game_never_moves(self):
        cache = {1: {'name': 'A', 'achievements': False}}
        self.assertEqual(self.plan(cache, {ACHIEVEMENTS: {1}, 'DONE': {1}}, [1]), {})

    def test_app_outside_library_never_moves(self):
        cache = {1: {'name': 'A', 'achievements': False, 'in_library': False}}
        self.assertEqual(self.plan(cache, {}, [1]), {})

    def test_collection_names_used_by_moves(self):
        moves = [{'from': ['A', 'B'], 'to': 'C'}, {'from': [], 'to': 'A'}]
        self.assertEqual(steamClient.collection_names(moves), ['A', 'B', 'C'])

    def test_game_outside_collections_is_flagged(self):
        cache = {1: {'name': 'A', 'achievements': False}}
        self.assertTrue(self.plan(cache, {ACHIEVEMENTS: {2}}, [1])[1]['new_to_collections'])

    def test_select_apps_keeps_playable_apps_and_collections(self):
        cache = {1: {'type': 0}, 2: {'type': 4}, 3: {'type': 4}, 4: {'type': 1}, 5: {'type': None}, 6: {'type': 11}}
        self.assertEqual(classify.select_apps(cache, {'VR': {3}}, [1, 2, 3, 4, 5, 6]), [1, 3, 4, 5])

class FakeResponse:

    def __init__(self, status_code=200, payload=None, text=''):
        self.status_code = status_code
        self.payload = payload
        self.text = text

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload

class FakeSession:

    def __init__(self, responses):
        self.responses = list(responses)

    def get(self, url, **kwargs):
        return self.responses.pop(0)

class StoreTest(unittest.TestCase):

    def test_limited_page(self):
        html = '<div class="apphub_AppName">A</div><div class="game_area_details_specs_ctn learning_about">'
        self.assertTrue(steamStore.page_is_limited(html))

    def test_normal_page(self):
        self.assertFalse(steamStore.page_is_limited('<div class="apphub_AppName">A</div>'))

    def test_redirected_page_gives_no_answer(self):
        self.assertIsNone(steamStore.page_is_limited('<html>Welcome to Steam</html>'))

    def test_items_are_parsed_and_failures_ignored(self):
        payload = {'response': {'store_items': [
            {'appid': 620, 'success': 1, 'name': 'Portal 2', 'type': 0, 'categories': {'feature_categoryids': [22, 23]}},
            {'appid': 10, 'success': 1, 'name': 'Other', 'categories': {'feature_categoryids': [23]}},
            {'appid': 0, 'success': 15},
        ]}}
        items = steamStore.fetch_items(FakeSession([FakeResponse(payload=payload)]), [620, 10, 99])
        self.assertEqual(set(items), {620, 10})
        self.assertTrue(items[620]['achievements'])
        self.assertFalse(items[10]['achievements'])

    def test_global_statistics_find_achievements(self):
        payload = {'achievementpercentages': {'achievements': [{'name': 'A', 'percent': 1}]}}
        session = FakeSession([FakeResponse(payload=payload)])
        self.assertTrue(steamStore.fetch_has_achievements(session, 1))

    def test_empty_global_statistics(self):
        session = FakeSession([FakeResponse(payload={'achievementpercentages': {'achievements': []}})])
        self.assertFalse(steamStore.fetch_has_achievements(session, 1))

    def test_no_global_statistics(self):
        session = FakeSession([FakeResponse(403, text='{}')])
        self.assertFalse(steamStore.fetch_has_achievements(session, 1))

    def test_throttled_global_statistics_are_not_read_as_no_achievements(self):
        self.assertFalse(steamStore.has_no_stats(FakeResponse(403, text='<html>Access denied</html>')))

    def test_throttling_is_retried(self):
        session = FakeSession([FakeResponse(429), FakeResponse(text='ok')])
        response = steamStore.get_with_retry(session, 'url', sleep=lambda seconds: None)
        self.assertEqual(response.text, 'ok')

    def test_gives_up_after_retries(self):
        session = FakeSession([FakeResponse(429)] * steamStore.RETRIES)
        with self.assertRaises(steamStore.SteamUnavailable):
            steamStore.get_with_retry(session, 'url', sleep=lambda seconds: None)

class CollectionsTest(unittest.TestCase):

    def test_read_collections(self):
        entries = [
            ['user-collections.a', {'value': json.dumps({'name': 'A', 'added': [1, 2]})}],
            ['user-collections.b', {'is_deleted': True}],
            ['showcases.1', {'value': '{}'}],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'collections.json')
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(entries, file)
            self.assertEqual(read_collections(path), {'A': {1, 2}})

if __name__ == '__main__':
    unittest.main()

import json

def read_json_without_bom(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        return json.load(file)

# Read the JSON files with UTF-8 encoding and BOM handling
pl = read_json_without_bom('Steam-Collection-Games-Success\JSON\PL.json')
sil = read_json_without_bom('Steam-Collection-Games-Success\JSON\SIL.json')
achievement = read_json_without_bom('Steam-Collection-Games-Success\JSON\Achievement.json')

# Step 2: Merge PL and SIL without duplicates
pl_sil = list(set(pl + sil))

# Step 3: Save merged result to PL_SIL.json with ensure_ascii=False to properly display characters
with open('Steam-Collection-Games-Success\JSON\PL_SIL.json', 'w', encoding='utf-8') as pl_sil_file:
    json.dump(pl_sil, pl_sil_file, indent=2, ensure_ascii=False)

# Step 4: Remove values from Achievement.json that are in PL_SIL.json
achievement_final = [item for item in achievement if item not in pl_sil]

# Step 5: Save the filtered achievements to AchievementFinal.json with ensure_ascii=False
with open('Steam-Collection-Games-Success\JSON\AchievementFinal.json', 'w', encoding='utf-8') as achievement_final_file:
    json.dump(achievement_final, achievement_final_file, indent=2, ensure_ascii=False)

print('Merging and filtering complete!')
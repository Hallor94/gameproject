# file: entities/enemy_character_loader.py

import os
import random
from collections import Counter

from entities.enemy_character import EnemyCharacter
from entities.enemy import Enemy
from utils.json_loader import load_json_file
from utils import globals as G
from utils.logger import log_info, log_warn, log_error, log_debug

ENEMY_JSON_DIR = "data/enemies/base"
ENEMY_IMAGE_DIR = "assets/enemies/base"
FALLBACK_IMAGE = "nemo.png"

def load_enemies(allowed_types=None):
    validate_enemy_assets()
    enemies = []

    for file in os.listdir(ENEMY_IMAGE_DIR):
        if not file.endswith(".png") or "_standee_" not in file:
            continue

        try:
            base_type, suffix = file.replace(".png", "").split("_standee_")
        except ValueError:
            log_warn("EnemyLoader", f"Invalid standee file name format: {file}", file=__file__)
            continue

        if allowed_types and base_type not in allowed_types:
            continue

        # Assign keys and check fallback
        standee_key = f"{base_type}_standee_{suffix}"
        portrait_key = f"{base_type}_portrait_{suffix}"
        portrait_path = os.path.join(ENEMY_IMAGE_DIR, portrait_key + ".png")
        if not os.path.exists(portrait_path):
            log_warn("EnemyLoader", f"Missing portrait: {portrait_path}, using standee as fallback", file=__file__)
            portrait_key = standee_key

        # Route to correct JSON source
        if suffix.isdigit():
            json_path = os.path.join(ENEMY_JSON_DIR, f"{base_type}.json")
            char_id = f"{base_type}_{suffix}"
            use_random = True
        else:
            json_path = os.path.join(ENEMY_JSON_DIR, f"{base_type}_{suffix}.json")
            char_id = f"{base_type}_{suffix}"
            use_random = None  # obey JSON setting

        if not os.path.exists(json_path):
            log_warn("EnemyLoader", f"Missing JSON for {char_id}: {json_path}", file=__file__)
            continue

        entry = load_json_file(json_path).copy()
        entry["char_id"] = char_id
        entry["image"] = f"{base_type}_{suffix}"
        if use_random is not None:
            entry["random_stats"] = use_random

        character = EnemyCharacter.from_json_entry(
            entry,
            variant_suffix=suffix,
            standee_key=standee_key,
            portrait_key=portrait_key
        )

        respawn = entry.get("respawn_allowed", suffix.isdigit())
        enemies.append(Enemy(char_id, character, respawn_allowed=respawn))

        stats_summary = {
            "STR": character.strength,
            "END": character.endurance,
            "DEX": character.dexterity,
            "INT": character.intelligence,
            "NRV": character.nerve,
            "LCK": character.luck,
            "HP": character.health_base,
            "MOV": character.move_points_base,
            "ATK": character.attack_base
        }

        log_debug("EnemyPool", f"{char_id} [{suffix}] → {character.display_name} "
                               f"[standee={standee_key}] "
                               f"[portrait={portrait_key}] "
                               f"[stats={stats_summary}]", file=__file__)

    summary = Counter(e.character_base_type for e in enemies)
    log_info("EnemyLoader", f"Final enemy pool by type: {dict(summary)}", file=__file__)
    log_info("EnemyLoader", f"Total enemies loaded: {len(enemies)}", file=__file__)
    return enemies

# --- Helpers ---

def _get_image_pool(base_type, role):
    return sorted([
        f for f in os.listdir(ENEMY_IMAGE_DIR)
        if f.startswith(f"{base_type}_{role}_") and f.endswith(".png") and _is_generic_image_name(f)
    ])

def _get_unique_variant_id(base_type, used_variants):
    pool = _get_image_pool(base_type, "standee")
    ids = [f.split("_")[-1].split(".")[0] for f in pool]
    used = used_variants.setdefault(base_type, set())
    unused = [i for i in ids if i not in used]

    if not unused:
        used.clear()
        unused = ids[:]

    variant = random.choice(unused)
    used.add(variant)
    return variant

def _build_image_path(base_type, role, variant):
    return os.path.join(ENEMY_IMAGE_DIR, f"{base_type}_{role}_{variant}.png")

def _is_generic_image_name(image_name):
    name_part = os.path.splitext(os.path.basename(image_name))[0]
    suffix = name_part.split("_")[-1]
    return suffix.isdigit()

def validate_enemy_assets():
    missing_json = []
    missing_portraits = []
    total = 0

    for file in os.listdir(ENEMY_IMAGE_DIR):
        if not file.endswith(".png") or "_standee_" not in file:
            continue

        total += 1
        name = file.replace(".png", "")
        try:
            base_type, suffix = name.split("_standee_")
        except ValueError:
            log_warn("Validator", f"Invalid standee file name format: {file}", file=__file__)
            continue

        # Check portrait
        portrait_path = os.path.join(ENEMY_IMAGE_DIR, f"{base_type}_portrait_{suffix}.png")
        if not os.path.exists(portrait_path):
            missing_portraits.append(f"{base_type}_portrait_{suffix}.png")

        # Check JSON
        if suffix.isdigit():
            json_file = f"{base_type}.json"
        else:
            json_file = f"{base_type}_{suffix}.json"

        json_path = os.path.join(ENEMY_JSON_DIR, json_file)
        if not os.path.exists(json_path):
            missing_json.append(json_file)

    if missing_json:
        log_warn("Validator", f"Missing JSON files: {missing_json}", file=__file__)
    if missing_portraits:
        log_warn("Validator", f"Missing portrait images: {missing_portraits}", file=__file__)

    log_info("Validator", f"Validated {total} standee variants.", file=__file__)

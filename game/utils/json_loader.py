# file: utils/json_loader.py

import json
import os
import glob
from utils.logger import log_warn


def load_json_files(folder, recursive=True):
    pattern = "**/*.json" if recursive else "*.json"
    files = glob.glob(os.path.join(folder, pattern), recursive=recursive)
    return [load_json_file(path) for path in files]


def load_json_file(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        log_warn("JsonLoader", f"Failed to load {path}: {e}", file=__file__)
        return None


def flatten_json_entries(data):
    if isinstance(data, list):
        return data
    return [data]


def load_all_json_entries(folder, recursive=True):
    """
    Globs the folder recursively (if enabled) and returns a flat list of all JSON entries.
    Supports JSON files that contain a single object or a list of objects.
    """
    raw_files = load_json_files(folder, recursive=recursive)
    all_entries = []
    for data in raw_files:
        if data:
            all_entries.extend(flatten_json_entries(data))
    return all_entries

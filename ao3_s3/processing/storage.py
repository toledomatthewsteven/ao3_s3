import os, json, datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "datasets")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def save_dataset(username, dataset_type, timeframe, data):
    ensure_data_dir()
    filename = f"{username}_{dataset_type}_{timeframe}_{datetime.date.today()}.json"
    path = os.path.join(DATA_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename, path

def list_datasets():
    ensure_data_dir()
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

def load_dataset(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def delete_dataset(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

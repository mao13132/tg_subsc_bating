import json


def parse_id_users(text):
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass
    return []


def add_id_user(text, user_id):
    ids = parse_id_users(text)
    ids.append(str(user_id))
    seen = set()
    uniq = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return json.dumps(uniq, ensure_ascii=False)


def add_id_users(text, user_ids):
    ids = parse_id_users(text)
    for uid in user_ids or []:
        ids.append(str(uid))
    seen = set()
    uniq = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return json.dumps(uniq, ensure_ascii=False)
    
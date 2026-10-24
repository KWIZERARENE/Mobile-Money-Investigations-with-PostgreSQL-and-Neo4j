START = 1788213600   # 1 Sep 2026 00:00 CAT

def hour_window(d):
    s = START + (d - 1) * 86400 + 9 * 3600 + 45 * 60
    return s, s + 3600
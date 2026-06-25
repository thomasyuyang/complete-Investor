def kelly(win_rate: float, avg_win: float, avg_loss: float, frac: float = 0.25):
    p = win_rate / 100
    q = 1 - p
    w = avg_win / 100
    l = avg_loss / 100
    if w <= 0 or l <= 0:
        return 0, 0, 0
    b = w / l
    raw = max(0, (b * p - q) / b)
    conservative = raw * frac
    return b, raw, conservative

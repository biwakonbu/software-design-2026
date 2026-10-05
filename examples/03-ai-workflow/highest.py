# 第03回: for文と初期値を学ぶための自作例(標準ライブラリのみ)


def highest_draft(temps):
    # 教材用に自作した誤りの例。特定サービスの回答ではない
    best = 0
    for t in temps:
        if t > best:
            best = t
    return best


def highest(temps):
    # 空でない整数リストの最大値を返す。空リストは ValueError
    if not temps:
        raise ValueError('temps must not be empty')
    best = temps[0]
    for t in temps[1:]:
        if t > best:
            best = t
    return best

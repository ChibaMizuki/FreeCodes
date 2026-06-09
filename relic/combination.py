def nCr(n, r):
    if n < r or n < 0 or r < 0:
        return []
    combinations = []
    index = list(range(r)) # リスト内包表記より早いらしい
    combinations.append(index.copy())

    while True:
        for i in reversed(range(r)):
            if index[i] != i + n - r: # 最大値をとっていない箇所を後ろから見つける
                break
        else: # for-else文。forが正常終了時に処理
            return combinations

        index[i] += 1

        for j in range(i + 1, r): # i + 1 > r の時は何も行われない
            index[j] = index[j - 1] + 1

        print("append: ", index)
        combinations.append(index.copy())

n = 5
r = 5
if n >= r:
    comb = nCr(n, r)
    print(comb)
else:
    print("n < r")
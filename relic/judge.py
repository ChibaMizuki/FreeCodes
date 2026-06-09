def match(r, s, p, r_num, s_num, p_num):
    win = 0
    if r >= p_num:
        win += p_num
    elif r < p_num:
        win += r

    if p >= s_num:
        win += s_num
    elif p < s_num:
        win += p

    if s >= r_num:
        win += r_num
    elif s < r_num:
        win += s
    return win

n, m = input().split()
hand = input()

battle_num = int(n)
finger = int(m)
rock = 0
scissors = 0
paper = 0
win = 0
max_win = 0

for i in hand:
    if i == "G":
        rock += 1
    elif i == "C":
        scissors += 1
    elif i == "P":
        paper += 1
    else:
        continue

is_even = int((finger % 5) % 2)
if is_even == 0:
    paper_num = int(finger / 5) # 余りが偶数ならパーを最大回数出せる
else:
    paper_num = int(finger / 5 - 1) # 奇数なら偶数にするために-1回

scissors_num = int((finger - paper_num * 5) / 2)
rock_num = battle_num - paper_num - scissors_num

while(paper_num >= 0 and rock_num >= 0):
    win = match(rock, scissors, paper, rock_num, scissors_num, paper_num)
    if max_win < win:
        max_win = win

    # パーを-10本（-2回）, チョキを+10本（+5回）, 回数合わせでグーを-3回
    paper_num -= 2
    rock_num -= 3
    scissors_num += 5

print(max_win)

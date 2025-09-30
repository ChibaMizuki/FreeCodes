before = 25 # 割る前のアルコール濃度（％）
amount = 1000 # 割った後のお酒の量（ml）
after = 10 # 割った後のアルコール濃度（％）

# アルコールの素の量を計算
alcohol = amount * after / before
pure = alcohol * before / 100

print(f"{alcohol} ml")
print(f"{pure} ml")
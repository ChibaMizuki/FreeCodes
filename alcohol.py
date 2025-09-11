before = 25 # 割る前のアルコール濃度（％）
amount = 350 # 割った後のお酒の量（ml）
after = 10 # 割った後のアルコール濃度（％）

# アルコールの素の量を計算
alcohol = amount * after / before

print(alcohol)
n, m = list(map(int,input().split()))
jan = input()
g = 0 
p = 0 
#c = 0 
count = 0 

for i in jan:
     if i == "G": 
        g += 1 
     elif i == "P": 
        p += 1 
     elif i == "C": 
        #c += 1 
        count += 1 

while p >= 5 and g >= 2 and m >= 10:
     count += 5 
     p -= 5 
     m -= 10 

for _ in range(g): 
    if m >= 5: 
        count += 1 
        m -= 5 

for _ in range(p): 
    if m >= 2: 
        count += 1 
        m -= 2 

x = m // 5 
y = m % 5 
z = y / 2 

if m >= 5: 
    count -= x 
elif y >= 2: 
    count -= z 

print(count)

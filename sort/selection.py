def selection_sort(array):
    a = array
    n = len(a)
    for i in range(n - 1):
        minimum = a[i]

        for j in range(i, n):
            if minimum > a[j]:
                minimum = a[j]
        
        if i != a.index(minimum):
            yield i, a.index(minimum)

            a.remove(minimum)
            a.insert(i, minimum)

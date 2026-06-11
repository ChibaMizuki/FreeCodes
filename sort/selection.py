def selection_sort(array):
    a = array
    n = len(a)
    for i in range(n - 1):
        minimum = i

        for j in range(i + 1, n):
            if a[j] < a[minimum]:
                minimum = j
        
        if i != minimum:
            yield i, minimum
            a[i], a[minimum] = a[minimum], a[i]

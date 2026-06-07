import random

array = [i for i in range(1, 11)]
random.shuffle(array)
print(array)

def bubble_sort(array):
    n = len(array)

    for i in range(n):
        swapped = False

        for j in range(n - i - 1):
            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]
                swapped = True
                yield array

        if not swapped:
            break

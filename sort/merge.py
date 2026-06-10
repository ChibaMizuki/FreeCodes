base = []
history = []
merge_range = []

def merge_sort(a):
    if len(a) <= 1:
        return a
    
    array = a

    split = len(array) // 2

    left = merge_sort(array[:split])
    right = merge_sort(array[split:])

    merged_list = merge(left, right)
    index_history(left, right, merged_list)

    return merged_list

def merge(l, r):
    result = []
    i, j = 0, 0

    while(i < len(l)) and (j < len(r)):
        if l[i] <= r[j]:
            result.append(l[i])
            i += 1
        else:
            result.append(r[j])
            j += 1

    if i < len(l):
        result.extend(l[i:])
    if j < len(r):
        result.extend(r[j:])
    return result

def index_history(left, right, merged_list):
    start = base.index(left[0])
    end = start + len(left) + len(right)
    base[start:end] = merged_list

    history.append(base.copy())
    merge_range.append([start, end])

# main関数
def merged_history(array):
    global history
    global base
    base = array.copy()
    history = []
    _ = merge_sort(array)

    return history, merge_range

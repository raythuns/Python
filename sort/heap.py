
# def parent(x):
#     return (x - 1) >> 1


def left(x):
    return x << 1 | 1


def right(x):
    return (x << 1) + 2


def max_heapify(A, i, size):
    l = left(i)
    r = right(i)
    _max = i
    if l < size and A[i] < A[l]:
        _max = l
    if r < size and A[_max] < A[r]:
        _max = r
    if _max != i:
        t = A[_max]
        A[_max] = A[i]
        A[i] = t
        max_heapify(A, _max, size)


def max_heapify_loop(A, i, size):
    while True:
        l = left(i)
        r = right(i)
        _max = i
        if l < size and A[i] < A[l]:
            _max = l
        if r < size and A[_max] < A[r]:
            _max = r
        if _max != i:
            t = A[_max]
            A[_max] = A[i]
            A[i] = t
            i = _max
            continue
        break


def build_heap(A):
    for i in range(int((len(A)-1)/2), -1, -1):
        max_heapify(A, i, len(A))


def heap_sort(A):
    build_heap(A)
    for i in range(len(A)-1, 0, -1):
        t = A[i]
        A[i] = A[0]
        A[0] = t
        max_heapify(A, 0, i)

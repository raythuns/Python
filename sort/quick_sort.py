
def partition(A, b, e):
    x = A[e]
    i = b - 1
    for j in range(b, e):
        if A[j] <= x:
            i = i + 1
            t = A[i]
            A[i] = A[j]
            A[j] = t
    i = i + 1
    t = A[i]
    A[i] = A[e]
    A[e] = t
    return i


def quick_sort(A, b, e):
    if b < e:
        m = partition(A, b, e)
        quick_sort(A, b, m-1)
        quick_sort(A, m+1, e)

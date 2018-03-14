
def merge(A, b, e, m):
    B = []
    i, j = b, m + 1
    while i <= m and j <= e:
        if A[j] < A[i]:
            B.append(A[j])
            j = j + 1
        else:
            B.append(A[i])
            i = i + 1
    while i <= m:
        B.append(A[i])
        i = i + 1
    while j <= e:
        B.append(A[j])
        j = j + 1
    for i in range(0, e-b+1):
        A[i+b] = B[i]


def merge_sort(A, b, e):
    if b < e:
        m = int((b + e) / 2)
        b1, e1 = b, m
        b2, e2 = m + 1, e
        merge_sort(A, b1, e1)
        merge_sort(A, b2, e2)
        merge(A, b, e, m)


def merge_sort_loop(A, b, e):
    stack = []
    loop = True
    while loop:
        if b < e:
            m = int((b + e) / 2)
            stack.append((b, e, m))
            e = m
        else:
            while True:
                b, e, m = stack.pop()
                merge(A, b, e, m)
                if len(stack) != 0:
                    b1, e1, m1 = stack[-1]
                    if b != b1:
                        continue
                    else:
                        b, e = m1+1, e1
                else:
                    loop = False
                break

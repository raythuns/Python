
def insert_sort(A):
    count = 0
    for i in range(1, len(A)):
        for j in range(i, 0, -1):
            if A[j-1] > A[j]:
                count += 1
                t = A[j-1]
                A[j-1] = A[j]
                A[j] = t
            else:
                break
    return A, count

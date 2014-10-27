cdef extern from "stdlib.h":
    void qsort(void *array, size_t count, size_t size,
               int (*compare)(const void *, const void *))
    void *malloc(size_t size)
    void free(void *ptr)

def pyqsort(list x):
    cdef:
        int *array
        int i, N

    # Allocate the C array
    N = len(x)
    array = <int*>malloc(sizeof(int) * N)
    if array == NULL:
        raise MemoryError()

    # Fill the C Array with the Python integers.
    for i in range(N):
        array[i] = x[i]

    # qsort the array...
    qsort(<void*>array, <size_t>N, sizeof(int), int_compare)

    # Convert back into Python and free the C array.
    for i in range(N):
        x[i] = array[i]
    free(array)

cdef int int_compare(const void *a, const void *b):
    cdef int ia, ib
    ia = (<int*>a)[0]
    ib = (<int*>b)[0]
    return ia - ib

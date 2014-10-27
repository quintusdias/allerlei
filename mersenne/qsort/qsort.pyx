cdef extern from "stdlib.h":
    void qsort(void *array, size_t count, size_t size,
               int (*compare)(const void *, const void *))
    void *malloc(size_t size)
    void free(void *ptr)

ctypedef int (*qsort_cmp)(const void *, const void *)

def pyqsort(list x, cmp=None, reverse=False):
    global py_cmp

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

    cdef qsort_cmp cmp_callback

    if cmp and reverse:
        py_cmp = cmp
        cmp_callback = reverse_py_cmp_wrapper
    elif cmp and not reverse:
        py_cmp = cmp
        cmp_callback = py_cmp_wrapper
    elif reverse:
        cmp_callback = reverse_int_compare
    else:
        cmp_callback = int_compare

    # qsort the array...
    result = safe_qsort(<void*>array, <size_t>N, sizeof(int), cmp_callback)

    # Convert back into Python and free the C array.
    for i in range(N):
        x[i] = array[i]
    free(array)

cdef int int_compare(const void *a, const void *b):
    cdef int ia, ib
    ia = (<int*>a)[0]
    ib = (<int*>b)[0]
    return ia - ib

cdef int reverse_int_compare(const void *a, const void *b):
    return -int_compare(a, b)

cdef object py_cmp = None

cdef int py_cmp_wrapper(const void *a, const void *b):
    cdef int ia, ib
    ia = (<int*>a)[0]
    ib = (<int*>b)[0]
    try:
        result = py_cmp(ia, ib)
    except:
        result = -2
    return result

cdef int reverse_py_cmp_wrapper(const void *a, const void *b):
    return -py_cmp_wrapper(a, b)


cdef extern from "mt19937ar.h":
    void init_genrand(unsigned long s)
    double genrand_real1()

def init_state(unsigned long s):
    init_genrand(s)

def rand():
    return genrand_real1()

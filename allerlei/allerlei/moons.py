import math

import matplotlib.pyplot as plt
import numpy as np

class planet:
    def __init__(self, a, e, n):
        self.a = a
        self.e = e
        self.b = a * np.sqrt(1 - e**2)
        self.names = n

    def plot(self, color):

        t = np.linspace(0, 2*math.pi, 100)
    
        x = self.a * np.cos(t)
        y = self.b * np.sin(t)
    
        # adjust for the focus.
        x -= self.a*self.e
    
        fig = plt.gcf()
        ax = plt.gca()
        ax.axis('equal')

        h = plt.plot(x.T,y.T, color=color)
        plt.grid()
        plt.show()
        return h



a = np.array([.128, 0.129, 0.181, 0.221, 0.422, 0.671, 1.070,
    1.882]).reshape((8,1))
e = np.array([0.00002, 0.0015, 0.0032, 0.0175, 0.0041, 0.0094, 0.0011,
    0.0074]).reshape((8,1))
n = ['Metis', 'Adrastea', 'Amalthea', 'Thebe', 'Io', 'Europa', 'Ganymede',
       'Callisto']
jupiter = planet(a, e, n)

a = np.array([0.167, 0.185, 0.238, 0.294, 0.377, 0.527, 1.222, 1.481,
    3.560, 12.869]).reshape(10,1)
e = np.array([0.0068, 0.0202, 0.0047, 0.0001, 0.0022, 0.001, 0.0288, 0.123,
    0.028, 0.156]).reshape(10,1)
n = ['Janus', 'Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea', 'Titan',
     'Hyperion', 'Iapetus', 'Phoebe']
saturn = planet(a, e, n)

a = np.array([0.129, 0.191, 0.266, 0.435, 0.583]).reshape((5,1))
e = np.array([0.0013, 0.0012, 0.0039, 0.0011, 0.0014]).reshape((5,1))
n = ['Miranda', 'Ariel', 'Umbriel', 'Titania', 'Oberon']
uranus = planet(a, e, n)

a = np.array([0.117, 0.354, 5.513]).reshape((3,1))
e = np.array([0.0005, 0.0000, 0.7507]).reshape((3,1))
n = ['Puck', 'Triton', 'Nereid']
neptune = planet(a, e, n)

if __name__ == "__main__":
    run(a_j, e_j, n_j)

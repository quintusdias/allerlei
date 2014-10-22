import math
import pkg_resources
import sqlite3

import matplotlib.pyplot as plt
import numpy as np

class Moon(object):
    def __init__(self, name, semi_major_axis, eccentricity):
        self.name = name
        self.a = semi_major_axis
        self.e = eccentricity

    def plot(self, color):
        a = self.a
        e = self.e
        b = a * np.sqrt(1 - e**2)

        t = np.linspace(0, 2*math.pi, 100)
    
        x = a * np.cos(t)
        y = b * np.sin(t)

        # adjust for the focus.
        x -= a * e

        plt.plot(x, y, color=color)
    
class Planet(object):
    def __init__(self, name, moons):
        self.name = name
        self.moons = moons

    def plot(self, color='red'):
        for moon in self.moons:
            moon.plot(color=color)

def load():
    db = pkg_resources.resource_filename(__name__, "data/moons.db")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = """SELECT * FROM planets""";
    cursor.execute(sql)
    rows = cursor.fetchall()
    planets = []
    for row in rows:
        sql = """SELECT m.name, m.semi_major_axis, m.eccentricity
                 FROM moons m
                 INNER JOIN planets p on p.id = m.planet_id
                 WHERE p.id = {}"""
        sql = sql.format(row[0])
        cursor.execute(sql)
        moon_rows = cursor.fetchall()
        moons = []
        for moon_row in moon_rows:
            name, a, e = moon_row
            moon = Moon(name, a, e)
            moons.append(moon)

        name = rows[1]
        planet = Planet(name, moons)
        planets.append(planet)
    
    return planets


fig = plt.figure()
ax = plt.gca()
ax.axis('equal')
plt.grid()
plt.show()


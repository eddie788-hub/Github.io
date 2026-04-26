"""
Cosmic Explorer Pro — Python Backend
=====================================
Run:  python server.py
Then open your HTML frontend (served from the same origin or with CORS enabled).

Requires: pip install flask flask-cors
"""

from flask import Flask, jsonify
from flask_cors import CORS
import math
import time

app = Flask(__name__)
CORS(app)  # Allow requests from your HTML file / dev server

# ── Simulation state ────────────────────────────────────────────
START_TIME = time.time()

# ── Planet / object definitions ─────────────────────────────────
# distance    = semi-major axis in scene units  (1 unit ≈ 1 AU)
# eccentricity= real orbital eccentricity
# inclination = orbital inclination in degrees
# period      = orbital period in real Earth days
# speed       = scene speed multiplier (keeps inner planets visibly faster)

CELESTIAL_BODIES = [
    # ── Sun ─────────────────────────────────────────────────────
    {
        "name": "Sun",
        "isSun": True,
        "radius": 3.5,
        "color": "#FDB813",
        "distance": 0,
        "eccentricity": 0,
        "inclination": 0,
        "orbital_period_days": 0,
        "speed": 0,
        "type": "star",
        "temperature": "5,778 K (surface) / 15M K (core)",
        "discovery_year": "Ancient",
        "moons": 0,
        "atmosphere": "Hydrogen 73%, Helium 25%",
        "fact": "The Sun contains 99.86% of the total mass of the Solar System. Every second it fuses ~600 million tonnes of hydrogen into helium.",
        "fun_fact": "Light from the Sun takes 8 minutes 20 seconds to reach Earth — yet it spent ~100,000 years travelling from the core to the surface.",
    },
    # ── Terrestrial planets ──────────────────────────────────────
    {
        "name": "Mercury",
        "radius": 0.35,
        "color": "#b5b5b5",
        "distance": 5.8,
        "eccentricity": 0.2056,
        "inclination": 7.0,
        "orbital_period_days": 87.97,
        "speed": 1.2,
        "type": "planet",
        "temperature": "-180 °C to +430 °C",
        "discovery_year": "Ancient",
        "moons": 0,
        "atmosphere": "Virtually none (exosphere only)",
        "fact": "Mercury's highly elliptical orbit means it moves almost twice as fast at perihelion as at aphelion — a fact that puzzled astronomers for centuries.",
        "fun_fact": "Despite being closest to the Sun, Mercury is NOT the hottest planet — Venus is, thanks to its runaway greenhouse effect.",
    },
    {
        "name": "Venus",
        "radius": 0.55,
        "color": "#e8cda0",
        "distance": 10.8,
        "eccentricity": 0.0068,
        "inclination": 3.39,
        "orbital_period_days": 224.7,
        "speed": 0.9,
        "type": "planet",
        "temperature": "462 °C (average)",
        "discovery_year": "Ancient",
        "moons": 0,
        "atmosphere": "CO₂ 96.5%, N₂ 3.5%",
        "fact": "Venus rotates backwards (retrograde) and so slowly that a Venusian day (243 Earth days) is longer than its year (225 Earth days).",
        "fun_fact": "Surface pressure on Venus is 92× Earth's — equivalent to being 900 m underwater. Early Soviet Venera landers survived only ~2 hours.",
    },
    {
        "name": "Earth",
        "radius": 0.6,
        "color": "#4fc3f7",
        "distance": 15.0,
        "eccentricity": 0.0167,
        "inclination": 0.0,
        "orbital_period_days": 365.25,
        "speed": 0.75,
        "type": "planet",
        "temperature": "-88 °C to +58 °C",
        "discovery_year": "Ancient",
        "moons": 1,
        "atmosphere": "N₂ 78%, O₂ 21%",
        "fact": "Earth's axial tilt of 23.5° drives our seasons. The planet is actually closest to the Sun in January (perihelion) — not in summer.",
        "fun_fact": "Earth is the densest planet in the Solar System at 5.51 g/cm³, and the only body known to support life.",
    },
    {
        "name": "Mars",
        "radius": 0.45,
        "color": "#cf6743",
        "distance": 22.8,
        "eccentricity": 0.0934,
        "inclination": 1.85,
        "orbital_period_days": 686.97,
        "speed": 0.6,
        "type": "planet",
        "temperature": "-125 °C to +20 °C",
        "discovery_year": "Ancient",
        "moons": 2,
        "atmosphere": "CO₂ 95.3%, N₂ 2.7%",
        "fact": "Olympus Mons on Mars is the tallest volcano in the Solar System at ~22 km — nearly 3× the height of Mount Everest.",
        "fun_fact": "Mars has the largest dust storms in the Solar System — planet-wide storms that can last months and block virtually all sunlight.",
    },
    # ── Gas / Ice Giants ─────────────────────────────────────────
    {
        "name": "Jupiter",
        "radius": 1.5,
        "color": "#c88b3a",
        "distance": 52.0,
        "eccentricity": 0.0489,
        "inclination": 1.30,
        "orbital_period_days": 4332.59,
        "speed": 0.35,
        "type": "planet",
        "temperature": "-110 °C (cloud tops)",
        "discovery_year": "Ancient",
        "moons": 95,
        "atmosphere": "H₂ 90%, He 10%",
        "fact": "Jupiter's Great Red Spot is a storm larger than Earth that has raged for at least 350 years, though it has been shrinking in recent decades.",
        "fun_fact": "Jupiter acts as a cosmic vacuum cleaner — its gravity deflects many comets and asteroids, shielding the inner solar system.",
    },
    {
        "name": "Saturn",
        "radius": 1.3,
        "color": "#e4d191",
        "distance": 95.0,
        "eccentricity": 0.0565,
        "inclination": 2.49,
        "orbital_period_days": 10759.22,
        "speed": 0.25,
        "type": "planet",
        "temperature": "-140 °C (cloud tops)",
        "discovery_year": "Ancient",
        "moons": 146,
        "atmosphere": "H₂ 96.3%, He 3.3%",
        "fact": "Saturn's rings are mostly water ice particles ranging from tiny grains to chunks several metres across, spanning ~280,000 km but only ~10 m thick in places.",
        "fun_fact": "Saturn is the least dense planet — less dense than water (0.69 g/cm³). In a large enough ocean it would float.",
    },
    {
        "name": "Uranus",
        "radius": 0.95,
        "color": "#7de8e8",
        "distance": 191.8,
        "eccentricity": 0.0457,
        "inclination": 0.77,
        "orbital_period_days": 30688.5,
        "speed": 0.18,
        "type": "planet",
        "temperature": "-195 °C (min)",
        "discovery_year": "1781",
        "moons": 27,
        "atmosphere": "H₂ 83%, He 15%, CH₄ 2.3%",
        "fact": "Uranus rotates on its side with an axial tilt of 97.77° — likely the result of a massive collision early in the Solar System's history.",
        "fun_fact": "Uranus is the coldest planetary atmosphere in the Solar System, reaching -224 °C despite being closer to the Sun than Neptune.",
    },
    {
        "name": "Neptune",
        "radius": 0.9,
        "color": "#3f54ba",
        "distance": 301.0,
        "eccentricity": 0.0113,
        "inclination": 1.77,
        "orbital_period_days": 60182.0,
        "speed": 0.14,
        "type": "planet",
        "temperature": "-201 °C (average)",
        "discovery_year": "1846",
        "moons": 16,
        "atmosphere": "H₂ 80%, He 19%, CH₄ 1.5%",
        "fact": "Neptune was the first planet found through mathematical prediction rather than direct observation — Le Verrier calculated its position from Uranus's orbital anomalies.",
        "fun_fact": "Winds on Neptune reach 2,100 km/h — the fastest recorded in the Solar System, faster even than a supersonic jet.",
    },
    # ── Dwarf planets ────────────────────────────────────────────
    {
        "name": "Pluto",
        "radius": 0.28,
        "color": "#c4a882",
        "distance": 395.0,
        "eccentricity": 0.2488,
        "inclination": 17.14,
        "orbital_period_days": 90560.0,
        "speed": 0.10,
        "type": "dwarf",
        "temperature": "-225 °C (average)",
        "discovery_year": "1930",
        "moons": 5,
        "atmosphere": "N₂, CH₄, CO (thin)",
        "fact": "New Horizons revealed Pluto has a heart-shaped nitrogen ice plain (Tombaugh Regio) and mountains of water ice up to 3,500 m tall.",
        "fun_fact": "Pluto's largest moon Charon is so massive relative to Pluto that they orbit a common barycentre outside Pluto — making them a true double-dwarf system.",
    },
    {
        "name": "Eris",
        "radius": 0.27,
        "color": "#d0c8c0",
        "distance": 559.0,
        "eccentricity": 0.4338,
        "inclination": 44.04,
        "orbital_period_days": 204199.0,
        "speed": 0.07,
        "type": "dwarf",
        "temperature": "-243 °C",
        "discovery_year": "2005",
        "moons": 1,
        "atmosphere": "Possible thin N₂/CH₄",
        "fact": "Discovery of Eris (slightly smaller but more massive than Pluto) triggered the 2006 IAU debate that reclassified Pluto as a dwarf planet.",
        "fun_fact": "Eris is nicknamed 'Xena' after the TV warrior princess. Its moon Dysnomia was nicknamed 'Gabrielle' after Xena's sidekick.",
    },
    # ── Comets ───────────────────────────────────────────────────
    {
        "name": "Halley",
        "radius": 0.2,
        "color": "#aaeeff",
        "distance": 35.1,
        "eccentricity": 0.9671,
        "inclination": 162.26,   # retrograde
        "orbital_period_days": 27507.0,
        "speed": 0.55,
        "type": "comet",
        "temperature": "-70 °C (nucleus)",
        "discovery_year": "Ancient (predicted 1705 by Halley)",
        "moons": 0,
        "atmosphere": "Coma of H₂O, CO, CO₂",
        "fact": "Halley's Comet is the only short-period comet clearly visible to the naked eye from Earth, returning roughly every 75–76 years.",
        "fun_fact": "Mark Twain was born in 1835 (Halley apparition) and died in 1910 (next apparition) — he famously predicted this himself.",
    },
]

# ── Asteroid belt config ─────────────────────────────────────────
ASTEROID_BELT = {
    "inner_distance": 27.0,
    "outer_distance": 48.0,
    "count": 3000,
    "inclination_spread": 20,
    "color": "#8899aa",
    "opacity": 0.5,
    "size": 0.08,
}

KUIPER_BELT = {
    "inner_distance": 340.0,
    "outer_distance": 500.0,
    "count": 2000,
    "inclination_spread": 30,
    "color": "#556688",
    "opacity": 0.35,
    "size": 0.12,
}


# ── Kepler position solver ───────────────────────────────────────
def solve_kepler(M: float, e: float, tol: float = 1e-7) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E."""
    E = M if e < 0.8 else math.pi
    for _ in range(50):
        dE = (M - E + e * math.sin(E)) / (1.0 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E


def compute_position(body: dict, elapsed_days: float) -> tuple[float, float, float]:
    """Return (x, y, z) in scene units for a body at elapsed_days."""
    a   = body["distance"]        # semi-major axis (scene units)
    e   = body["eccentricity"]
    inc = math.radians(body["inclination"])
    T   = body["orbital_period_days"]
    spd = body["speed"]

    if a == 0 or T == 0:          # Sun stays at origin
        return 0.0, 0.0, 0.0

    b = a * math.sqrt(max(0.0, 1 - e * e))   # semi-minor axis

    # Mean anomaly — scale by speed multiplier for visual clarity
    M = (2 * math.pi * elapsed_days * spd / T) % (2 * math.pi)
    E = solve_kepler(M, e)

    x_orb = a * (math.cos(E) - e)
    z_orb = b * math.sin(E)

    # Apply inclination (tilt around x-axis)
    x = x_orb
    y = -z_orb * math.sin(inc)
    z =  z_orb * math.cos(inc)

    return float(x), float(y), float(z)


# ── Flask endpoint ───────────────────────────────────────────────
@app.route("/planets")
def get_planets():
    elapsed_seconds = time.time() - START_TIME
    # 1 real second = 1 simulated day by default (frontend speed slider multiplies on top)
    elapsed_days  = elapsed_seconds
    elapsed_years = elapsed_days / 365.25

    planets_out = []
    for body in CELESTIAL_BODIES:
        x, y, z = compute_position(body, elapsed_days)
        entry = {**body, "x": x, "y": y, "z": z}
        planets_out.append(entry)

    return jsonify({
        "elapsed_days":  round(elapsed_days, 2),
        "elapsed_years": round(elapsed_years, 4),
        "planets":       planets_out,
        "asteroid_belt": ASTEROID_BELT,
        "kuiper_belt":   KUIPER_BELT,
    })


# ── Dev server ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀  Cosmic Explorer Pro — Python backend")
    print("    http://localhost:5000/planets")
    print("    Ctrl-C to stop\n")
    app.run(host="0.0.0.0", port=5000, debug=True)

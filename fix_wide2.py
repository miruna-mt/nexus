path = r"C:\Users\Miruna\nexus\frontend\style.css"
with open(path, "r", encoding="utf-8-sig") as f:
    c = f.read()

# Borrar el bloque anterior (mal calibrado)
old = """

/* Pantallas grandes: aprovechar el ancho */
@media (min-width: 1600px) {
    .app-container {
        max-width: 1800px;
    }
}

@media (min-width: 2000px) {
    .app-container {
        max-width: 2200px;
        gap: 32px;
    }
}
"""

new = """

/* Pantallas grandes: aprovechar el ancho */
@media (min-width: 1400px) {
    .app-container {
        max-width: 1600px;
    }
}

@media (min-width: 1700px) {
    .app-container {
        max-width: 2000px;
        gap: 32px;
    }
}

@media (min-width: 2100px) {
    .app-container {
        max-width: 2400px;
        gap: 40px;
    }
}
"""

if old in c:
    c = c.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("OK: breakpoints recalibrados")
else:
    print("MISS: bloque anterior no encontrado")

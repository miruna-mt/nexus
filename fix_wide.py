path = r"C:\Users\Miruna\nexus\frontend\style.css"
with open(path, "r", encoding="utf-8-sig") as f:
    c = f.read()

addition = """

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

if "@media (min-width: 1600px)" not in c:
    with open(path, "a", encoding="utf-8") as f:
        f.write(addition)
    print("OK: media queries para pantallas grandes anadidas")
else:
    print("SKIP: ya existe")

import re

path = r"C:\Users\Miruna\nexus\frontend\style.css"
with open(path, "r", encoding="utf-8-sig") as f:
    c = f.read()

# Mapa: valor viejo -> token
mapping = {
    "0.65rem": "var(--text-xs)",
    "0.68rem": "var(--text-xs)",
    "0.75rem": "var(--text-xs)",
    "0.8rem":  "var(--text-sm)",
    "0.82rem": "var(--text-sm)",
    "0.85rem": "var(--text-sm)",
    "0.88rem": "var(--text-sm)",
    "0.9rem":  "var(--text-sm)",
    "0.92rem": "var(--text-sm)",
    "1.1rem":  "var(--text-lg)",
    "1.4rem":  "var(--text-xl)",
    "1.6rem":  "var(--text-2xl)",
}

count = 0
for old, new in mapping.items():
    pattern = re.compile(r"font-size:\s*" + re.escape(old) + r"\s*;")
    c, n = pattern.subn("font-size: " + new + ";", c)
    if n > 0:
        print("OK: " + old + " -> " + new + " (" + str(n) + " ocurrencias)")
        count += n

# Caso especial: hay un 0.85rem SIN punto y coma, al final de una regla en result-hero-label (ya no aplica)
# y el .result-hero-line usa 0.92rem.
# Tambien revisar si queda algun font-size con valor no mapeado
remaining = re.findall(r"font-size:\s*([\d.]+rem)", c)
if remaining:
    print("")
    print("AVISO: quedan tamanos sin mapear:")
    for r in sorted(set(remaining)):
        print("  - " + r)

print("")
print("Total: " + str(count) + " font-sizes tokenizados")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

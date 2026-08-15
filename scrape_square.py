import re, json, urllib.request, html as h

print("🔍 Début du scraping de squareportsaid.com...")

try:
    req = urllib.request.Request(
        "https://squareportsaid.com/",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    print(f"✅ Page téléchargée ({len(raw)} octets)")
except Exception as e:
    print(f"❌ Erreur de téléchargement: {e}")
    json.dump({"date": "erreur", "rates": {}, "source": "squareportsaid.com"},
              open("square.json", "w"), ensure_ascii=False, indent=1)
    exit(0)

t = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S)
t = re.sub(r"<[^>]+>", "\n", t)
t = h.unescape(t)
L = [x.strip() for x in t.splitlines() if x.strip()]

print(f"📄 {len(L)} lignes de texte extraites")

codes = ["EUR", "USD", "GBP", "CAD", "CHF"]
out = {}

for i, l in enumerate(L):
    if any(l.startswith(c + " /") or l == c for c in codes):
        code = l.split(" /")[0].strip()
        if code in out:
            continue
        a = v = None
        for j in range(i + 1, min(i + 15, len(L))):
            if L[j] == "Achat" and j + 1 < len(L):
                m = re.match(r"^([\d.,]+)$", L[j + 1])
                if m:
                    a = float(m.group(1).replace(",", "."))
            if L[j] == "Vente" and j + 1 < len(L):
                m = re.match(r"^([\d.,]+)$", L[j + 1])
                if m:
                    v = float(m.group(1).replace(",", "."))
            m = re.match(r"^([\d.,]+)\s+Achat$", L[j])
            if m:
                a = float(m.group(1).replace(",", "."))
            m = re.match(r"^([\d.,]+)\s+Vente$", L[j])
            if m:
                v = float(m.group(1).replace(",", "."))
            if a and v:
                break
        if a and v:
            out[code] = {"achat": a, "vente": v}
            print(f"  ✅ {code}: achat={a}, vente={v}")

date = ""
m = re.search(r"Dernière mise à jour\s*:\s*([^<\n]+)", t)
if m:
    date = m.group(1).strip()

print(f"📊 {len(out)} devises trouvées sur 5 attendues")

if len(out) >= 1:
    json.dump({"date": date, "rates": out, "source": "squareportsaid.com"},
              open("square.json", "w"), ensure_ascii=False, indent=1)
    print("💾 square.json sauvegardé")
else:
    print("❌ Aucune devise trouvée")
    exit(1)

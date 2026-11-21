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
    with open("square.json", "w", encoding="utf-8") as f:
        json.dump({"date": "erreur", "rates": {}, "source": "squareportsaid.com"}, f, ensure_ascii=False, indent=1)
    exit(0)

t = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S)
t = re.sub(r"<[^>]+>", "\n", t)
t = h.unescape(t)

L = [
    re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', x)
      .replace('\xa0', ' ')
      .strip()
    for x in t.splitlines() if x.strip()
]

print(f"📄 {len(L)} lignes de texte extraites")

codes = ["EUR", "USD", "GBP", "CAD", "CHF", "CNY", "SAR", "AED", "TRY", "TND", "MAD"]
out = {}

def parse_num(s):
    s = s.replace(",", ".").strip()
    m = re.match(r"^([\d.]+)$", s)
    return float(m.group(1)) if m else None

for i, l in enumerate(L):
    found_code = None
    for c in codes:
        if c in l and len(l) < 30:
            found_code = c
            break

    if found_code and found_code not in out:
        a = v = None
        for j in range(i + 1, min(i + 20, len(L))):
            line = L[j].strip()

            # Format A : prix PUIS mot sur la MÊME ligne ("273.00 Achat")
            m1 = re.match(r"^([\d.,]+)\s*(?:Achat|Buy)\b", line, re.IGNORECASE)
            if m1: a = parse_num(m1.group(1))
            m2 = re.match(r"^([\d.,]+)\s*(?:Vente|Sell)\b", line, re.IGNORECASE)
            if m2: v = parse_num(m2.group(1))

            # Format B : mot SEUL, prix à la ligne PRÉCÉDENTE (le fix !)
            if re.match(r"^(?:Achat|Buy)$", line, re.IGNORECASE):
                if j - 1 >= 0:
                    a = parse_num(L[j-1])
            if re.match(r"^(?:Vente|Sell)$", line, re.IGNORECASE):
                if j - 1 >= 0:
                    v = parse_num(L[j-1])

            # Format C : mot SEUL, prix à la ligne SUIVANTE (ancien format, gardé)
            if re.match(r"^(?:Achat|Buy)$", line, re.IGNORECASE) and j + 1 < len(L):
                if a is None: a = parse_num(L[j+1])
            if re.match(r"^(?:Vente|Sell)$", line, re.IGNORECASE) and j + 1 < len(L):
                if v is None: v = parse_num(L[j+1])

            if a is not None and v is not None:
                break

        if a is not None and v is not None:
            out[found_code] = {"achat": a, "vente": v}
            print(f"  ✅ {found_code}: achat={a}, vente={v}")
        else:
            print(f"  ⚠️ {found_code} trouvé mais prix manquants (ligne {i})")

date = ""
m = re.search(r"Dernière mise à jour\s*[:\-]?\s*([^\n<]+)", t, re.IGNORECASE)
if m:
    date = m.group(1).strip()

print(f"\n📊 {len(out)} devises trouvées sur {len(codes)} attendues")

if len(out) >= 1:
    with open("square.json", "w", encoding="utf-8") as f:
        json.dump({"date": date, "rates": out, "source": "squareportsaid.com"}, f, ensure_ascii=False, indent=1)
    print("💾 square.json sauvegardé avec succès !")
else:
    print("❌ Aucune devise trouvée.")
    exit(1)

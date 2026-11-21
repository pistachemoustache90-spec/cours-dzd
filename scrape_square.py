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

print(f"📄 {len(L)} lignes extraites")

codes = ["EUR", "USD", "GBP", "CAD", "CHF", "CNY", "SAR", "AED", "TRY", "TND", "MAD"]
out = {}

# Nouvelle approche : pour chaque code, on cherche les 2 prochains nombres dans les 15 lignes suivantes
for i, l in enumerate(L):
    found_code = None
    for c in codes:
        if c in l and len(l) < 30:
            found_code = c
            break
    
    if found_code and found_code not in out:
        # Chercher les 2 prochains nombres après ce code
        prices = []
        for j in range(i + 1, min(i + 15, len(L))):
            line = L[j].strip()
            # Extraire tous les nombres de cette ligne
            numbers = re.findall(r'[\d]+[.,][\d]+', line)
            for num in numbers:
                prices.append(float(num.replace(",", ".")))
            if len(prices) >= 2:
                break
        
        if len(prices) >= 2:
            out[found_code] = {"achat": prices[0], "vente": prices[1]}
            print(f"  ✅ {found_code}: {prices[0]} / {prices[1]}")
        else:
            print(f"  ⚠️ {found_code}: seulement {len(prices)} prix trouvé(s)")

date = ""
m = re.search(r"Dernière mise à jour\s*[:\-]?\s*([^\n<]+)", t, re.IGNORECASE)
if m:
    date = m.group(1).strip()

print(f"\n📊 {len(out)} devises sur {len(codes)}")

if len(out) >= 1:
    with open("square.json", "w", encoding="utf-8") as f:
        json.dump({"date": date, "rates": out, "source": "squareportsaid.com"}, f, ensure_ascii=False, indent=1)
    print("💾 square.json sauvegardé !")
else:
    print("❌ Aucune devise trouvée")
    exit(1)

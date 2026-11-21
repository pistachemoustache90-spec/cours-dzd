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
        
        # Chercher le pattern : nombre → Achat → nombre → Vente dans les 20 lignes suivantes
        for j in range(i + 1, min(i + 20, len(L))):
            line = L[j].strip()
            
            # Pattern 1 : "273.00 Achat" ou "273.00Achat"
            m = re.match(r"^([\d.,]+)\s*(?:Achat|Buy)", line, re.IGNORECASE)
            if m and a is None:
                a = parse_num(m.group(1))
            
            # Pattern 2 : "275.50 Vente" ou "275.50Vente"
            m = re.match(r"^([\d.,]+)\s*(?:Vente|Sell)", line, re.IGNORECASE)
            if m and v is None:
                v = parse_num(m.group(1))
            
            # Pattern 3 : "Achat" seul, le nombre est à la ligne PRÉCÉDENTE
            if re.match(r"^(?:Achat|Buy)$", line, re.IGNORECASE) and a is None:
                if j - 1 >= i:
                    a = parse_num(L[j-1])
            
            # Pattern 4 : "Vente" seul, le nombre est à la ligne PRÉCÉDENTE
            if re.match(r"^(?:Vente|Sell)$", line, re.IGNORECASE) and v is None:
                if j - 1 >= i:
                    v = parse_num(L[j-1])
            
            if a is not None and v is not None:
                break
        
        if a is not None and v is not None:
            out[found_code] = {"achat": a, "vente": v}
            print(f"  ✅ {found_code}: {a} / {v}")
        else:
            print(f"  ⚠️ {found_code}: a={a}, v={v}")

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

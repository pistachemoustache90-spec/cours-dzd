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

# Nettoyage avancé du HTML
t = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S)
t = re.sub(r"<[^>]+>", "\n", t)
t = h.unescape(t)

# ✅ CORRECTION ICI : On supprime uniquement les emojis et on remplace les espaces insécables
L = [
    re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', x)
      .replace('\xa0', ' ')
      .strip() 
    for x in t.splitlines() if x.strip()
]

print(f"📄 {len(L)} lignes de texte extraites")

codes = ["EUR", "USD", "GBP", "CAD", "CHF", "CNY", "SAR", "AED", "TRY", "TND", "MAD"]
out = {}

for i, l in enumerate(L):
    # Cherche si un code devise est présent dans la ligne
    found_code = None
    for c in codes:
        if c in l and len(l) < 30:
            found_code = c
            break
            
    if found_code and found_code not in out:
        
        # 🔍 SECTION DEBUG AJOUTÉE ICI
        print(f"\n🔍 DEBUG {found_code} à la ligne {i}:")
        for k in range(max(0, i-2), min(len(L), i+30)):
            print(f"  L{k}: [{L[k]}]")
        # FIN SECTION DEBUG
        
        a = v = None
        # Recherche flexible des prix dans les 25 lignes suivantes
        for j in range(i + 1, min(i + 25, len(L))):
            line = L[j].replace(",", ".").strip()
            
            # Format 1 : "273.00 Achat" ou "273.00 Buy"
            m_achat = re.match(r"^([\d.]+)\s*(?:Achat|Buy)", line, re.IGNORECASE)
            if m_achat: 
                a = float(m_achat.group(1))
            
            # Format 2 : "275.50 Vente" ou "275.50 Sell"
            m_vente = re.match(r"^([\d.]+)\s*(?:Vente|Sell)", line, re.IGNORECASE)
            if m_vente: 
                v = float(m_vente.group(1))
            
            # Format 3 : Mot "Achat" seul, prix à la ligne suivante
            if re.match(r"^(?:Achat|Buy)$", line, re.IGNORECASE) and j + 1 < len(L):
                try: 
                    a = float(L[j+1].replace(",", ".").strip())
                except: 
                    pass
                
            # Format 4 : Mot "Vente" seul, prix à la ligne suivante
            if re.match(r"^(?:Vente|Sell)$", line, re.IGNORECASE) and j + 1 < len(L):
                try: 
                    v = float(L[j+1].replace(",", ".").strip())
                except: 
                    pass

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
    print("❌ Aucune devise trouvée. Vérifiez la structure du site.")

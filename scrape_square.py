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

# Nettoyage avancé du HTML
t = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S)
t = re.sub(r"<[^>]+>", "\n", t)
t = h.unescape(t)
# On garde uniquement les lignes qui contiennent du texte utile
L = [re.sub(r'[^\x00-\x7F]+', '', x).strip() for x in t.splitlines() if x.strip()]

print(f"📄 {len(L)} lignes de texte extraites")

codes = ["EUR", "USD", "GBP", "CAD", "CHF", "CNY", "SAR", "AED", "TRY", "TND", "MAD"]
out = {}

for i, l in enumerate(L):
    # ✅ NOUVELLE LOGIQUE : Cherche si le code est présent n'importe où dans la ligne
    # Cela gère "EUR /", "EUR-", "EUR.", " EUR " etc.
    found_code = None
    for c in codes:
        if c in l and len(l) < 20: # On limite la longueur pour éviter les faux positifs dans les phrases
            found_code = c
            break
            
    if found_code and found_code not in out:
        a = v = None
        # On cherche les prix dans les 20 lignes suivantes (au lieu de 15)
        for j in range(i + 1, min(i + 20, len(L))):
            line = L[j].replace(",", ".")
            
            # Format 1 : "273.00 Achat"
            m_achat = re.match(r"^([\d.]+)\s*(?:Achat|Buy)", line, re.IGNORECASE)
            if m_achat: a = float(m_achat.group(1))
            
            # Format 2 : "275.50 Vente"
            m_vente = re.match(r"^([\d.]+)\s*(?:Vente|Sell)", line, re.IGNORECASE)
            if m_vente: v = float(m_vente.group(1))
            
            # Format 3 : Ligne "Achat" suivie du prix à la ligne d'après
            if re.match(r"^(?:Achat|Buy)$", line, re.IGNORECASE) and j + 1 < len(L):
                try: a = float(L[j+1].replace(",", "."))
                except: pass
                
            # Format 4 : Ligne "Vente" suivie du prix à la ligne d'après
            if re.match(r"^(?:Vente|Sell)$", line, re.IGNORECASE) and j + 1 < len(L):
                try: v = float(L[j+1].replace(",", "."))
                except: pass

            if a is not None and v is not None:
                break
                
        if a is not None and v is not None:
            out[found_code] = {"achat": a, "vente": v}
            print(f"  ✅ {found_code}: achat={a}, vente={v}")
        else:
            print(f"  ⚠️ {found_code} trouvé mais prix manquants (L{i})")

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

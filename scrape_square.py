# Remplacez TOUTE votre boucle for i, l in enumerate(L): ... par ceci :

for i, line in enumerate(L):
    # Nettoyage agressif : supprime espaces insécables, tabulations, etc.
    clean_line = re.sub(r'[\xa0\t]+', ' ', line).strip()
    
    # Cherche si un code devise est présent dans cette ligne courte
    found_code = None
    for c in codes:
        if c in clean_line and len(clean_line) < 40:
            found_code = c
            break
    
    if not found_code or found_code in out:
        continue
        
    # Recherche flexible des prix dans les 25 lignes suivantes
    a = v = None
    for j in range(i + 1, min(i + 25, len(L))):
        current = L[j].replace(",", ".").strip()
        
        # Format A : "273.00 Achat" ou "273.00 Buy"
        m = re.match(r'^([\d.]+)\s*(?:Achat|Buy|achat)', current, re.IGNORECASE)
        if m: 
            a = float(m.group(1))
            
        # Format B : "275.50 Vente" ou "275.50 Sell"  
        m = re.match(r'^([\d.]+)\s*(?:Vente|Sell|vente)', current, re.IGNORECASE)
        if m: 
            v = float(m.group(1))
            
        # Format C : Mot "Achat" seul, prix à la ligne suivante
        if re.match(r'^(?:Achat|Buy)$', current, re.IGNORECASE) and j+1 < len(L):
            try: a = float(L[j+1].replace(",", ".").strip())
            except: pass
            
        # Format D : Mot "Vente" seul, prix à la ligne suivante  
        if re.match(r'^(?:Vente|Sell)$', current, re.IGNORECASE) and j+1 < len(L):
            try: v = float(L[j+1].replace(",", ".").strip())
            except: pass
            
        if a is not None and v is not None:
            break
    
    if a is not None and v is not None:
        out[found_code] = {"achat": a, "vente": v}
        print(f"  ✅ {found_code}: {a} / {v}")
    else:
        print(f"  ⚠️ {found_code} trouvé mais prix non capturés (ligne {i})")

from pathlib import Path
p = Path('scripts/bilan_extracted.txt')
if not p.exists():
    print('Fichier source manquant:', p)
    raise SystemExit(1)
text = p.read_text(encoding='utf-8', errors='replace')
# Mapping des séquences courantes rencontrées après extraction
repl = {
    'P�riode': 'Période',
    'p�riode': 'période',
    'b�n�fice': 'bénéfice',
    'B�n�fice': 'Bénéfice',
    'Soci�t�': 'Société',
    'Qt�': 'Qté',
    'Revenu': 'Revenu',
    'Total b�n�fice': 'Total bénéfice',
}
# Also handle Unicode replacement char U+FFFD
text = text.replace('\ufffd', 'é')
for k, v in repl.items():
    text = text.replace(k, v)
out = Path('scripts/bilan_extracted_clean.txt')
out.write_text(text, encoding='utf-8')
print('WROTE', out, 'SIZE', out.stat().st_size)
print('\nSAMPLE:\n')
print(text[:1000])

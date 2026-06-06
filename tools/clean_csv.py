import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

CSV = Path(__file__).parents[1] / "dados_extraidos.csv"
BACKUP = CSV.with_suffix('.csv.bak')

def is_valid_name(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    if len(s) < 3:
        return False
    # reject tokens containing 'pix' or too many non-letters
    if re.search(r"pix|comprovante|transfer|valor|R\$", s, re.IGNORECASE):
        return False
    words = [w for w in re.split(r"\s+", s) if w]
    if len(words) < 2:
        return False
    if any(len(re.sub(r"[^A-Za-zÀ-ÿ]", "", w)) < 2 for w in words):
        return False
    return True


def clean():
    # backup: if original exists, copy to .bak; if original missing but .bak exists, use it as source
    if CSV.exists():
        BACKUP.write_text(CSV.read_text(encoding='utf-8'), encoding='utf-8')
        source = BACKUP
    elif BACKUP.exists():
        print('Arquivo original não encontrado; usando backup existente para limpeza.')
        source = BACKUP
    else:
        print('Nenhum CSV encontrado para limpar.')
        return

    rows = []
    with source.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        print('CSV vazio')
        return

    header = rows[0][:4]
    data = rows[1:]

    # normalize rows: keep first, second, third, last columns
    normalized = []
    for r in data:
        if len(r) >= 4:
            norm = [r[0].strip(), r[1].strip(), r[2].strip(), r[-1].strip()]
        else:
            # pad with empty values
            rr = r + [''] * (4 - len(r))
            norm = [rr[0].strip(), rr[1].strip(), rr[2].strip(), rr[3].strip()]
        normalized.append(norm)

    # build mapping of (banco,hora) -> most common valid recebedor
    mapping = defaultdict(Counter)
    for b,h,name,val in normalized:
        if is_valid_name(name):
            mapping[(b,h)][name] += 1

    most_common = {k: (c.most_common(1)[0][0] if c else None) for k,c in mapping.items()}

    # Replace invalid names with mapping if available
    cleaned = []
    for b,h,name,val in normalized:
        if not is_valid_name(name):
            key = (b,h)
            candidate = most_common.get(key)
            if candidate:
                name = candidate
        cleaned.append([b,h,name,val])

    # write back
    with CSV.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['banco','hora','recebedor','valor'])
        for r in cleaned:
            writer.writerow(r)

    print('CSV limpo. Backup em', BACKUP)

if __name__ == '__main__':
    clean()

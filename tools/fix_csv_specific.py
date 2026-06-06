import csv, shutil
path='dados_extraidos.csv'
shutil.copy(path, path + '.bak')
rows=[]
with open(path, 'r', newline='', encoding='utf-8') as f:
    r=csv.reader(f)
    for row in r:
        rows.append(row)
changed=0
for i,row in enumerate(rows):
    if len(row) >= 4:
        banco=row[0].strip().lower()
        hora=row[1].strip()
        nome=row[2]
        valor=row[3].strip().replace('"','')
        valor_norm=valor.replace(',','.')
        if banco=='bradesco' and hora=='22:16' and 'éncia' in nome.lower() and (valor_norm.startswith('50') or valor_norm=='50.00' or valor_norm=='50'):
            rows[i][2]='Daniely lopes clemente'
            changed+=1
with open(path, 'w', newline='', encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerows(rows)
print('Replaced', changed, 'rows. Backup saved to', path + '.bak')

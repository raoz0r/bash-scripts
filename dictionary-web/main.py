import funcoes
import library


wordd = funcoes.search('Cachorro')
with open('data.json', 'w') as data:
    library.json.dump(wordd, data, indent=2)

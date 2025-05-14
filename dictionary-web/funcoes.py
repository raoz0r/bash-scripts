import library

def search(datas):
    datas = library.urllib.parse.quote(datas)
    data = library.urllib.request.urlopen('http://dicionario-aberto.net/search-json/' + datas)
    data_json = library.json.load(data)
    return(data_json)


def imprimir(datai):
    datalen = len(datai['entry']['sense'])
    print(f"{datai['entry']['form']['orth']}")
    for x in range(0, datalen):
        if 'gramGrp' in datai['entry']['sense'][x].keys():
            print(datai['entry']['sense'][x]['gramGrp'])
        if 'usg' in datai['entry']['sense'][x].keys():
            print(datai['entry']['sense'][x]['usg']['#text'])
        datadef = datai['entry']['sense'][x]['def']
        print(datadef.replace('<br/>', '\n'))
    repetir()


def repetir():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    a = str(input('Deseja procurar mais palavras? [S/N] ')).lower()
    if a == 's' or a == 'sim':
        intro()
    elif a == 'n' or a == 'não':
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Obrigado por usar o dicionário r.Aorelio')
        print('              Volte Sempre              ')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    else:
        print('opção invalida\n')
        repetir()


def intro():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('~~~~Dicionário da Lingua Portuguesa~~~~')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    word_i = str(input(('~~~~~ Qual palavra deseja buscar? ~~~~~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~~~~~ ')))
    search(word_i)
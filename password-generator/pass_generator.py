import smtplib
import string
import config
from random import *
from time import sleep
from email.mime.text import MIMEText

#Função para enviar o e-mail. Para definir qual e-mail será enviado editar config.py
def send_email(msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Successo! Email enviado!")
    except:
        print("O Envio do Email falhou.")
#Função 1 para gerar senhas com Letras, Números e Símbolos
def pass_gen1(x = 8, y = 16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(choice(characters)for x in range(randint(x,y)))
    return password
#Função 2 para gerar senhas apenas com Letras e Números
def pass_gen2(x = 8, y = 16):
    characters = string.ascii_letters + string.digits
    password2 = ''.join(choice(characters)for x in range(randint(x,y)))
    return password2
#Função 3 para gerar senhas com Letras apenas.
def pass_gen3(x = 8, y = 16):
    characters = string.ascii_letters
    password3 = ''.join(choice(characters)for x in range(randint(x,y)))
    return password3

while True:
    SUBJECT = str(input('Para qual lugar deseja gerar a senha? '))
    user = str(input('Qual usuário? '))
    print('''[ 1 ] Caracteres/Números/Símbolos
[ 2 ] Caracters/Números
[ 3 ] Caracters''')
    option = int(input('Qual opção deseja? '))
    try:
        x, y = [int(x) for x in input('Escolha o número min/max: ').split()]
        if option == 1:
            pw = pass_gen1(x, y)
        elif option == 2:
            pw = pass_gen2(x, y)
        elif option == 3:
            pw = pass_gen3(x, y)
        else:
            print('Opção inválida.')
    except ValueError: #Será que preciso repetir toda a função aqui denovo? Ou tem uma forma mais limpa de fazer isso?
        x, y = None, None
        if option == 1:
            pw = pass_gen1()
        elif option == 2:
            pw = pass_gen2()
        elif option == 3:
            pw = pass_gen3()
        else:
            print('Opção inválida.')
    print(f'\033[1mUsuário:\033[m {user}\n\033[1mSenha:\033[m {pw}') #print usuário e senha para poder conferir

    #Declarando as variaveis para o MIMEText Enviar o e-mail.
    msg = (f'Usuário: {user} Senha:{pw}')
    TO = config.EMAIL_ADDRESS
    FROM = config.EMAIL_ADDRESS

    msg = MIMEText(msg)
    msg['Subject'] = SUBJECT
    msg['To'] = TO
    msg['From'] = FROM

    print('Enviando...')
    sleep(1)
    send_email(msg)
    c = str(input('Gerar outra senha? [S/N] ')).lower().strip()[0]
    if c == 'n':
        break
print('Programa encerrado.')

from ChatClient import ChatClient
from utilities import *
import getpass
import logging
import asyncio

# logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

def starter():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    option = 0
    while option != "3":
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Cerrar")
        option = input("Ingrese una opción: ")
        client = None
        if option == '1':
            print("Iniciando sesión con una cuenta registrada")
            jid = input("Ingrese su JID: ")
            password = getpass.getpass("Ingrese su contraseña: ")
            client = ChatClient(jid, password)
            client.connect(disable_starttls=True)
            client.process(forever=False)
        elif option == '2':
            print("Registrando una nueva cuenta")
            jid = input("Ingrese su JID: ")
            password = input("Ingrese su contraseña: ")
            #password = getpass.getpass("Ingrese su contraseña: ")
            online = register(jid, password)
            if online:
                print("Registro exitoso")
            else:
                print("No se pudo registrar la cuenta")
        elif option == '3':
            print("Cerrando aplicación")    
        else:
            print("Opción inválida")

starter()


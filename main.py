from ChatClient import ChatClient
from utilities import *
import getpass
# import logging
import asyncio


def starter():
    # logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    option = 0
    while option != "3":
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Cerrar")
        option = input("Ingrese una opción: ")
        client = None
        if option == '1':
            print("\nIniciando sesión con una cuenta registrada\n")
            jid = input("Ingrese su JID: ")
            jid = jid + "@alumchat.xyz"
            password = getpass.getpass("Ingrese su contraseña: ")
            client = ChatClient(jid, password)
            client.connect(disable_starttls=True)
            client.process(forever=False)
        elif option == '2':
            print("\nRegistrando una nueva cuenta\n")
            jid = input("Ingrese su JID: ")
            jid = jid + "@alumchat.xyz"
            password = input("Ingrese su contraseña: ")
            #password = getpass.getpass("Ingrese su contraseña: ")
            registered = register(jid, password)
            if registered:
                print("\nRegistro exitoso\n")
            else:
                print("\nNo se pudo registrar la cuenta\n")
        elif option == '3':
            print("\nCerrando aplicación\n")    
        else:
            print("\nOpción inválida\n")

starter()


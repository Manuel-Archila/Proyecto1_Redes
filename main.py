from ChatClient import ChatClient
from utilities import *
import getpass

openchat = True
while openchat == True:
    print("1. Iniciar sesión")
    print("2. Registrarse")
    print("3. Salir")
    option = input("Elige una opción: ")
    if option == "1" or option == "2":
        print("Dentro del chat")
    else:
        openchat = False
        print("Saliendo del chat")
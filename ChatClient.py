import slixmpp
import logging
from slixmpp.exceptions import IqError, IqTimeout
from utilities import *
import asyncio
from aioconsole import ainput
from aioconsole.stream import aprint

class ChatClient(slixmpp.ClientXMPP):

    def __init__(self, jid, password, ):
        super().__init__(jid, password)
        self.connected = False
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("connection_failed", self.connection_failed)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.disconnected)
        self.add_event_handler("failed_auth", self.failed_auth)

    async def start(self, event):
        try:
            self.send_presence()
            await self.get_roster()
            self.connected = True
            print('Conexion establecida')
            asyncio.create_task(self.main_menu())
        except IqError as err:
            self.connected = False
            print(f"Error: {err.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            self.connected = False
            print('Error: Server is taking too long to respond')
            self.disconnect()
        
    
    def failed_auth(self, event):
        logging.error("Authentication failed.")

    def connection_failed(self, event):
        logging.error("Connection failed.")
    
    def disconnected(self, event):
        logging.error("Disconnected.")

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("----------------------------------------------------")
            print("Mensaje de:", msg['from'])
            print("Asunto:", msg['subject'] if 'subject' in msg else "N/A")
            print("Mensaje:", msg['body'] if 'body' in msg else "N/A")
            print("----------------------------------------------------")
    
    async def main_menu(self):
        while self.connected == True:
            menu()
            option = await ainput("Ingrese una opción: ")

            if option == "1":
                print("Todos los usuarios conectados:")
            
            elif option == "2":
                print("Agregar a un usuario")
            
            elif option == "3":
                print("Mostrar detalles de un contacto")
            
            elif option == "4":
                print("Enviar mensaje a un usuario")
            
            elif option == "5":
                print("Enviar un mensaje grupal")

            elif option == "6":
                print("Definir mensaje de presencia")

            elif option == "7":
                print("Enviar un archivo")

            elif option == "8":
                print("Cerrando sesión")
                self.disconnect()
                self.connected = False

            else:
                print("Opción inválida")
            
            await asyncio.sleep(0.3)

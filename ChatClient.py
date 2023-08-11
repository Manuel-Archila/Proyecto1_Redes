import slixmpp
import logging
from slixmpp.exceptions import IqError, IqTimeout
from utilities import *
import asyncio
from aioconsole import ainput
from aioconsole.stream import aprint

class ChatClient(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.connected = False
        self.user = jid.split("@")[0]
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):
        try:
            self.send_presence()
            await self.get_roster()
            self.connected = True
            print("\nConexion establecida\n")
            asyncio.create_task(self.main_menu())
        except IqError as err:
            self.connected = False
            print(f"Error: {err.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            self.connected = False
            print('Error: El servidor no respondio a tiempo')
            self.disconnect()
        
    async def get_contacts(self):
        contacts = []
        for jid in self.client_roster.keys():
            presence = self.client_roster.presence(jid)
            status = "Desconectado"
            status_message = ""
            if jid != self.user:
                for _, pres in presence.items():
                    if pres:
                        status = pres['show']
                    if pres['status']:
                        status_message = pres['status']

                    if status == 'dnd':
                        status = 'Ocupado'
                    elif status == 'xa':
                        status = 'No disponible'
                    elif status == 'away':
                        status = 'Ausente'
                    else:
                        status = 'Disponible'
                    
                    contacts.append((jid, status, status_message))
        return contacts

    async def add_user(self, jid):
        try:
            self.send_presence_subscription(pto=jid)
            print("Solicitud de amistad enviada")
            await self.get_roster()
        except IqError as err:
            print(f"Error: {err.iq['error']['text']}")
        except IqTimeout:
            print('Error: El servidor no respondio a tiempo')

    async def get_user_info(self, jid):
        contacts = []
        if jid in self.client_roster.keys():
            presence = self.client_roster.presence(jid)
            status = "Desconectado"
            status_message = ""
            for _, pres in presence.items():
                if pres:
                    status = pres['show']
                if pres['status']:
                    status_message = pres['status']
                
                if status == 'dnd':
                    status = 'Ocupado'
                elif status == 'xa':
                    status = 'No disponible'
                elif status == 'away':
                    status = 'Ausente'
                else:
                    status = 'Disponible'
                
                contacts.append((jid, status, status_message))
                #FORMATEAR PARA LOS DIFERENTES ENCODINGS
          
        return contacts

    async def send_individual_message(self, jid):
        in_ = True

        while in_:
            msg = await ainput("Ingrese el mensaje que desea enviar: ")
            if msg == "out":
                in_ = False
            else:
                self.send_message(mto=jid, mbody=msg, mtype='chat')
                print("Mensaje enviado")
    
    async def send_group_message(self, jid):
        pass

    async def send_new_presence(self, status, message):
        self.send_presence(pshow=status, pstatus=message)
    
    async def delete_account(self):
        delete_stanza_str = f"""
            <iq type="set" id="delete-account">
            <query xmlns="jabber:iq:register">
                <remove jid="{self.user}"/>
            </query>
            </iq>
        """

        try:
            self.send_raw(delete_stanza_str)
            # Enviar la stanza y esperar una respuesta
            print("Cuenta borrada exitosamente")
            self.connected = False
            self.disconnect()
        except IqError as err:
            print(f"Error deleting account: {err}")
            self.disconnect()
        except IqTimeout:
            print('Error: El servidor no respondio a tiempo')
            self.disconnect()
        
    async def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Nuevo mensaje de {msg['from']}: {msg['body']}")
    
    async def main_menu(self):
        while self.connected == True:
            menu()
            option = await ainput("Ingrese una opción: ")

            if option == "1":
                print("\nTodos los usuarios conectados:\n")
                contacts = await self.get_contacts()
                for contact in contacts:
                    print("Usuario", contact[0])
                    print("Estado:", contact[1])
                    print("Mensaje de estado:", contact[2])
            
            elif option == "2":
                print("\nAgregar a un usuario\n")
                jid = input("Ingrese el JID del usuario: ")
                jid = jid + "@alumchat.xyz"
                await self.add_user(jid)
            
            elif option == "3":
                print("\nMostrar detalles de un contacto\n")
                jid = input("Ingrese el JID del usuario: ")
                jid = jid + "@alumchat.xyz"
                contacts = await self.get_user_info(jid)
                for contact in contacts:
                    print("Usuario", contact[0])
                    print("Estado:", contact[1])
                    print("Mensaje de estado:", contact[2])

            
            elif option == "4":
                print("\nEnviar mensaje a un usuario\n")
                jid = input("Ingrese el JID del usuario: ")
                jid = jid + "@alumchat.xyz"
                await self.send_individual_message(jid)

            elif option == "5":
                print("\nEnviar un mensaje grupal\n")
                #Pendientes gato

            elif option == "6":
                print("\nDefinir mensaje de presencia\n")
                undefined = True
                status = ''
                print("Escoja el estado de presencia al que desea actualizar")
                print("1. Disponible")
                print("2. Ocupado")
                print("3. No disponible")
                print("4. Ausente")
                while undefined:
                    option = input("Ingrese una opción: ")
                    if option == "1":
                        status = ''
                        undefined = False
                    elif option == "2":
                        status = 'dnd'
                        undefined = False
                    elif option == "3":
                        status = 'xa'
                        undefined = False
                    elif option == "4":
                        status = 'away'
                        undefined = False
                    else:
                        print("Opción inválida")
                message = input("Ingrese el nuevo mensaje de presencia: ")
                await self.send_new_presence(status, message)
                await self.get_roster()
                print("Mensaje de presencia actualizado")

            elif option == "7":
                print("\nEnviar un archivo\n")
            
            elif option == "8":
                print("\nEliminar cuenta\n")
                valid = False
                while not valid:
                    print("¿Está seguro que desea eliminar su cuenta?")
                    print("1. Sí")
                    print("2. No")
                    option = input("Ingrese una opción: ")
                    if option == "1":
                        valid = True
                        await self.delete_account()
                    elif option == "2":
                        valid = True
                    else:
                        print("Opción inválida")
            elif option == "9":
                print("\nCerrando sesión\n")
                self.disconnect()
                self.connected = False

            else:
                print("Opción inválida")
            
            await asyncio.sleep(0.3)

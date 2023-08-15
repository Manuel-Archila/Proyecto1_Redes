import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from utilities import *
import asyncio
from aioconsole import ainput
from aioconsole.stream import aprint
import base64

class ChatClient(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.connected = False
        self.user = jid.split("@")[0]
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("subscription_request", self.subscription)
        self.add_event_handler("changed_status", self.changed_status)
        self.add_event_handler("groupchat_invite", self.group_invite)
        self.add_event_handler("message", self.message)
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0030') # Service Discovery


    async def start(self, event):
        try:
            self.send_presence()
            await self.get_roster()
            self.connected = True
            print("\nConexion establecida\n")
            asyncio.create_task(self.main_menu())
        except IqError as err:
            self.connected = False
            print(f"Error: {err}")
            self.disconnect()
        except IqTimeout:
            self.connected = False
            print('Error: El servidor no respondio a tiempo')
            self.disconnect()
    
    async def subscription(self, event):
        try:
            if event['type'] == 'subscribe':
                self.send_presence(pto=event['from'], ptype='subscribed')
                await self.get_roster()
        except IqError as err:
            self.connected = False
            print(f"Error: {err}")
            self.disconnect()
        except IqTimeout:
            self.connected = False
            print('Error: El servidor no respondio a tiempo')
            self.disconnect()
    
    async def group_invite(self, event):
        group = event['from']
        self.plugin['xep_0045'].join_muc(group, self.boundjid.user)
        print(f"\nSe ha unido al grupo {group}\n")

    
    async def changed_status(self, event):
        try:
            if event['from'].bare != self.boundjid.bare and "conference" not in event["from"].domain:
                if event["type"] == "unavailable":
                    print(f"\n{event['from'].bare} se ha desconectado\n")
                else:
                    estado = event['show']
                    if estado == 'dnd':
                        estado = 'Ocupado'
                    elif estado == 'xa':
                        estado = 'No disponible'
                    elif estado == 'away':
                        estado = 'Ausente'
                    else:
                        estado = 'Disponible'
                    print(f"\n{event['from'].bare} a cambiado su estado a {estado}\n")
        except IqError as err:
            self.connected = False
            print(f"Error: {err}")
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
            print(f"Error: {err}")
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
    
    async def create_lobby(self, lobby_name):
        try:
            self.plugin['xep_0045'].join_muc(lobby_name, self.boundjid.bare)

            await asyncio.sleep(2)
            new_form = self.plugin['xep_0004'].make_form(ftype='submit')
            new_form['muc#roomconfig_roomname'] = lobby_name
            new_form['muc#roomconfig_persistentroom'] = '1'
            new_form['muc#roomconfig_publicroom'] = '1'
            new_form['muc#roomconfig_membersonly'] = '0'
            new_form['muc#roomconfig_allowinvites'] = '1'
            new_form['muc#roomconfig_enablelogging'] = '1'
            new_form['muc#roomconfig_changesubject'] = '1'
            new_form['muc#roomconfig_maxusers'] = '100'
            new_form['muc#roomconfig_whois'] = 'anyone'
            new_form['muc#roomconfig_roomdesc'] = 'Chat room'
            new_form['muc#roomconfig_roomowners'] = [self.boundjid.bare]

            await self.plugin['xep_0045'].set_room_config(lobby_name, config=new_form)

            print("\nChat de grupo", lobby_name, "creado correctamente\n")

            open_invite = True
            while open_invite:
                invite = await ainput("Ingrese el nombre de usuario que desea invitar: ")
                full_invite = invite + "@alumchat.xyz"
                self.plugin['xep_0045'].invite(room= lobby_name, jid=full_invite, reason="Invitación a chat de grupo")
                await aprint("Se ha enviado una invitación a", invite, "para unirse al grupo.")
                invite_more = await ainput("¿Desea invitar a alguien más? (y/n): ")
                if invite_more == "n":
                    open_invite = False
        except IqError as err:
            print(f"Error: {err}")
        except IqTimeout:
            print('Error: El servidor no respondio a tiempo')

    async def send_group_message(self, lobby_name):
        in_ = True
        while in_:
            msg = await ainput("Ingrese el mensaje que desea enviar: ")
            if msg == "out":
                in_ = False
            else:
                self.send_message(mto=lobby_name, mbody=msg, mtype='groupchat')
                print("Mensaje enviado")
    
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
            if "file|" in msg['body']:
                body = msg['body'].split("|")
                file_extension = body[1]
                file_data_base64 = body[2]
                file_data = base64.b64decode(file_data_base64.encode('utf-8'))
                filename = "received_file." + file_extension
                with open(filename, 'wb') as file:
                    file.write(file_data)
                print(f"Nuevo archivo recibido de {msg['from']}")
            else:
                print(f"Nuevo mensaje de {msg['from']}: {msg['body']}")
        
        if msg['type'] == 'groupchat':
            grupo = msg['from'].bare
            emisor = msg['from'].resource
            if emisor != self.boundjid.user:
                print(f"Nuevo mensaje en el grupo {grupo} de {emisor}: {msg['body']}")
    
    async def send_file(self, jid, filename):
        file_extension = filename.split('.')[-1]
        with open(filename, 'rb') as file:
            file_data = file.read()
            file_data_base64 = base64.b64encode(file_data).decode('utf-8')
            message = "file|" + file_extension + "|" + file_data_base64
            self.send_message(mto=jid, mbody=message, mtype='chat')
        print(f"File '{filename}' enviado a {jid}")
    
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
                    print()
            
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
                    print()

            
            elif option == "4":
                print("\nEnviar mensaje a un usuario\n")
                jid = input("Ingrese el JID del usuario: ")
                jid = jid + "@alumchat.xyz"
                await self.send_individual_message(jid)

            elif option == "5":
                print("\nMenu de grupos\n")
                in_group_menu = True
                while in_group_menu:
                    print("1. Crear un grupo")
                    print("2. Unirse a un grupo existente")
                    print("3. Salir del menu de grupos")
                    new_option = input("Ingrese una opción: ")
                    if new_option == "1":
                        print("\nCrear un grupo\n")
                        lobby_name = input("Ingrese el nombre del grupo: ")
                        lobby_name = lobby_name + "@conference.alumchat.xyz"
                        await self.create_lobby(lobby_name)
                    elif new_option == "2":
                        print("\nUnirse a un grupo existente\n")
                        lobby_name = input("Ingrese el nombre del grupo al que desea unirse: ")
                        lobby_name = lobby_name + "@conference.alumchat.xyz"
                        await self.send_group_message(lobby_name)
                        
                    elif new_option == "3":
                        print("\nSalir del menu de grupos\n")
                        in_group_menu = False
                    else:
                        print("Opción inválida")

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
                jid = input("Ingrese el JID del usuario: ")
                jid = jid + "@alumchat.xyz"
                filename = input("Ingrese el nombre del archivo: ")
                await self.send_file(jid, filename)
            
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

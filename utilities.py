import xmpp

def menu():
    print("1. Mostrar usuarios conectados")
    print("2. Agregar a un usuario")
    print("3. Mostrar detalles de un contacto")
    print("4. Enviar mensaje a un usuario")
    print("5. Opciones de grupo")
    print("6. Definir mensaje de presencia")
    print("7. Enviar un archivo")
    print("8. Eliminar cuenta")   
    print("9. Cerrar sesión")

def register(client, password):
        jid = xmpp.JID(client)
        account = xmpp.Client(jid.getDomain(), debug=[])
        account.connect()
        return bool(
            xmpp.features.register(account, jid.getDomain(), {
                'username': jid.getNode(),
                'password': password
        }))


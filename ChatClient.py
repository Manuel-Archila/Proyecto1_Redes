import slixmpp

class ChatClient(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):
        self.send_presence()
        await self.get_rooster()


    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("----------------------------------------------------")
            print("Mensaje de:", msg['from'])
            print("Asunto:", msg['subject'])
            print("Mensaje:", msg['body'])
            print("----------------------------------------------------")
    
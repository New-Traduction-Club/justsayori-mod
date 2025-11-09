init -999 python:

    from pypresence import Presence
    import time

    def setupRPC(status=None):

        client_id = '1436898855886131212'  # Fake ID, put your real one here
        RPC = Presence(client_id)  # Initialize the client class
        RPC.connect() # Start the handshake loop

        if status is None:
            raise Exception("Must provide status")

        print(RPC.update(state=status, large_image='faelogo', details=___("Spending Time With Sayori"), start=time.time(), large_text=___("Just Sayori")))  
from threading import Event # Monkey patched

class User:
    def __init__(self, name, socketio, room, sid):
        self.name = name
        self.socketio = socketio
        self.room = room
        self._sid = sid

    @property
    def sid(self):
        return self._sid

    @sid.setter
    def sid(self, new_sid):
        self._sid = new_sid

    def call(self, event_name, data):
        """
        Send a request to the player and wait for a response.
        """
        event = Event()
        response = None

        # Create callback to run when a response is received
        def ack(response_data):
            print("WHY DOES THIS NOT RUN AFTER A REJOIN?")
            nonlocal event
            nonlocal response
            response = response_data
            event.set()
      
        # Try in a loop with a one second timeout in case an event gets missed or a network error occurs
        tries = 0
        while True:
            # Send request
            self.socketio.emit(
                event_name,
                data, 
                to=self.sid,
                callback=ack,
            )
            # Wait for response
            if event.wait(1):
                # Response was received
                break
            tries += 1
            if tries % 10 == 0:
                print(f"Still waiting for input after {tries} seconds")

        return response
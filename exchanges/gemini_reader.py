from geminipy import Geminipy
from exchanges import Exchange


class Gemini(Exchange):
    client = None

    def __init__(self, config):
        try:
            self.client = Geminipy.AuthenticatedClient(
                config['key'], config['secret'], config['passphrase']
            )
            print('Connected to Gemini.')
        except:
            print('Could not connect to Gemini.')

    def get_buys_sells(self):
        pass

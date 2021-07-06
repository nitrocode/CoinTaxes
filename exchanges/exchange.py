from exchanges import CachedClient

class Exchange(object):
    client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()
        return False

    def get_client(self):
        raise NotImplemented

    def get_cached_client(self, client_name):
        return CachedClient(client_name, self.get_client)

    def done(self):
        client = self.client
        if client != None and hasattr(client, "cache_commit") and callable(client.cache_commit):
            client.cache_commit()
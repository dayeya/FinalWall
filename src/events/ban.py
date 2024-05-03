from src.time_utils import get_epoch_time


class BanMap:
    """
    A class representing a ban map.
    Notes:
        If a client is banned and is trying to access a service within the ban period his ban will increase.

    """
    def __init__(self):
        self.__map: dict[bytes, (float, float)] = {}

    def insert_client(self, client_hash: bytes, ban_duration: float):
        self.__map[client_hash] = (get_epoch_time(), ban_duration)

    def get_ban_state(self, client_hash) -> tuple[float, float]:
        return self.__map[client_hash]

    def remove_client(self, client_hash):
        self.__map.pop(client_hash)

    def still_banned(self, client_hash) -> bool:
        current_time = get_epoch_time()
        ban_duration, banned_at = self.get_ban_state(client_hash)
        if (diff := current_time - banned_at) < ban_duration:  # Still banned...
            return True
        return False

    def __contains__(self, client_hash):
        return client_hash in self.__map.keys()

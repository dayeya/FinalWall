import redis
from src.time_utils import get_epoch_time

from src.components.singleton import Singleton


class BanManager(metaclass=Singleton):
    """
    A wrapper class to redis.Redis representing a ban manager.

    Notes
    -----
    1. BanManager will access the redis db in a separate task evaluating all the bans.
    2. A client is freed when a ban is over or when the admin removes the ban.
    3. A ban is extended when a client exceeds the attack threshold.
    """
    def __init__(self):
        try:
            self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        except Exception as e:
            raise e

    def insert_mapping(self, client_hash: str, time_of_ban: float, ban_duration: float):
        """
        Sets a new entry inside the cache of client_hash and its ban state.

        Notes
        -----
        1. Will not override existing mappings.
        2. Will expire the cache entry automatically if not configured otherwise.

        :param client_hash:
        :param ban_duration:
        :param time_of_ban:
        :return:
        """
        if self.r.exists(client_hash):
            return
        successful_ops = self.r.hset(client_hash, mapping={
            "banned_at": time_of_ban,
            "duration_remaining": ban_duration
        })
        if successful_ops != 2:  # Error with Redis.hset()
            print("Redis.hset() error. Not all values of given mapping were successfully inserted.")
        self.r.expire(name=client_hash, time=int(ban_duration))

    def get_ban_state(self, client_hash: str) -> dict:
        """
        Retrieves an entry from the cache.
        :param client_hash:
        :return:
        """
        if not self.r.exists(client_hash):
            print(f"Given argument {client_hash} does not exist in the cache")
            return {}
        return self.r.hgetall(client_hash)

    def remove_client(self, client_hash: str):
        """
        Removes a client_hash and its mapping from the cache.
        :param client_hash:
        :return:
        """
        if not self.r.exists(client_hash):
            print(f"Given argument {client_hash} does not exist in the cache")
        self.r.hdel(client_hash)

    def banned(self, client_hash: str) -> bool:
        """
        Returns if the client_hash represents an active ban.
        :param client_hash:
        :return:
        """
        print("Before r.exists()")
        if not self.r.exists(client_hash):
            print("Inside! r.exists()")
            return False
        current_time = get_epoch_time()
        state = self.get_ban_state(client_hash)
        return current_time - state["banned_at"] <= state["duration_remaining"]

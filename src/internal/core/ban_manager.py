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
    def __init__(self, logs=True):
        try:
            self.__logs = logs
            self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        except redis.exceptions.ConnectionError:
            print("Redis server is not running. Please run scripts/run_redis before deploying.")

    def log(self, msg: str):
        """
        Log `msg` if __logs is True.
        :param msg:
        :return:
        """
        if self.__logs:
            print(msg)

    def redis_alive(self) -> bool:
        """
        Checks the connection to the redis server.
        :return:
        """
        return self.r.ping()

    def insert_mapping(self, client_hash: str, banned_at: float, ban_duration: float):
        """
        Sets a new entry inside the cache of client_hash and its ban state.
        Will expire the cache entry automatically if not configured otherwise.
        :param client_hash:
        :param ban_duration:
        :param banned_at:
        :return:
        """
        self.r.hset(client_hash, key="banned_at", value=str(banned_at))
        self.r.hset(client_hash, key="duration_remaining", value=str(ban_duration))
        self.r.expire(name=client_hash, time=int(ban_duration))

    def get_mapping(self, client_hash: str) -> dict:
        """
        Retrieves an entry from the cache.
        :param client_hash:
        :return:
        """
        if not self.r.exists(client_hash):
            self.log(f"Given argument {client_hash} does not exist in the cache")
            return {}
        return self.r.hgetall(client_hash)

    def remove_client(self, client_hash: str):
        """
        Removes a client_hash and its mapping from the cache.
        :param client_hash:
        :return:
        """
        if not self.r.exists(client_hash):
            self.log(f"Given argument {client_hash} does not exist in the cache")
        self.r.hdel(client_hash)

    def banned(self, client_hash: str) -> bool:
        """
        Returns if the client_hash represents an active ban.
        :param client_hash:
        :return:
        """
        return self.r.exists(client_hash)


if __name__ == "__main__":

    bm = BanManager()
    hashy = "14145d0b335424d93d9100b07ad16ec72a268511"
    bm.insert_mapping(hashy, 1.0, 5.0)

    print(bm.get_mapping(hashy))

    import time
    time.sleep(5.0)

    print(bm.get_mapping(hashy))
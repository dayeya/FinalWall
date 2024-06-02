import redis
from engine.time_utils import get_unix_time
from engine.components.singleton import Singleton
from engine.internal.events import Event, AUTHORIZED_REQUEST, UNAUTHORIZED_REQUEST


class EventManager(metaclass=Singleton):
    def __init__(
            self,
            host="localhost",
            port=6379,
            access_events_namespace="access_events",
            security_events_namespace="security_events",
            logs=True
    ):
        try:
            self.__logs = logs
            self.__host, self.__port = host, port
            self.__last_security_update, self.__last_access_update = 'Nan', 'Nan'
            self.__access_events_namespace = access_events_namespace
            self.__security_events_namespace = security_events_namespace
            self.access_events_redis = redis.Redis(host=host, port=port)
            self.security_events_redis = redis.Redis(host=host, port=port)
        except redis.exceptions.ConnectionError:
            print("Redis server is not running. Please run scripts/run_redis before deploying.")

    @property
    def service_report(self):
        """Builds a report of the EventManager."""
        access_cache_size, security_cache_size = len(self.get_access_events()), len(self.get_security_events())
        return {
            "redis_host": self.__host,
            "redis_port": self.__port,
            "cache_size": access_cache_size + security_cache_size,
            "access_events_size": access_cache_size,
            "security_events_size": security_cache_size,
            "last_security_update": self.__last_security_update,
            "last_access_update": self.__last_access_update
        }

    def log(self, msg: str):
        """
        Log `msg` if __logs is True.
        :param msg:
        :return:
        """
        if self.__logs:
            print(msg)

    def redis_alive(self) -> tuple:
        """
        Checks the connections to the redis server.
        :return:
        """
        return self.access_events_redis.ping(), self.security_events_redis.ping()

    def cache_event(self, event: Event):
        """
        Sets a new entry inside the cache of client_hash and its access log.
        Will expire the cache entry automatically if not configured otherwise.
        :return:
        """
        redis_client, namespace = None, ''
        
        if event.kind == AUTHORIZED_REQUEST:
            redis_client = self.access_events_redis
            namespace = self.__access_events_namespace
            self.__last_access_update = get_unix_time("Asia/Jerusalem")

        if event.kind == UNAUTHORIZED_REQUEST:
            redis_client = self.security_events_redis
            namespace = self.__security_events_namespace
            self.__last_security_update = get_unix_time("Asia/Jerusalem")

        redis_client.zadd(namespace, mapping={Event.serialize(event): event.log.sys_epoch_time})

    def get_access_events(self):
        """Retrieves the access, events ordered set from the cache."""
        return [Event.deserialize(event) for event in
                self.access_events_redis.zrange(self.__access_events_namespace, start=0, end=-1)]

    def get_security_events(self):
        """Retrieves the security events, ordered set from the cache."""
        return [Event.deserialize(event) for event in
                self.security_events_redis.zrange(self.__security_events_namespace, start=0, end=-1)]

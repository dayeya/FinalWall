import asyncio
from dataclasses import dataclass


@dataclass(slots=True)
class AccessList:
    api: str
    acl: list
    interval: int

    @staticmethod
    def fetch_anonymous_proxies():
        """
        response = requests.get(AccessList.api)
        if response.status_code != 200:
            raise RuntimeError(f"ACL.{AccessList.fetch_anonymous_proxies.__name__} failed")
        AccessList.acl = response.text
        print("Fetched!")
        """
        with open(AccessList.api, "r") as exit_nodes:
            AccessList.acl = exit_nodes.readlines()

    @staticmethod
    async def activity_loop(max_retries=10):
        """
        Activity loop of refetching the Tor exit nodes.
        """
        tries = 0
        while True:
            await asyncio.sleep(AccessList.interval)
            try:
                AccessList.fetch_anonymous_proxies()
            except RuntimeError as e:
                if tries <= max_retries:
                    tries += 1
                    print(f"{e}, retrying")
                    continue
                break
        raise Exception("Reached loop limit, check for API connection")

    def __contains__(self, ip):
        return ip in AccessList.acl

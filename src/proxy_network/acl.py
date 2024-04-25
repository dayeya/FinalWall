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
        Until my router is fixed I will use a hard-coded list of ips.
        """
        with open(AccessList.api, "r") as data:
            exit_nodes = data.readlines()
            AccessList.acl = exit_nodes

    @staticmethod
    async def activity():
        """
        Refreshes the ACL every interval.
        """
        while True:
            await asyncio.sleep(AccessList.interval)
            AccessList.fetch_anonymous_proxies()

    def __contains__(self, ip):
        return ip in AccessList.acl

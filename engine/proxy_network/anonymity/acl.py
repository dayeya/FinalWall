#
# FinalWall - ACL for untrusted products.
# Author: Dayeya
#

import time
import asyncio
import requests
from dataclasses import dataclass
from engine.errors import AclFetchError, AclBackUpError


@dataclass(slots=True)
class AccessList:
    """A class representing a list of ip addresses of untrusted proxies."""
    main_list: list
    api: str
    interval: int
    backup: str

    def fetch_anonymous_proxies(self):
        try:
            response = requests.get(self.api)
            if response.status_code != 200:
                raise AclFetchError(f"ACL.{AccessList.fetch_anonymous_proxies.__name__} failed")
            self.main_list = response.text.split("\n")

        except (AclFetchError, requests.exceptions.SSLError):
            try:
                with open(self.backup, "r") as exit_nodes:
                    self.main_list = exit_nodes.read().split("\n")
            except FileNotFoundError:
                raise AclBackUpError("Backup is not available. Please check config.toml for ACL.backup")

    def activity_loop(self, max_retries=10):
        """Activity loop of refetching the Tor exit nodes."""
        tries = 0
        while True:
            try:
                self.fetch_anonymous_proxies()
                time.sleep(self.interval)
            except (AclFetchError, AclBackUpError) as e:
                if tries <= max_retries:
                    tries += 1
                    print(f"{e}, retrying")
                    continue
                break
            except asyncio.exceptions.CancelledError:
                """Coroutine was cancelled."""
                return
        raise Exception("Reached loop limit, check for API connection")

    def __contains__(self, ip):
        return ip in self.main_list

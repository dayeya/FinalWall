class AccessList:
    acl: list
    interval: int = 30

    @staticmethod
    def fetch_anonymous_proxies():
        """
        Until my router is fixed I will use a hard-coded list of ips.
        """
        with open("TorExitNodes.txt", "r") as data:
            exit_nodes = data.readlines()
            AccessList.acl = exit_nodes

    @staticmethod
    def activity():
        """
        Refreshes the ACL every interval.
        """
        pass

    def __contains__(self, ip):
        return ip in AccessList.acl

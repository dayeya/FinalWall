#!/usr/bin/env python
#
# FinaWall - An example of using the finalwall-engine module with a unique WafConfig.
# Author: Dayeya
#
# *NOT FINISHED*

import asyncio
from finalwall import Waf, WafConfig
from finalwall.errors import VersionError


async def main():
    """Main program"""
    conf = WafConfig()
    waf = Waf(
        conf=conf,
        ucid=8585,
        local=True,
        with_tunneling=True,
    )
    await waf.deploy()
    await waf.work()

if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())

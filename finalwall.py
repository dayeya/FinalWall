import asyncio

from engine import Waf, WafConfig
from engine.net import create_new_task
from engine.errors import VersionError


async def main():
    """
    Main entry point of program. the start of the Asyncio.Eventloop.
    Generated coroutines:
        WAF_WORK: Main work of the Waf instance.
        WAF_ACL_LOOP: Background task that updates the ACL (access list) once every interval.
    :return: None
    """
    conf = WafConfig()
    waf = Waf(conf=conf)
    await waf.deploy()

    work = [
        create_new_task(task_name="WAF_WORK", task=waf.work, args=()),
        create_new_task(task_name="WAF_ACL_LOOP", task=waf.start_acl_loop, args=())
    ]
    await asyncio.gather(*work)


if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())

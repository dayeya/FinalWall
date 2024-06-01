import asyncio

from engine import Waf, WafConfig
from engine.net import create_new_task
from engine.errors import VersionError


async def main():
    """Main program"""
    conf = WafConfig()
    waf = Waf(
        conf=conf,
        ucid=8585,
        local=True,
        with_tunneling=True,
        init_api=True
    )
    await waf.deploy()
    await waf.work()

    # work = [
    #     create_new_task(task_name="WAF_WORK", task=waf.work, args=()),
    #     create_new_task(task_name="WAF_ACL_LOOP", task=waf.start_acl_loop, args=()),
    #     create_new_task(task_name="WAF_API_LISTENER", task=waf.start_api, args=())
    # ]
    # await asyncio.gather(*work)


if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())

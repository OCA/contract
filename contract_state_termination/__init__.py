from . import models


def post_init_hook(env):
    env["contract.contract"]._sync_terminated_state()

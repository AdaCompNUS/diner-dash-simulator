import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='DinerDash-v0',
    entry_point='diner_dash.envs:DinerDashEnv',
    # timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic=True,
)

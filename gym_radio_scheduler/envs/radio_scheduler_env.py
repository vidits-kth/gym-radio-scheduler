import gym
from gym import error, spaces, utils
from gym.utils import seeding

from .radio_multilink_scheduler import RadioMultilinkScheduler

class RadioSchedulerEnv(gym.Env):
  metadata = {'render.modes': ['random']}
  
  def __init__(self):

    # nrof_ues: Integer value
    # scheduler_type: ['Random', 'MaxRate', 'RoundRobin', 'PropFair']
    self.sched = RadioMultilinkScheduler(nrof_ues=30, scheduler_type='Random')

  def step(self, action=-1):
    result = self.sched.transmit()

    return result

  def reset(self):
    pass

  def render(self, mode='random', close=False):
    pass

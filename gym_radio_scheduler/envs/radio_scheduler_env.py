import gym
from gym import error, spaces, utils
from gym.utils import seeding

from radio_multilink_scheduler import RadioMultilinkScheduler

class RadioSchedulerEnv(gym.Env):
  metadata = {'render.modes': ['random']}
  
  def __init__(self):
    self.sched = RadioMultilinkScheduler(nrof_ues=30, scheduler_type='Random')

  def step(self, action):
    reward = self.sched.transmit(action)

  def reset(self):
    pass

  def render(self, mode='random', close=False):
    pass

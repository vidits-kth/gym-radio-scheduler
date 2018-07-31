import gym
from gym import error, spaces, utils
from gym.utils import seeding

from .radio_multilink_scheduler import RadioMultilinkScheduler

class RadioSchedulerEnv(gym.Env):
#    metadata = {'render.modes': ['random']}
    
    def __init__(self):
  
        # nrof_ues: Integer value
        # scheduler_type: ['Random', 'MaxRate', 'RoundRobin', 'PropFair']
        self.sched = RadioMultilinkScheduler(nrof_ues=30, scheduler_type='Random')
  
    def step(self, action=-1):
        """
           A step in the environment.
     
           Parameters
           ----------
           action : int in range [0, 30]
           
           action: 
               The UE specified by the action is scheduled in the next
               transmission time interval (TTI). If action is -1, the traditional
               radio scheduler schedules one of the UEs with index [0,...,30].
     
           Returns
           -------
           scheduled_ue_index, channel_quality_index, realized_throughput : tuple
     
           scheduled_ue_index (int) :
               UE scheduled in the current TTI either by specified action or
               by the radio scheduler
           channel_quality_index (int) :
               The observed channel quality index (CQI) for the UE scheduled
               in the current TTI.
           realized_throughput (int) :
               Throughput is 0 if tranmsission failed or UE was out of range,
               otherwise the number of information bits transmitted successfully.
        """
        result = self.sched.transmit(action)
  
        return result
  
    def reset(self):
        result = self.sched.transmit(-1)

        return result[1]
  
    def render(self, mode='random', close=False):
        pass

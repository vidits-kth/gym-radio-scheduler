from gym.envs.registration import register

register(id = 'RadioScheduler-v0',
         entry_point = 'gym_radio_scheduler.envs:RadioSchedulerEnv')

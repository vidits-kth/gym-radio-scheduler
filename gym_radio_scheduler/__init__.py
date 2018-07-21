from gym.envs.registration import register

register(id = 'radio-scheduler-v0',
         entry_point = 'radio-scheduler.envs:RadioSchedulerEnv')

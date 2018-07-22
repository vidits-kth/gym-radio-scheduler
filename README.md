# gym-radio-scheduler  

This repository contains a PIP package which is an OpenAI environment for simulating a radio scheduler.  

# Installation  
Install [OpenAI gym](https://github.com/openai/gym#installation).    
Install [py-itpp](https://github.com/vidits-kth/py-itpp).  
Clone [simulator](https://github.com/vidits-kth/py-radio-multilink-scheduler).  
Add the simulator to PYTHONPATH.  
  
# Usage  
import gym  
import gym_radio_scheduler  
env = gym.make('RadioScheduler-v0')  

result = env.step()  
print(result) 

The result is a tuple containing (scheduled_ue_index, channel_quality_index, realized_throughput)  

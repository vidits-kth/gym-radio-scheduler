import numpy as np
import os

# Load parameters from a parameter file
def load_from_file(filepath, encoding=''):
    if encoding == '':
        return np.load(filepath)[()]
    else:
        return np.load(filepath, encoding=encoding)[()]

# Create directory to store simulation parameters and results
def create_new_simulation_directory(base_dir):
    if not os.path.exists(base_dir):
        # Create the base directory and initialize the sim_id to 1
        os.makedirs(base_dir)
        sim_id = 1
    else:
        # Find the largest existing sim_id
        largest_sim_id = 0
        for name in os.listdir(base_dir):
            try:
                name_int = int(name)
                if name_int > largest_sim_id:
                    largest_sim_id = name_int
            except ValueError:
                # Ignore this name 
                pass
        
        sim_id = largest_sim_id + 1
        
    # Create new sim directory
    sim_id_str = '%06d'%(sim_id)    
    sim_dir = base_dir + '/' + sim_id_str + '/'
    
    os.makedirs(sim_dir)
    
    return sim_dir

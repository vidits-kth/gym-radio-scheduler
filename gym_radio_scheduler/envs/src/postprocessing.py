import numpy as np

def save_simulation_result(filepath, ue_statistics=[], descr=''):
    nrof_ues = len(ue_statistics)
    
    # Prepare a dict to hold variables to be saved
    data = {'description': descr}
    
    # Copy the UE statistics
    data['ue_statistics'] = [{} for _ in range(nrof_ues)]
    for ue_index in range(nrof_ues):                
        for key, value in ue_statistics[ue_index].items():
            data['ue_statistics'][ue_index][key] = value.to_numpy_ndarray()
        
    print('Saving simulation result to %s'%(filepath))
    np.save(filepath, data)
    
    return filepath 

def load_simulation_result(filepath):
    return np.load(filepath)[()]
    
def save_simulation_data(filepath, sim_par, sim_stats, ue_data, nrof_ues):
    # Prepare a dict to hold variables to be saved
    data = {}
    
    # Copy the simulation parameters
    data['sim'] = {}
    data['sim']['par'] = sim_par

    # Iteratively copy the simulation statistics, converting py-itpp 
    # data structures to Numpy arrays
    data['sim']['statistics'] = {}
    for key, value in sim_stats.items():
        data['sim']['statistics'][key] = value.to_numpy_ndarray()
    
    # Copy the UE data
    data['ue'] = [{} for _ in range(nrof_ues)]
    for ue_index in range(nrof_ues):
        
        # Handle the special case of a single UE for indexing
        if nrof_ues == 1:
            data['sim']['par']['nrof_ues'] = 1
            current_ue_data = ue_data
        else:
            current_ue_data = ue_data[ue_index]
            
        data['ue'][ue_index]['par'] = current_ue_data['par']

        # Iteratively copy the UE state and statistics, converting py-itpp 
        # data structures to Numpy arrays        
        data['ue'][ue_index]['state'] = {}
        for key, value in current_ue_data['state'].items():
            data['ue'][ue_index]['state'][key] = value.to_numpy_ndarray()
                    
        data['ue'][ue_index]['statistics'] = {}
        for key, value in current_ue_data['statistics'].items():
            data['ue'][ue_index]['statistics'][key] = value.to_numpy_ndarray()
        
    print('Saving simulation data to %s'%(filepath))
    np.save(filepath, data)
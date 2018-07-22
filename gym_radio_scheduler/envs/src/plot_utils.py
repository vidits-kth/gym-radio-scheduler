import numpy as np

import matplotlib
#matplotlib.use('Agg')

from matplotlib import pyplot as plt

def calculate_window_average(values, win_size):
    nrof_values = len(values)
    nrof_windows = int(nrof_values / win_size)
    winavg = np.ndarray((nrof_windows))
    for window_index in range(nrof_windows):
        window_values = values[window_index * win_size : (window_index + 1) * win_size]
        winavg[window_index] = sum(window_values) / float(win_size)
        
    return winavg

def calculate_moving_average(values, win_size):
    nrof_values = len(values)
    moving_avg_values = np.ndarray((nrof_values - win_size))
    for i in range(nrof_values - win_size):
        win_values = values[i : i + win_size]
        moving_avg_values[i] = sum(win_values) / float(win_size)
        
    return moving_avg_values
            
def calculate_jain_fairness_index(values):
    nrof_resources = len(values)
     
    sum_of_squared_values = sum([np.square(x) for x in values])
    square_of_summed_values = np.square(sum(values))
    
    fairness_index = []
    for i in range(len(sum_of_squared_values)):
        if sum_of_squared_values[i] != 0:
            fairness_index.append(square_of_summed_values[i] / (nrof_resources * sum_of_squared_values[i]))
            
    return fairness_index

# Plot
# Plot Flags: [Moving Average Throughput, Window Average Throughput, Jain Fairness Index]
def plot_average_throughput_and_fairness_index(filepath, plot_flags=[True, True, True], tput_win_size=100):
    
    data = np.load(filepath)[()]
    
    sim_par = data['sim']['par']
    nrof_ues = sim_par['nrof_ues']
    nrof_subframes = sim_par['nrof_subframes']
    
    ue = data['ue']
    
    nrof_subplots = sum(plot_flags)
    ax_index = 0
    _, ax = plt.subplots(nrof_subplots, 1, figsize=(8, 11))
    
#    f.suptitle(sim_par['scheduler_type'])
    legend_strings = []
    snr_dB = np.ndarray((nrof_ues))
    for ue_index in range(nrof_ues):
        noise_variance = ue[ue_index]['par']['noise_variance']
        snr_dB[ue_index] = 10 * np.log10(1.0 / noise_variance)
        legend_strings.append('User %d SNR %d dB'%(ue_index, snr_dB[ue_index]))
    legend_strings.append('Cell')
    
    ue_subframe_tputs = []
    cell_subframe_tputs = np.zeros((nrof_subframes))
    for ue_index in range(nrof_ues):
        ue_subframe_tputs.append(ue[ue_index]['statistics']['subframe_throughput'])
        cell_subframe_tputs = cell_subframe_tputs + ue_subframe_tputs[ue_index]
    
    # Moving average of throughput
    if (plot_flags[0]):
        for ue_index in range(nrof_ues):
            ue_moving_avg_tput = calculate_moving_average(ue_subframe_tputs[ue_index], tput_win_size)
            ax[ax_index].semilogy(ue_moving_avg_tput)
             
        cell_moving_avg_tput = calculate_moving_average(cell_subframe_tputs, tput_win_size)
             
        ax[ax_index].semilogy(cell_moving_avg_tput)
         
        ax[ax_index].set_ylim([1, 1000])
        ax[ax_index].set_ylabel('Throughput (Mov. Avg., N=%d) [kbps]'%(tput_win_size))
        ax[ax_index].set_xlabel('Subframe Index (offset %d)'%(tput_win_size))
        ax[ax_index].grid(True)
        ax[ax_index].legend(legend_strings)
        
        ax_index = ax_index + 1
    
    # Plot the cumulative distribution of the window averages        
    ue_winavg_tput = [calculate_window_average(ue_subframe_tputs[ue_index], tput_win_size) for ue_index in range(nrof_ues)]
        
    ue_winavg_tput_sorted = [np.sort(ue_winavg_tput[ue_index]) for ue_index in range(nrof_ues)]
    cell_winavg_tput_sorted = sum(ue_winavg_tput_sorted)
    
    nrof_windows = len(cell_winavg_tput_sorted)
    y = np.arange(nrof_windows) / float(nrof_windows)
    
    if (plot_flags[1]):
        for ue_index in range(nrof_ues):
            ax[ax_index].semilogx(ue_winavg_tput_sorted[ue_index] / 1e3, y) 
            
        ax[ax_index].semilogx(cell_winavg_tput_sorted / 1e3, y)
        
        # Plot percentiles if enough data was collected
        if nrof_windows >= 100:
            print('Displaying percentile values on throughput plot')
    
            percentiles = [5, 50, 95]
            text_offset = 1.2
            for perc in percentiles:
                tput_pc = cell_winavg_tput_sorted[int(nrof_windows * perc / 100.0)]
                ax[ax_index].scatter(tput_pc, perc / 100.0, marker='*', c='k', s=100)
                ax[ax_index].text(tput_pc * text_offset, perc / 100.0, str(tput_pc), va='center', fontsize=16) 
    
        ax[ax_index].set_xlim([1e0, 1e3])
        ax[ax_index].tick_params(labelsize=16)
        ax[ax_index].set_xlabel('Throughput [kbps]', fontsize=20)
        ax[ax_index].set_ylabel('CDF', fontsize=20)
        ax[ax_index].grid(True)
        #ax[0].legend(legend_strings)
        
        ax_index = ax_index + 1
    
    # Calculate the Jain fairness index
    window_sizes = np.arange(10, 101, 10)
    avg_fairness = np.ndarray((len(window_sizes))) 
    for i, W in enumerate(window_sizes):
        ue_scaled_tput = []
        for ue_index in range(nrof_ues):
            window_avg_tput = calculate_window_average(ue_subframe_tputs[ue_index], W)
            ue_scaled_tput.append(window_avg_tput / snr_dB[ue_index])
        
        avg_fairness[i] = np.mean(calculate_jain_fairness_index(ue_scaled_tput))
        
    if (plot_flags[2]):
        ax[ax_index].plot(window_sizes, avg_fairness)
        ax[ax_index].set_ylim([0, 1])
        ax[ax_index].tick_params(labelsize=16)
        ax[ax_index].set_xlabel('Window Size', fontsize=20)
        ax[ax_index].set_ylabel('Fairness Index', fontsize=20)
        ax[ax_index].grid(True)
        
        ax_index = ax_index + 1
    
    #plt.figure()
    #plt.plot(cqi)
    
    #plt.figure()
    #plt.plot(nrof_harq_transmissions)
    
    plot_filepath = filepath.replace('npy', 'png')
    plot_filepath = plot_filepath.replace('DATA', 'PLOT')
    print('Saving plot to %s'%(plot_filepath))
    plt.savefig(plot_filepath)
    
    plt.show()
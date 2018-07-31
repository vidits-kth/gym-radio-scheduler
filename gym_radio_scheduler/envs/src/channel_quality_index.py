import py_itpp as pyp
import numpy as np
from .CONSTANTS import CUSTOM_SYSTEM_CONFIG as CONFIG

def determine_snr_at_bler_target(awgn_data, bler_target):
    awgn_snr_range_dB = awgn_data['snr_range_dB']
    awgn_snr_vs_bler = awgn_data['snr_vs_bler']

    _, nrof_cqi = awgn_snr_vs_bler.shape
    
    snr_at_bler_target = pyp.vec(nrof_cqi)
    snr_at_bler_target[0] = -100 # CQI for out of range link
    for i in range(1, nrof_cqi):
        bler = awgn_snr_vs_bler[:, i]
        hbler_indices = np.argwhere(bler > bler_target) # Indices for higher BLER than target
        lbler_indices = np.argwhere(bler < bler_target) # Indices for lower BLER than target
        
        if hbler_indices.size == 0: # BLER always less than the target
            snr_at_bler_target[i] = np.min(awgn_snr_range_dB)
        elif lbler_indices.size == 0: # BLER always higher than the target
            snr_at_bler_target[i] = np.max(awgn_snr_range_dB)
        else:
            index1 = np.max(np.argwhere(bler > bler_target)) # Largest SNR index with BLER higher than target
            index2 = np.min(np.argwhere(bler < bler_target)) # Smallest SNR index with BLER lower than target
            snr_at_bler_target[i] = (awgn_snr_range_dB[index1] + awgn_snr_range_dB[index2]) / 2.0
            
    return snr_at_bler_target
        
def calculate_nrof_transmit_bits(modulation_order, nrof_resource_blocks):
    nrof_subcarriers = CONFIG.SUBCARRIERS_PER_PRB * nrof_resource_blocks
    nrof_resource_elements = CONFIG.NROF_OFDM_SYMBOLS_PER_SUBFRAME * nrof_subcarriers
    
    return (nrof_resource_elements * modulation_order)

''' Returns the modulation order and transport block size for the given
    channel quality index, where the channel code rate is x1024.
'''
def get_transmission_parameters_from_cqi(cqi, nrof_resource_blocks, offset=0, adaptive_tbs=False):        

    # Handle the outage scenario if reported CQI is 0
    if (cqi == 0):
        modulation_order = 0
        transport_block_size = 0
        return (modulation_order, transport_block_size)
        
    modulation_order, cqi_rate = CONFIG.CQI_INDEX__MODORDER_RATE[cqi]
    
    # Find the rate for all valid TBS sizes
    valid_tbs = CONFIG.VALID_TBS[nrof_resource_blocks]
    
    nrof_data_symbols = nrof_resource_blocks * CONFIG.NROF_SUBCARRIERS_PER_PRB * CONFIG.NROF_DATA_SYMBOLS_PER_SUBFRAME
    valid_rates = [CONFIG.CQI_RATE_MULTIPLIER * tbs / (modulation_order * nrof_data_symbols) for tbs in valid_tbs]
    
    # Find the index of the valid rate closest to the CQI rate
    rate_difference = [abs(rate - cqi_rate) for rate in valid_rates]
    
    # Find the index of the minimum rate difference; this is the required TBS index
    tbs_index = rate_difference.index(min(rate_difference))

    tbs_index = tbs_index + offset    
    if tbs_index < 0:
        tbs_index = 0
    elif tbs_index >= len(valid_tbs):
        tbs_index = len(valid_tbs) - 1
        
    transport_block_size = CONFIG.VALID_TBS[nrof_resource_blocks][tbs_index]
        
#         if transport_block_size < 0:
#             transport_block_size = 0
        
    return (modulation_order, transport_block_size)

'''
'''
def calculate_wideband_channel_quality_index(channel_coefficients, noise_variance, snr_at_bler_target):
    
    nrof_cqi = snr_at_bler_target.length()
    
    eesm_dB = pyp.vec(nrof_cqi)
    eesm_beta = pyp.ones(nrof_cqi)#[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    snr_per_subcarrier = pyp.math.pow(pyp.math.abs(channel_coefficients), 2) * (1.0 / noise_variance)
   
    for i in range(nrof_cqi):
        v = pyp.math.exp(-1.0 * snr_per_subcarrier / eesm_beta[i])
        eesm_value = -1.0 * eesm_beta[i] * pyp.math.log(pyp.stat.mean(v))  
        eesm_dB[i] = pyp.math.dB(eesm_value)

    # Find the largest CQI that has BLER less than the BLER target
    # The CQIs are evaluated in decreasing order and first value that predicts a BLER < 0.1
    # is returned.
    for i in range(nrof_cqi):
        current_cqi = nrof_cqi - i - 1
        if snr_at_bler_target[current_cqi] < eesm_dB[current_cqi]:
            return current_cqi
        else:
            continue

    return 0 # No valid CQI found

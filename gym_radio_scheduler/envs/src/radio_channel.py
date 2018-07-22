import py_itpp as pyp
from src.CONSTANTS import CUSTOM_SYSTEM_CONFIG as CONFIG

''' Create an instance of the channel
'''
def setup_fading_channel(channel_spec, relative_speed):
    sampling_interval = CONFIG.SAMPLING_INTERVAL

    channel = pyp.comm.TDL_Channel(channel_spec, sampling_interval)

    # Maximum Doppler frequency assuming a 2Ghz carrier
    doppler_frequency = (CONFIG.CARRIER_FREQUENCY / 3e8) * relative_speed
    
    norm_doppler = doppler_frequency * CONFIG.SAMPLING_INTERVAL
    channel.set_norm_doppler(norm_doppler)
    
    return channel

''' Obtain the complex-values channel coefficients in the frequency domain, for the given subframe index.
    This method generates the channel impulse response with a time offset for the given subframe index,
    and calculates the frequency domain coefficients from the channel impulse response.
'''
def calculate_channel_frequency_response(channel, subframe_index, nrof_resource_blocks=CONFIG.NROF_TOTAL_PRBS):
    channel_impulse_response = pyp.cmat() 
    channel_frequency_response = pyp.cmat()

    nrof_offset_samples = int(subframe_index * CONFIG.SUBFRAME_DURATION / CONFIG.SAMPLING_INTERVAL)
    channel.set_time_offset(nrof_offset_samples)
    
    # Generate channel samples. Each channel sample is shifted by the transmission duration
    channel.generate(1, channel_impulse_response)
    
    channel.calc_frequency_response(channel_impulse_response, channel_frequency_response, CONFIG.SUBCARRIERS_PER_PRB * nrof_resource_blocks)
    
    channel_coefficients = channel_frequency_response.get_col(0)
    
    return channel_coefficients


def propagate_transmit_bits_over_channel(transmit_bits, modulation_order, nrof_resource_blocks, channel_coefficients, noise_variance):
    nrof_constellation_symbols = int(pyp.math.pow2(modulation_order))
    modulator = pyp.comm.QAM(nrof_constellation_symbols)
        
    nrof_subcarriers = nrof_resource_blocks * CONFIG.SUBCARRIERS_PER_PRB
    nrof_symbols = CONFIG.NROF_OFDM_SYMBOLS_PER_SUBFRAME
    
    modulated_symbols = modulator.modulate_bits(transmit_bits)
        
    if (modulated_symbols.length() != nrof_subcarriers * nrof_symbols):
        print('Mismatched number of modulated symbols: %d and resource elements: %d'%(modulated_symbols.length(), nrof_subcarriers * nrof_symbols))
    
    ofdm_symbols = pyp.cmat(nrof_subcarriers, nrof_symbols)
    for i in range(nrof_symbols):
        temp = modulated_symbols.mid(i * nrof_subcarriers, nrof_subcarriers)
        ofdm_symbols.set_col(i, pyp.signal.ifft(temp, nrof_subcarriers))#.left(nrof_subcarriers))
    
    noise = pyp.randn_c(nrof_subcarriers, nrof_symbols) * (0.5 * pyp.math.sqrt(noise_variance))
    
    block_channel_coefficients = pyp.repmat(channel_coefficients, 1, nrof_symbols, True)
    received_symbols = pyp.elem_mult_mat(ofdm_symbols, block_channel_coefficients) + noise
    
    compensated_symbols = pyp.elem_div_mat(received_symbols, block_channel_coefficients)
    
    # Receiver processing
    demultiplexed_symbols = pyp.cvec(nrof_subcarriers * nrof_symbols)
    for i in range(nrof_symbols):
        temp = compensated_symbols.get_col(i)
        demultiplexed_symbols.set_subvector(i * nrof_subcarriers, pyp.signal.fft(temp, nrof_subcarriers))#.left(nrof_subcarriers))
            
#    receive_soft_values = modulator.demodulate_soft_bits(demultiplexed_symbols, channel_coefficients, noise_variance, pyp.comm.Soft_Method.LOGMAP)
    receive_soft_values = modulator.demodulate_soft_bits(demultiplexed_symbols, noise_variance, pyp.comm.Soft_Method.LOGMAP)
    
    return receive_soft_values

import os
import py_itpp as pyp
from .src import *

class RadioMultilinkScheduler():
    nrof_bits_in_packet = 1000000 # bits
    nrof_max_harq_transmissions = 4
    relative_speed = 0.83 # m/s
    bler_target = 0.1
    channel_profile = pyp.comm.CHANNEL_PROFILE.ITU_Vehicular_B
    
    def __init__(self, 
                 nrof_ues, 
                 scheduler_type, 
                 prop_fair_window_size=50, 
                 cqi_reporting_interval=1,
                 seed=42):

        self.nrof_ues = nrof_ues
        self.scheduler_type = scheduler_type
        self.prop_fair_window_size = prop_fair_window_size
        self.cqi_reporting_interval = cqi_reporting_interval
        self.subframe_index = 0
         
        dirpath = os.path.dirname(os.path.abspath(__file__))
        awgn_datafile = dirpath + '/sim_data/awgn_custom_config_datafile.npy'
        awgn_data = load_from_file(awgn_datafile, encoding='latin1')
        self.snr_at_bler_target = determine_snr_at_bler_target(awgn_data, self.bler_target)

        # Setup variables used to maintain state during the simulation
        self.state = self._setup_state_variables(nrof_ues)

        # Set the random number generator seed for repeatability
        pyp.RNG_reset(seed)

        # Update the UE-level parameters for each UE
        ue_snr_dB = [pyp.random.I_Uniform_RNG(min=10, max=20).sample() for _ in range(nrof_ues)]
        self.ue_noise_variance = [10 ** (-snr * 0.1) for snr in ue_snr_dB]

        # Setup radio channel for each UE
        channel_spec = pyp.comm.Channel_Specification(self.channel_profile)
        self.channel = [setup_fading_channel(channel_spec, self.relative_speed) for _ in range(nrof_ues)]

    def _setup_state_variables(self, nrof_ues):
        # Define a dict to store statistics related to scheduler
        state = {}
        state['previous_scheduled_subframe'] = [-1 for ue_index in range(nrof_ues)]
        state['current_data_buffer_index']   = [0 for ue_index in range(nrof_ues)]
        state['next_data_buffer_index']      = [0 for ue_index in range(nrof_ues)]
        state['cqi']                         = [0 for ue_index in range(nrof_ues)]
        state['harq_transmission_index']     = [0 for ue_index in range(nrof_ues)]
        state['current_harq_buffer_index']   = [0 for ue_index in range(nrof_ues)]
        state['next_harq_buffer_index']      = [0 for ue_index in range(nrof_ues)]
        state['scheduling_grant']            = [{} for ue_index in range(nrof_ues)]
        
        state['transmit_data_buffer']        = [pyp.randb(self.nrof_bits_in_packet) for ue_index in range(nrof_ues)] # IP packet bits
        state['transmit_harq_buffer']        = [pyp.bvec() for ue_index in range(nrof_ues)] # Transmit bits before modulation 
        state['receive_harq_buffer']         = [pyp.vec() for ue_index in range(nrof_ues)]  # Receive soft value after demodulation
        
        state['scheduled_ue'] = 0 
        
        state['subframe_throughput']      = [pyp.ivec(self.prop_fair_window_size) for ue_index in range(nrof_ues)]
        state['interleaver_sequence']     = [pyp.ivec() for ue_index in range(nrof_ues)]
        state['transport_bits']           = [pyp.ivec() for ue_index in range(nrof_ues)]

        return state
        
    # Simulate
    def transmit(self, scheduled_ue_index=-1):
        state = self.state
        nrof_ues = self.nrof_ues
        sf_index = self.subframe_index

        # Obtain the channel for each UE (frequency-domain complex channel coefficients) and update CQI. 
        channel_coefficients = []
        for ue_index in range(nrof_ues):
            channel_coefficients.append(calculate_channel_frequency_response(self.channel[ue_index], sf_index))
            
            #  Update the channel quality index (CQI) state at reporting intervals
            if (sf_index % self.cqi_reporting_interval) == 0:
                # Calculate the wideband CQI assuming perfect channel knowledge
                cqi = calculate_wideband_channel_quality_index(channel_coefficients[ue_index], self.ue_noise_variance[ue_index], self.snr_at_bler_target)
                state['cqi'][ue_index] = cqi
                
            # Update the HARQ transmission state 
            if (state['harq_transmission_index'][ue_index] == self.nrof_max_harq_transmissions):
#                print('Encountered HARQ failure for UE %d in Subframe %d'%(ue_index, subframe_index))
                state['harq_transmission_index'][ue_index] = 0
        
        # Determine the UE scheduled in this frame if not specified.
        if scheduled_ue_index == -1:
            if self.scheduler_type == 'Random':
                scheduled_ue_index = pyp.randi(0, nrof_ues - 1)
            elif self.scheduler_type == 'RoundRobin':
                scheduled_ue_index = self.subframe_index % nrof_ues
            elif self.scheduler_type == 'MaxRate':
                cqi = [state['cqi'][ue_index] for ue_index in range(nrof_ues)]
                scheduled_ue_index = cqi.index(max(cqi))
            elif self.scheduler_type == 'PropFair':
                window_size = self.prop_fair_window_size
                if self.subframe_index < window_size: # Not enough data, perform round robin scheduling
                    scheduled_ue_index = self.subframe_index % nrof_ues
                else:
                    proportional_rate = []
                    for ue_index in range(nrof_ues):
                        cqi = state['cqi'][ue_index]
                        _, transport_block_size = get_transmission_parameters_from_cqi(cqi, 1)
                        instant_rate = transport_block_size * 1e3
                        
                        tputs = state['subframe_throughput'][ue_index]
                        average_rate = pyp.stat.mean(tputs)
                        
                        if average_rate == 0:
                            proportional_rate.append(1e12)
                        else:
                            proportional_rate.append(instant_rate / average_rate)
                        
                    scheduled_ue_index = proportional_rate.index(max(proportional_rate))
            else:
                print('Error: Unsupported scheduler type %s'%(scheduler_type))
            
        # Determine the grant for the scheduled UE
        scheduled_ue_grant = state['scheduling_grant'][scheduled_ue_index]

        cqi = state['cqi'][scheduled_ue_index]
        print('Subframe %d, Scheduled UE: %d, CQI: %d, HARQ Transmission Index %d'%(self.subframe_index, scheduled_ue_index, cqi, state['harq_transmission_index'][scheduled_ue_index]))

        # If the HARQ transmission index is 0, schedule a new grant
        if (state['harq_transmission_index'][scheduled_ue_index] == 0): # Get a new transport block
            
            scheduled_ue_grant['start_resource_block'] = 0
            scheduled_ue_grant['nrof_resource_blocks'] = 1
            
            # Transmit a few bits based on the CQI
            (modulation_order, transport_block_size) = get_transmission_parameters_from_cqi(cqi, scheduled_ue_grant['nrof_resource_blocks'])
            
            scheduled_ue_grant['modulation_order'] = modulation_order
            scheduled_ue_grant['transport_block_size'] = transport_block_size
                
            if transport_block_size == 0:
                print ('Out of range, skipping!')
                tput = 0
                state['subframe_throughput'][scheduled_ue_index].shift_left(tput, 1)
     
                self.subframe_index += 1

                return (scheduled_ue_index, cqi, tput)

        # If this is a new HARQ transmission, extract new transport bits and update HARQ buffers
        if (state['harq_transmission_index'][scheduled_ue_index] == 0):
            state['transport_bits'][scheduled_ue_index] = extract_next_bits_with_zero_padding(state['transmit_data_buffer'][scheduled_ue_index], state['current_data_buffer_index'][scheduled_ue_index], transport_block_size)
                    
            state['transmit_harq_buffer'][scheduled_ue_index].clear()
            state['transmit_harq_buffer'][scheduled_ue_index], state['interleaver_sequence'][scheduled_ue_index] = channel_encode_and_interleave_bits(state['transport_bits'][scheduled_ue_index])
            
            state['receive_harq_buffer'][scheduled_ue_index].clear()
            state['receive_harq_buffer'][scheduled_ue_index].set_size(state['transmit_harq_buffer'][scheduled_ue_index].length(), False)
            
        nrof_transmit_bits = calculate_nrof_transmit_bits(scheduled_ue_grant['modulation_order'], scheduled_ue_grant['nrof_resource_blocks'])
            
        transmit_bits = extract_next_bits_with_wraparound(state['transmit_harq_buffer'][scheduled_ue_index], state['current_harq_buffer_index'][scheduled_ue_index], nrof_transmit_bits) 
                    
        state['next_harq_buffer_index'][scheduled_ue_index] = (state['current_harq_buffer_index'][scheduled_ue_index] + transmit_bits.length()) % state['transmit_harq_buffer'][scheduled_ue_index].length()

        noise_variance = self.ue_noise_variance[scheduled_ue_index]
        received_soft_values = propagate_transmit_bits_over_channel(transmit_bits, scheduled_ue_grant['modulation_order'], scheduled_ue_grant['nrof_resource_blocks'], channel_coefficients[scheduled_ue_index], noise_variance)
        
        state['receive_harq_buffer'][scheduled_ue_index] = add_values_with_wraparound(state['receive_harq_buffer'][scheduled_ue_index], state['current_harq_buffer_index'][scheduled_ue_index], received_soft_values)

        decoded_bits = deinterleave_and_channel_decode_symbols(state['receive_harq_buffer'][scheduled_ue_index], state['interleaver_sequence'][scheduled_ue_index])

        if (decoded_bits == state['transport_bits'][scheduled_ue_index]):
            state['harq_transmission_index'][scheduled_ue_index] = 0
            
            tput = scheduled_ue_grant['transport_block_size']
        else:
            state['harq_transmission_index'][scheduled_ue_index] = state['harq_transmission_index'][scheduled_ue_index] + 1
            tput = 0

        state['subframe_throughput'][scheduled_ue_index].shift_left(tput, 1)

        # Increment the subframe index
        self.subframe_index += 1

        return (scheduled_ue_index, cqi, tput)

    # Save Simulation Data
    def save_simulation_data():
        filepath = '../sim_data/DATA_%s_%dUES_%dSF.npy'%(scheduler_type, nrof_ues, nrof_subframes)
        save_simulation_data(filepath, sim['par'], ue, nrof_ues)

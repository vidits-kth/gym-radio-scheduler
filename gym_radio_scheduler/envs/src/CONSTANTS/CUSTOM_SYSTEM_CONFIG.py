''' Abbreviations
    NROF   Number of
    OFDM   Orthogonal Frequency Division Multiplexing
    PRB    Physical Resource Block
    CQI    Channel Quality Index
    FFT    Fast Fourier Transform
    TBS    Transport Block Size
'''
CARRIER_FREQUENCY = 2e9 # Hz

NROF_TOTAL_PRBS = 6
SUBCARRIERS_PER_PRB = 12
NROF_TOTAL_SUBCARRIERS = NROF_TOTAL_PRBS * SUBCARRIERS_PER_PRB
SUBCARRIER_SPACING = 15000 # Hz

FFT_SIZE = 128
SAMPLING_RATE = SUBCARRIER_SPACING * FFT_SIZE # Hz
SAMPLING_INTERVAL = 1.0 / SAMPLING_RATE

SUBFRAME_DURATION = 0.001 # s
NROF_OFDM_SYMBOLS_PER_SUBFRAME = 14
NROF_DATA_SYMBOLS_PER_SUBFRAME = 14
NROF_SUBCARRIERS_PER_PRB = 12
OFDM_SYMBOL_DURATION = SUBFRAME_DURATION / NROF_OFDM_SYMBOLS_PER_SUBFRAME

# TS 36.213 Table 7.1.7.2.1-1: Transport block size table
VALID_TBS = {1: [4 * x for x in range(200)]}
    
# TS 36.213 Table 7.2.3-1
CQI_RATE_MULTIPLIER = 1024
CQI_INDEX__MODORDER_RATE = {0:  (0, 0),
                            1:  (2, 64),
                            2:  (2, 128),
                            3:  (2, 192),
                            4:  (2, 256),
                            5:  (2, 320),
                            6:  (2, 384),
                            7:  (2, 448),
                            8:  (2, 512),
                            9:  (4, 224),
                            10: (4, 288),
                            11: (4, 352),
                            12: (4, 416),
                            13: (4, 480),
                            14: (4, 544),
                            15: (4, 608),
                            16: (6, 416),
                            17: (6, 480),
                            18: (6, 544),
                            19: (6, 608),
                            20: (6, 672),
                            21: (6, 736),
                            22: (6, 800)}

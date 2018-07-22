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
VALID_TBS = {1: [0, 16, 24, 32, 40, 56, 72, 104, 120, 136, 144, 176, 208, 224, 256, 280, 328, 328, 336, 376, 408, 440, 488, 520, 552, 584, 616, 632, 712],
             6: [0, 152, 208, 256, 328, 408, 504, 600, 712, 808, 1032, 1192, 1352, 1544, 1736, 1800, 1928, 2152, 2344, 2600, 2792, 2984, 3240, 3496, 3624, 3752, 4392, 3880]}

ADAPTIVE_TBS = {1: [4 * x for x in range(200)]}
    
# TS 36.213 Table 7.2.3-1
CQI_RATE_MULTIPLIER = 1024
CQI_INDEX__MODORDER_RATE = {0:  (0, 0),
                            1:  (2, 78),
                            2:  (2, 120),
                            3:  (2, 193),
                            4:  (2, 308),
                            5:  (2, 449),
                            6:  (2, 602),
                            7:  (4, 378),
                            8:  (4, 490),
                            9:  (4, 616),
                            10: (6, 466),
                            11: (6, 567),
                            12: (6, 666),
                            13: (6, 772),
                            14: (6, 873),
                            15: (6, 948)}

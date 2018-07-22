import py_itpp as pyp

''' Extract the next few bits from the buffer. If too few bits are available, 
    pad the extracted bits with zeros. 
'''
def extract_next_bits_with_zero_padding(buffer_, index, nrof_bits):
    extracted_bits = pyp.bvec()
    buffer_size = buffer_.length()
    
    if (index + nrof_bits) <= buffer_size:
        extracted_bits = buffer_.mid(index, nrof_bits)
    else:
        extracted_bits = buffer_.mid(index,  buffer_size - index)
        nrof_padding_bits = nrof_bits - extracted_bits.length()
        extracted_bits = pyp.concat(extracted_bits, pyp.zeros_b(nrof_padding_bits))
        
    return extracted_bits

''' Extract the next bits from buffer with wraparound, in effect simulating 
    a circular buffer starting from the provided index.
'''
def extract_next_bits_with_wraparound(buffer_, index, nrof_bits):
    extracted_bits = pyp.bvec()
    buffer_size = buffer_.length()
    
    if (index + nrof_bits) < buffer_size:
        extracted_bits = buffer_.mid(index, nrof_bits)
    else:
        # Get the remaning bits in the buffer
        extracted_bits = pyp.concat(extracted_bits, buffer_.right(buffer_size - index))
        
        # Wrap around the HARQ buffer
        while (extracted_bits.length() < nrof_bits):
            nrof_remaining_bits =  nrof_bits - extracted_bits.length()
            if (nrof_remaining_bits > buffer_size):
                extracted_bits = pyp.concat(extracted_bits, buffer_)
            else:
                extracted_bits = pyp.concat(extracted_bits, buffer_.left(nrof_remaining_bits))

    return extracted_bits

''' Add given values to the buffer starting from index. If there are more values,
    wrap around the buffer and continue adding from start of the buffer.
'''
def add_values_with_wraparound(buffer_, index, values):
    buffer_size = buffer_.length()
    temp_buffer = pyp.zeros(buffer_size)
    
    nrof_values = values.length()
    if (index + nrof_values) < buffer_size:
        temp_buffer.set_subvector(index, values)
    else:
        temp_buffer.set_subvector(index, values.mid(index, buffer_size - index))
        
        value_index = buffer_size - index
        while (value_index < nrof_values):
            if (value_index + buffer_size) < nrof_values:
                temp_buffer = temp_buffer + values.mid(value_index, buffer_size)
                value_index = value_index + buffer_size
            else:
                temp = values.mid(value_index, nrof_values - value_index) + temp_buffer.left(nrof_values - value_index)
                temp_buffer.set_subvector(0, temp)
                value_index = nrof_values
                                
    return (buffer_ + temp_buffer)

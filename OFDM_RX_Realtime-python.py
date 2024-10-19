## Kode Basic OFDM dengan nilai data yang diambil langsung dari hasil encoding transmitter

import numpy as np
import reedsolo

combine_real_of_ofdm = np.array([199, 202, 197, 197, 195, 200, 198, 204, 198, 201, 209, 193, 196, 205, 208, 206, 196, 208, 204, 205, 202, 203, 206, 198, 209, 208, 207, 203, 193, 203, 206, 200, 198, 202, 202, 204, 197, 204, 204, 206, 203, 202, 211, 210, 205, 199, 211, 199, 200, 207, 201, 197, 209, 211, 213, 202, 210, 211, 203, 217, 216, 211, 207, 210, 217, 218, 210, 212, 211, 212, 209, 216, 210, 207, 218, 203, 214, 211, 203, 212, 208, 213, 206, 217, 210, 202, 212, 213, 218, 215, 217, 214, 203, 212, 216, 209, 216, 209, 206, 209, 198, 203, 204, 204, 191, 193, 200, 206, 201, 197, 208, 195, 200, 203, 196, 202, 203, 207, 197, 206, 209, 197, 205, 194, 197, 205, 203, 202, 203, 205, 198, 208, 209, 203, 201, 204, 197, 206, 197, 196, 208, 207, 212, 202, 209, 209, 209, 213, 201, 199, 210, 207, 209, 206, 211, 215, 203, 214, 213, 208, 216, 212, 214, 208, 199, 213, 203, 210, 219, 212, 209, 208, 217, 215, 211, 210, 219, 209, 219, 220, 206, 211, 209, 216, 212, 215, 215, 205, 204, 209, 214, 214])
combine_real_of_ofdm.shape
complex_ofdm = combine_real_of_ofdm + 0j
print("Complex OFDM Symbols:")
print(complex_ofdm)
ofdm_symbols_without_bias = complex_ofdm 
ofdm_symbols_reshaped = ofdm_symbols_without_bias.reshape(-1, 16)
fft_ofdm_symbols = np.fft.fft(ofdm_symbols_reshaped, axis=1)
fft_ofdm_symbols.shape

def reverse_hermitian_symmetry_matrix(hermitian_symmetric_matrix):
    num_rows = hermitian_symmetric_matrix.shape[0]
    qam_symbols_matrix = np.zeros((num_rows, 7), dtype=complex)
    for i in range(num_rows):
        qam_symbols_matrix[i, :] = hermitian_symmetric_matrix[i, 1:8]
    return qam_symbols_matrix

qam_symbols_matrix = reverse_hermitian_symmetry_matrix(fft_ofdm_symbols)
QAM_16 = np.concatenate(qam_symbols_matrix)

def qam4_to_binary(symbols):
    binary_list = []
    for RI in symbols:
        R = np.real(RI)
        I = np.imag(RI)
        if R >= 0 and I >= 0:
            binary_list.append('00')
        elif R < 0 and I >= 0:
            binary_list.append('10')
        elif R < 0 and I < 0:
            binary_list.append('11')
        elif R >= 0 and I < 0:
            binary_list.append('01')
    return binary_list

binary_output = qam4_to_binary(QAM_16)
binary_string = ''.join(binary_output)

def binary_to_bytes(binary_str):
    return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))

def bytes_to_binary(byte_data):
    return ''.join(format(byte, '08b') for byte in byte_data)

n = 15
k = 11
rs = reedsolo.RSCodec(n - k)
binary_bytes = binary_to_bytes(binary_string)
corrupted_bytes = binary_bytes
decoded_tuple = rs.decode(corrupted_bytes)
corrected_message = decoded_tuple[0]
decoded_binary = bytes_to_binary(corrected_message)

def bits_to_string(bits):
    chars = [chr(int(''.join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

corrected_bits = [int(bit) for bit in decoded_binary]
decoded_message = bits_to_string(corrected_bits)
print(f"Decoded message: {decoded_message}")

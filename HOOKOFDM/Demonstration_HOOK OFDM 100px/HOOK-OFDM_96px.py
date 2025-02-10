import cv2
import numpy as np
from pypylon import pylon

# Initialize Pylon camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Configure default resolution and frame rate
camera.Open()
camera.Width.Value = 1920  # Set image width
camera.Height.Value = 1080  # Set image height
camera.AcquisitionFrameRateEnable.SetValue(True)
initial_fps = 3.61  # Default frame rate
camera.AcquisitionFrameRate.SetValue(initial_fps)  # Set default frame rate

# Image Format Converter to convert the image to BGR format compatible with OpenCV
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed  # Convert to 8-bit BGR format
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned  # Bit alignment

# Start capturing video
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Initialize variables
last_printed_row_sums = None
all_value_intensity = []
capturing_data = False
data_captured = False
key_start_threshold = (0, 40)  # Threshold for detecting low intensity values
all_decoded_message = []  # Initialize decoded messages as an empty list
last_decoded_message = []  # Store the last decoded message for comparison

# Create a window with a trackbar to adjust frame rate
cv2.namedWindow("Screen with ROI")

# Main loop to capture and process frames
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Convert image to format compatible with OpenCV (BGR)
        image = converter.Convert(grabResult).GetArray()

        # Define initial coordinates (x1, y1) and the width and height of the bounding box
        x1, y1, width, height = 900, 200, 10, 600  # Monitored area

        # Copy the image and draw a rectangle on it
        rectangle_image = image.copy()
        cv2.rectangle(
            rectangle_image, (x1, y1), (x1 + width, y1 + height), (255, 0, 0), 2
        )

        # Display the original image with the rectangle
        cv2.imshow("Screen with ROI", rectangle_image)

        # Retrieve the intensity values within the ROI (blue channel only)
        row_sums = [
            int(np.sum(row) / width)
            for row in image[y1 : y1 + height, x1 : x1 + width, 2]
        ]

        # Detect when to start capturing data if sufficient low-intensity values are present
        if (
            sum(value <= key_start_threshold[1] for value in row_sums) >= 25
            and not capturing_data
            and not data_captured
        ):
            capturing_data = True
            all_value_intensity = []  # Reset previous intensity data
            print("Start capturing data...")
        
        # print("000000", row_sums)
        # Process captured data if it meets the required conditions (low + data + low)
        if capturing_data and (
            len(row_sums) == 600
            and all(value <= key_start_threshold[1] for value in row_sums[:1])
            and all(value <= key_start_threshold[1] for value in row_sums[-1:])
        ):
            # print("00", row_sums)

            if (
                any(value > key_start_threshold[1] for value in row_sums)
                and row_sums != last_printed_row_sums
            ):
                while len(row_sums) > 0 and row_sums[0] <= key_start_threshold[1]:
                    row_sums.pop(0)

                while len(row_sums) > 0 and row_sums[-1] <= key_start_threshold[1]:
                    row_sums.pop()

                value_intensity = []  # sampai sini aman
                # Print the processed intensity values
                # print("Processed Value Intensity: ", value_intensity)
                # print("01", row_sums)
                # for i in range(3, 598, 6):
                #     pair_avg = int((row_sums[i] + row_sums[i + 1]) / 2)
                #     value_intensity.append(pair_avg)

                # print("01", row_sums)
                # for i in range(3, 598, 6): #100 dta
                for i in range(3, 574, 6): #96
                    pair_avg = int((row_sums[i] + row_sums[i + 1]) / 2)
                    value_intensity.append(pair_avg)
                    
                
                print("Processed Value Intensity: ", value_intensity)
                #sampai sini code nya


                mapping_HOFDM = value_intensity
                mapping = {
                70: (55, 72),
                71: (73, 75),
                72: (76, 78),
                73: (79, 81),
                74: (82, 84),
                75: (85, 87),
                76: (88, 90),
                77: (91, 93),
                78: (94, 96),
                79: (97, 99),
                80: (100, 102),
                81: (103, 105),
                82: (106, 108),
                83: (109, 111),
                84: (112, 114),
                85: (115, 117),
                86 : (118, 120),
                87 : (121, 149),


                200: (150, 172),
                201: (173, 175),
                202: (176, 178),
                203: (179, 181),
                204: (182, 184),
                205: (185, 187),
                206: (188, 190),
                207: (191, 193),
                208: (194, 196),
                209: (197, 199),
                210: (200, 202),
                211: (203, 205),
                212: (206, 208),
                213: (209, 211),
                214: (212, 214),
                215: (215, 217),
                216: (218, 220),
                217: (221, 250),
                }

                # Fungsi untuk membalikkan mapping (reverse mapping) dengan pengecekan rentang
                def reverse_map_value(mapped_value):
                    for key, value_range in mapping.items():
                        if value_range[0] <= mapped_value <= value_range[1]:  # Cek apakah mapped_value berada dalam rentang
                            return key
                    return None
                reversed_values = [reverse_map_value(value) for value in mapping_HOFDM ]
                print(f"reversed_values = {reversed_values}")



                # Hasil untuk data gabungan
                corrected_values = []

                # Proses data per 12 indeks
                for i in range(0, len(reversed_values), 12):
                    # Ambil 12 data sekaligus
                    subset = reversed_values[i:i+12]
                    
                    # Cek jumlah data dalam rentang 60-77
                    count_low = sum(70 <= x <= 87 for x in subset)
                    
                    # Cek jumlah data dalam rentang 200-217
                    count_high = sum(200<= x <= 217 for x in subset)
                    
                    # Perbaiki data
                    if count_low > len(subset) / 2:
                        # Kategori "low" - batas nilai maksimal 77
                        corrected_subset = [min(x, 87) for x in subset]
                    elif count_high > len(subset) / 2:
                        # Kategori "high" - batas nilai minimal 200
                        corrected_subset = [max(x, 200) for x in subset]
                    else:
                        # Jika tidak memenuhi kriteria low atau high, tidak ada perubahan
                        print(f"Warning: Subset {subset} tidak memenuhi kriteria 'low' atau 'high'!")
                        corrected_subset = subset  # Tetap gunakan subset asli jika tidak memenuhi kriteria
                    
                    # Tambahkan ke hasil gabungan
                    corrected_values.extend(corrected_subset)

                # Cetak hasil akhir
                print("Corrected Values:")
                print(corrected_values)


                # Initialize reconstructed data
                reconstructed_OFDM = []
                reconstructed_OOK = []

                # Iterate over Modified OFDM
                for value in reversed_values:
                    if 70 <= value <= 87:
                        reconstructed_OOK.append(0)

                        reconstructed_OFDM.append(value - 70)
                    elif 200 <= value <= 217:
                        reconstructed_OOK.append(1)
                        reconstructed_OFDM.append(value - 200)
                    else:
                        print(f"Warning: Value {value} out of expected range!")

                # Print results
                print("Reconstructed OOK Signal:", reconstructed_OOK)
                print("Reconstructed Pure OFDM Signal:", reconstructed_OFDM)



                # Initialize list for final OOK signal
                final_OOK = []

                # Initialize list for final OOK signal
                final_OOK = []

                # Process data in chunks of 12
                for i in range(0, len(reconstructed_OOK), 12):
                    block = reconstructed_OOK[i:i + 12]  # Extract a block of 12 elements
                    count_1 = block.count(1)  # Count the number of 1s
                    count_0 = block.count(0)  # Count the number of 0s
                    
                    # Determine the majority
                    if count_1 > count_0:
                        final_OOK.append(1)
                    else:
                        final_OOK.append(0)

                # Print the final OOK signal
                print("Final OOK Signal (12-block majority):", final_OOK)



                restored_signal = np.array(reconstructed_OFDM)
                print("combine_real_of_ofdm:", restored_signal)

                # Complex format 
                # Add 0j to convert real numbers to complex numbers
                complex_ofdm = restored_signal + 0j

                # Print the complex array
                print("Complex OFDM Symbols:")
                print(complex_ofdm)


                # Remove DC Bias
                ofdm_symbols_without_bias = complex_ofdm 

                ## perform reshape
                ofdm_symbols_reshaped = ofdm_symbols_without_bias.reshape(-1, 16)
                print(ofdm_symbols_reshaped)



                # Original FFT and QAM recovery

                fft_ofdm_symbols = np.fft.fft(ofdm_symbols_reshaped, axis=1)

                # Print the FFT result for each OFDM symbol
                print("FFT of OFDM Symbols:")
                print(fft_ofdm_symbols)
                print("FFT of OFDM Symbols shape:", fft_ofdm_symbols.shape)

                # Initialize the matrix for storing the QAM symbols
                num_rows = fft_ofdm_symbols.shape[0]  # Get the number of rows
                qam_symbols_matrix = np.zeros((num_rows, 7), dtype=complex)  # Initialize the output array

                # Recover the QAM symbols from the Hermitian-symmetric OFDM symbols
                for i in range(num_rows):
                    # Extract the original QAM symbols from each row
                    qam_symbols_matrix[i, :] = fft_ofdm_symbols[i, 1:8]

                # Print the recovered QAM symbols for each row
                print("QAM after Hermitian:")
                print(qam_symbols_matrix)


                # Concatenate all rows into a single row
                QAM_4 = np.concatenate(qam_symbols_matrix)

                # Print the final QAM symbols
                print("Concatenated QAM symbols:")
                print(QAM_4)

                # Duplicate code: passing values to the second block

                # Store values from the original FFT and QAM recovery
                stored_fft_ofdm_symbols = fft_ofdm_symbols
                stored_qam_symbols_matrix = qam_symbols_matrix
                stored_QAM_4 = QAM_4

                # Second block using the stored values

                # Use stored values for further processing
                print("\nSecond Block Processing using Stored Values")

                # Print the stored FFT result for each OFDM symbol
                print("Stored FFT of OFDM Symbols:")
                print(stored_fft_ofdm_symbols)
                print("Stored FFT of OFDM Symbols shape:", stored_fft_ofdm_symbols.shape)

                # Print the stored recovered QAM symbols for each row
                print("Stored QAM after Hermitian:")
                print(stored_qam_symbols_matrix)

                # Print the stored concatenated QAM symbols
                print("Stored Concatenated QAM symbols:")
                print(stored_QAM_4)




                binary_list = []

                # Proses konversi setiap simbol QAM-4 menjadi biner
                for RI in QAM_4:
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

                # Gabungkan list biner menjadi satu string
                binary_string = ''.join(binary_list)

                # Menampilkan hasil output
                print("Binary Output\n:", binary_list)
                print("Combine:", binary_string)




                import reedsolo

                # # Initialize the Reed-Solomon codec
                n = 15
                k = 11

                # n = 255
                # k = 245


                rs = reedsolo.RSCodec(n - k)
                binary_bytes = bytes(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
                corrupted_bytes = binary_bytes
                decoded_tuple = rs.decode(corrupted_bytes)
                corrected_message = decoded_tuple[0]
                decoded_binary = ''.join(format(byte, '08b') for byte in corrected_message)

                # Menampilkan hasil
                print(f"Original Binary Data:\n {binary_string}")
                print(f"Corrected Binary Data (15,11):\n {decoded_binary}")



                # Convert the bits to the original string without using a function
                corrected_bits = [int(bit) for bit in decoded_binary]

                # Convert each 8-bit chunk into a character
                chars = []
                for i in range(0, len(corrected_bits), 8):
                    byte = corrected_bits[i:i + 8]
                    char = chr(int(''.join(map(str, byte)), 2))
                    chars.append(char)

                # Join the characters to form the decoded message
                decoded_message = ''.join(chars)

                # Get the current date and time
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")

                # Output the decoded message and the current time
                print(f"Decoded message: {decoded_message}")
                print("Date/time:", current_time)



                # # Final OOK
                # final_OOK = [0, 0, 1, 1, 0, 1, 0, 0]

                # Gabungkan bit menjadi string biner
                binary_string = ''.join(map(str, final_OOK))

                # Konversi string biner ke desimal
                decimal_value = int(binary_string, 2)

                # Konversi desimal ke karakter ASCII
                ascii_character = chr(decimal_value)

                # Cetak hasil
                print("Binary String:", binary_string)
                print("Decimal Value:", decimal_value)
                print("ASCII Character:", ascii_character)



# Exit the loop and close resources when the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Release resources and close everything
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()

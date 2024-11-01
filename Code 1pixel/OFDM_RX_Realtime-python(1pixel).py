#Jarak 5 m (AFR =6.80725 fps, Data = 200, Delay= 5s, Gain= 1.22539, Black Level{DN}=2, Gamma=1 )
#Jarak 10 m (AFR =6.80725 fps, Data = 200, Delay= 5s, Gain= 2.09471, Black Level{DN}=3, Gamma=0.8 )

import cv2
import numpy as np
from pypylon import pylon

# Initialize the camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# Set camera parameters
camera.Width.Value = 1920  # Set image width
camera.Height.Value = 1080  # Set image height
camera.AcquisitionFrameRateEnable.SetValue(True)
initial_fps = 6.80725  # Set default frame rate, 6.80715, 6.8072, 6.80725
camera.AcquisitionFrameRate.SetValue(initial_fps)

# Image format converter to convert the image to BGR format compatible with OpenCV
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed  # Convert to 8-bit BGR format
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned  # Bit alignment

# Start capturing video
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

capturing_data = False
key_start_threshold = (0, 50)
all_row_sums = []
captured_arrays = []
last_printed_message = None  # To store the last printed message
all_decoded_message = []
# Main loop to capture and process frames
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult).GetArray()
        x1, y1, width, height = 1590, 565, 12, 1  # Monitored area  #560 #565
        rectangle_image = image.copy()
        # Draw the monitored area on the image
        cv2.rectangle(rectangle_image, (x1, y1), (x1 + width, y1 + height), (255, 0, 0), 2)
        cv2.imshow("Screen with ROI", rectangle_image)

        # Shadow Rectangle
        rectangle_image1 = image.copy()
        x2, y2, width2, height2 = 1590, 500, 12, 150  # Monitored area
        cv2.rectangle(rectangle_image1, (x2, y2), (x2 + width2, y2 + height2), (255, 0, 255), 2)
        cv2.imshow("Screen with ROI", rectangle_image1)

        
        # Calculate row sums
        row_sums = [int(np.sum(row) / width) for row in image[y1:y1 + height, x1:x1 + width, 0]]
        # print(row_sums)
        # Check if the average intensity falls within the key_start_threshold range
        if key_start_threshold[0] <= row_sums[0] <= key_start_threshold[1]:
            capturing_data = True  # Start capturing data after threshold condition is met
            # print(row_sums)
        # Capture and print row sums if capturing_data is True
        if capturing_data:
            all_row_sums.extend(row_sums)

            # Check if the first element is 0, and reset if necessary
            if all_row_sums and all_row_sums[0] == 0:
                captured_arrays.append(all_row_sums.copy())  # Store a copy of current sums
                all_row_sums.clear()  # Reset to start a new array
                # print(row_sums)
            # Filter row sums outside the threshold
            filtered_row_sums = [value for value in all_row_sums if value < key_start_threshold[0] or value > key_start_threshold[1]]
            print("01", filtered_row_sums)
            # Print filtered row sums if their count is a multiple of 200
            if len(filtered_row_sums) % 200 == 0 and len(filtered_row_sums) > 0:
                print("Filtered Row Sums:\n", filtered_row_sums[:-8])
                last_printed_message = filtered_row_sums[:-8]  # Update the last printed message


                import reedsolo

                mapping = {
                    200: (60, 77),  
                    201: (78, 85),
                    202: (86, 93),
                    203: (94, 101),
                    204: (102, 109),
                    205: (110, 117),
                    206: (118, 125),
                    207: (126, 133),
                    208: (134, 141),
                    209: (142, 149),
                    210: (150, 157),
                    211: (158, 165),
                    212: (166, 173),
                    213: (174, 181),
                    214: (182, 189),
                    215: (190, 197),
                    216: (198, 205),
                    217: (206, 250),
                }

                def reverse_map_value(mapped_value):
                    for key, value_range in mapping.items():
                        if value_range[0] <= mapped_value <= value_range[1]:
                            return key
                    return None

                reversed_values = [reverse_map_value(value) for value in last_printed_message]
                print ("reversed_values\n", reversed_values)
                combine_real_of_ofdm = np.array(reversed_values)
                complex_ofdm = combine_real_of_ofdm + 0j
                print ("complex_ofdm\n", complex_ofdm)
                print(f"Complex OFDM Symbols: {complex_ofdm}")
                ofdm_symbols_without_bias = complex_ofdm
                ofdm_symbols_reshaped = ofdm_symbols_without_bias.reshape(-1, 16)
                fft_ofdm_symbols = np.fft.fft(ofdm_symbols_reshaped, axis=1)
                print(f"fft_ofdm_symbols: {fft_ofdm_symbols}")

                def reverse_hermitian_symmetry_matrix(hermitian_symmetric_matrix):
                    num_rows = hermitian_symmetric_matrix.shape[0]
                    qam_symbols_matrix = np.zeros((num_rows, 7), dtype=complex)

                    for i in range(num_rows):
                        qam_symbols_matrix[i, :] = hermitian_symmetric_matrix[
                            i, 1:8
                        ]

                    return qam_symbols_matrix

                qam_symbols_matrix = reverse_hermitian_symmetry_matrix(
                    fft_ofdm_symbols
                )
                QAM_16 = np.concatenate(qam_symbols_matrix)

                def qam4_to_binary(symbols):
                    binary_list = []
                    for RI in symbols:
                        R = np.real(RI)
                        I = np.imag(RI)

                        if R >= 0 and I >= 0:
                            binary_list.append("00")
                        elif R < 0 and I >= 0:
                            binary_list.append("10")
                        elif R < 0 and I < 0:
                            binary_list.append("11")
                        elif R >= 0 and I < 0:
                            binary_list.append("01")

                    return binary_list

                binary_output = qam4_to_binary(QAM_16)
                print("Binary Output:", binary_output)

                binary_string = "".join(binary_output)
                print("Combine:", binary_string)

                def binary_to_bytes(binary_str):
                    return bytes(
                        int(binary_str[i : i + 8], 2)
                        for i in range(0, len(binary_str), 8)
                    )

                def bytes_to_binary(byte_data):
                    return "".join(format(byte, "08b") for byte in byte_data)

                n = 15
                k = 11
                rs = reedsolo.RSCodec(n - k)
                binary_bytes = binary_to_bytes(binary_string)
                corrupted_bytes = binary_bytes

                decoded_tuple = rs.decode(corrupted_bytes)
                corrected_message = decoded_tuple[0]

                decoded_binary = bytes_to_binary(corrected_message)
                
                print(f"Original Binary Data: {binary_string}")
                print(f"Corrected Binary Data using Reed Solomon: {decoded_binary}")

                def bits_to_string(bits):
                    chars = [
                        chr(int("".join(map(str, bits[i : i + 8])), 2))
                        for i in range(0, len(bits), 8)
                    ]
                    return "".join(chars)

                # all_decoded_message = []
                corrected_bits = [int(bit) for bit in decoded_binary]
                decoded_message = bits_to_string(corrected_bits)
                print(f"Decoded message BER: {decoded_message}")
                all_decoded_message.extend(decoded_message)
                print(f"Decoded message extend: {all_decoded_message}")
                print("All Decoded Messages: ", "".join(all_decoded_message))
 
                all_row_sums.clear()  # Reset to only store new data

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    grabResult.Release()

# Stop grabbing and clean up
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()


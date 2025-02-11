import cv2
import numpy as np
from pypylon import pylon
import reedsolo

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
camera.Width.Value = 1920
camera.Height.Value = 1080
camera.AcquisitionFrameRateEnable.SetValue(True)
initial_fps = 3.61
camera.AcquisitionFrameRate.SetValue(initial_fps)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)


last_printed_row_sums1 = None
last_printed_row_sums2 = None
# last_printed_row_sums3 = None

all_value_intensity1 = []
all_value_intensity2 = []
# all_value_intensity3 = []

capturing_data1 = False
capturing_data2 = False
data_captured1 = False
data_captured2 = False
key_start_threshold = (0, 30)


# ROI 1 (Area pertama)
x1, y1, width1, height1 = 600, 200, 15, 600
# ROI 2 (Area kedua)
x2, y2, width2, height2 = 1740, 300, 15, 600


while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult).GetArray()
        rectangle_image = image.copy()

        cv2.rectangle(
            rectangle_image, (x1, y1), (x1 + width1, y1 + height1), (255, 0, 0), 2
        )
        cv2.rectangle(
            rectangle_image, (x2, y2), (x2 + width2, y2 + height2), (0, 255, 0), 2
        )

        cv2.imshow("Screen with ROI", rectangle_image)
        # ROI 1
        row_sums_1 = [
            int(np.sum(row) / width1)
            for row in image[y1 : y1 + height1, x1 : x1 + width1, 0]
        ]
        # ROI 2
        row_sums_2 = [
            int(np.sum(row) / width2)
            for row in image[y2 : y2 + height2, x2 : x2 + width2, 0]
        ]

        # PROCESS ROI1
        if (
            sum(value_1 <= key_start_threshold[1] for value_1 in row_sums_1) >= 25
            and not capturing_data1
            and not data_captured1
        ):
            capturing_data1 = True
            all_value_intensity1 = []  # Reset previous intensity data
        if capturing_data1 and (
            len(row_sums_1) == 600  # 600
            and all(value_1 <= key_start_threshold[1] for value_1 in row_sums_1[:1])
            and all(value_1 <= key_start_threshold[1] for value_1 in row_sums_1[-1:])
        ):

            if (
                any(value_1 > key_start_threshold[1] for value_1 in row_sums_1)
                and row_sums_1 != last_printed_row_sums1
            ):
                while len(row_sums_1) > 0 and row_sums_1[0] <= key_start_threshold[1]:
                    row_sums_1.pop(0)

                while len(row_sums_1) > 0 and row_sums_1[-1] <= key_start_threshold[1]:
                    row_sums_1.pop()

                value_intensity_1 = []
                # print(row_sums_1)
                for i in range(3, 574, 6):
                    pair_avg_1 = int((row_sums_1[i] + row_sums_1[i + 1]) / 2)
                    value_intensity_1.append(pair_avg_1)

                # print("Processed Value Intensity1: ", value_intensity_1)

                mapping_HOFDM_1 = value_intensity_1
                mapping_1 = {
                    70: (30, 72),
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
                    86: (118, 120),
                    87: (121, 149),
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
                    217: (221, 255),
                }

                def reverse_map_value(mapped_value_1):
                    for key, value_range_1 in mapping_1.items():
                        if value_range_1[0] <= mapped_value_1 <= value_range_1[1]:
                            return key
                    return None

                reversed_values_1 = [
                    reverse_map_value(value) for value in mapping_HOFDM_1
                ]
                # print(f"reversed_values1 = {reversed_values_1}")

                corrected_values_1 = []
                for i in range(0, len(reversed_values_1), 12):
                    subset_1 = reversed_values_1[i : i + 12]
                    count_low_1 = sum(70 <= x <= 87 for x in subset_1)
                    count_high_1 = sum(200 <= x <= 217 for x in subset_1)
                    if count_low_1 > len(subset_1) / 2:
                        corrected_subset_1 = [min(x, 87) for x in subset_1]
                    elif count_high_1 > len(subset_1) / 2:
                        corrected_subset_1 = [max(x, 200) for x in subset_1]
                    else:
                        corrected_subset_1 = subset_1
                    corrected_values_1.extend(corrected_subset_1)
                reconstructed_OFDM_1 = []
                reconstructed_OOK_1 = []

                for value_1 in reversed_values_1:
                    if 70 <= value_1 <= 87:
                        reconstructed_OOK_1.append(0)
                        reconstructed_OFDM_1.append(value_1 - 70)
                    elif 200 <= value_1 <= 217:
                        reconstructed_OOK_1.append(1)
                        reconstructed_OFDM_1.append(value_1 - 200)
                    else:
                        print(f"Warning: Value {value_1} out of expected range!")

                final_OOK_1 = []
                for i in range(0, len(reconstructed_OOK_1), 12):
                    block = reconstructed_OOK_1[
                        i : i + 12
                    ]  # Extract a block of 12 elements
                    count_1 = block.count(1)  # Count the number of 1s
                    count_0 = block.count(0)  # Count the number of 0s
                    if count_1 > count_0:
                        final_OOK_1.append(1)
                    else:
                        final_OOK_1.append(0)

                restored_signal_1 = np.array(reconstructed_OFDM_1)
                complex_ofdm_1 = restored_signal_1 + 0j
                ofdm_symbols_without_bias_1 = complex_ofdm_1
                ofdm_symbols_reshaped_1 = ofdm_symbols_without_bias_1.reshape(-1, 16)
                fft_ofdm_symbols_1 = np.fft.fft(ofdm_symbols_reshaped_1, axis=1)
                num_rows_1 = fft_ofdm_symbols_1.shape[0]
                qam_symbols_matrix_1 = np.zeros((num_rows_1, 7), dtype=complex)
                for i in range(num_rows_1):
                    qam_symbols_matrix_1[i, :] = fft_ofdm_symbols_1[i, 1:8]
                QAM_4_1 = np.concatenate(qam_symbols_matrix_1)
                stored_fft_ofdm_symbols_1 = fft_ofdm_symbols_1
                stored_qam_symbols_matrix_1 = qam_symbols_matrix_1
                stored_QAM_4_1 = QAM_4_1
                binary_list_1 = []

                for RI_1 in QAM_4_1:
                    R_1 = np.real(RI_1)
                    I_1 = np.imag(RI_1)

                    if R_1 >= 0 and I_1 >= 0:
                        binary_list_1.append("00")
                    elif R_1 < 0 and I_1 >= 0:
                        binary_list_1.append("10")
                    elif R_1 < 0 and I_1 < 0:
                        binary_list_1.append("11")
                    elif R_1 >= 0 and I_1 < 0:
                        binary_list_1.append("01")
                binary_string_1 = "".join(binary_list_1)

                n_1 = 15
                k_1 = 11
                rs_1 = reedsolo.RSCodec(n_1 - k_1)
                binary_bytes_1 = bytes(
                    int(binary_string_1[i : i + 8], 2)
                    for i in range(0, len(binary_string_1), 8)
                )
                corrupted_bytes_1 = binary_bytes_1
                decoded_tuple_1 = rs_1.decode(corrupted_bytes_1)
                corrected_message_1 = decoded_tuple_1[0]
                decoded_binary_1 = "".join(
                    format(byte, "08b") for byte in corrected_message_1
                )
                corrected_bits_1 = [int(bit_1) for bit_1 in decoded_binary_1]
                chars_1 = []
                for i in range(0, len(corrected_bits_1), 8):
                    byte_1 = corrected_bits_1[i : i + 8]
                    char_1 = chr(int("".join(map(str, byte_1)), 2))
                    chars_1.append(char_1)

                decoded_message_1 = "".join(chars_1)
                from datetime import datetime

                now_1 = datetime.now()
                current_time = now_1.strftime("%Y-%m-%d %H:%M:%S")
                binary_string_1 = "".join(map(str, final_OOK_1))
                decimal_value_1 = int(binary_string_1, 2)
                ascii_character_1 = chr(decimal_value_1)
                print(f"Data link 1: {decoded_message_1}")
                print(f"OOK Data 1: {ascii_character_1}")
                print("\n")

        # PROCESS ROI2
        if (
            sum(value_2 <= key_start_threshold[1] for value_2 in row_sums_2) >= 25
            and not capturing_data2
            and not data_captured1
        ):
            capturing_data2 = True
            all_value_intensity2 = []  # Reset previous intensity data
        if capturing_data2 and (
            len(row_sums_2) == 600  # 600
            and all(value_2 <= key_start_threshold[1] for value_2 in row_sums_2[:1])
            and all(value_2 <= key_start_threshold[1] for value_2 in row_sums_2[-1:])
        ):

            if (
                any(value_2 > key_start_threshold[1] for value_2 in row_sums_2)
                and row_sums_2 != last_printed_row_sums1
            ):
                while len(row_sums_2) > 0 and row_sums_2[0] <= key_start_threshold[1]:
                    row_sums_2.pop(0)

                while len(row_sums_2) > 0 and row_sums_2[-1] <= key_start_threshold[1]:
                    row_sums_2.pop()

                value_intensity_2 = []
                # print(row_sums_2)
                for i in range(3, 574, 6):
                    pair_avg_2 = int((row_sums_2[i] + row_sums_2[i + 1]) / 2)
                    value_intensity_2.append(pair_avg_2)

                # print("Processed Value Intensity2: ", value_intensity_2)

                mapping_HOFDM_2 = value_intensity_2
                mapping_2 = {
                    70: (50, 72),
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
                    86: (118, 120),
                    87: (121, 149),
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

                def reverse_map_value(mapped_value_2):
                    for key, value_range_2 in mapping_2.items():
                        if value_range_2[0] <= mapped_value_2 <= value_range_2[1]:
                            return key
                    return None

                reversed_values_2 = [
                    reverse_map_value(value) for value in mapping_HOFDM_2
                ]
                # print(f"reversed_values2 = {reversed_values_2}")

                corrected_values_2 = []
                for i in range(0, len(reversed_values_2), 12):
                    subset_2 = reversed_values_2[i : i + 12]
                    count_low_2 = sum(70 <= x <= 87 for x in subset_2)
                    count_high_2 = sum(200 <= x <= 217 for x in subset_2)
                    if count_low_2 > len(subset_2) / 2:
                        corrected_subset_2 = [min(x, 87) for x in subset_2]
                    elif count_high_2 > len(subset_2) / 2:
                        corrected_subset_2 = [max(x, 200) for x in subset_2]
                    else:
                        corrected_subset_2 = subset_2
                    corrected_values_2.extend(corrected_subset_2)
                reconstructed_OFDM_2 = []
                reconstructed_OOK_2 = []

                for value_2 in reversed_values_2:
                    if 70 <= value_2 <= 87:
                        reconstructed_OOK_2.append(0)
                        reconstructed_OFDM_2.append(value_2 - 70)
                    elif 200 <= value_2 <= 217:
                        reconstructed_OOK_2.append(1)
                        reconstructed_OFDM_2.append(value_2 - 200)
                    else:
                        print(f"Warning: Value {value_2} out of expected range!")

                final_OOK_2 = []
                for i in range(0, len(reconstructed_OOK_2), 12):
                    block = reconstructed_OOK_2[
                        i : i + 12
                    ]  # Extract a block of 12 elements
                    count_1 = block.count(1)  # Count the number of 1s
                    count_0 = block.count(0)  # Count the number of 0s
                    if count_1 > count_0:
                        final_OOK_2.append(1)
                    else:
                        final_OOK_2.append(0)

                restored_signal_2 = np.array(reconstructed_OFDM_2)
                complex_ofdm_2 = restored_signal_2 + 0j
                ofdm_symbols_without_bias_2 = complex_ofdm_2
                ofdm_symbols_reshaped_2 = ofdm_symbols_without_bias_2.reshape(-1, 16)
                fft_ofdm_symbols_2 = np.fft.fft(ofdm_symbols_reshaped_2, axis=1)
                num_rows_2 = fft_ofdm_symbols_2.shape[0]
                qam_symbols_matrix_2 = np.zeros((num_rows_2, 7), dtype=complex)
                for i in range(num_rows_2):
                    qam_symbols_matrix_2[i, :] = fft_ofdm_symbols_2[i, 1:8]
                QAM_4_2 = np.concatenate(qam_symbols_matrix_2)
                stored_fft_ofdm_symbols_2 = fft_ofdm_symbols_2
                stored_qam_symbols_matrix_2 = qam_symbols_matrix_2
                stored_QAM_4_2 = QAM_4_2
                binary_list_2 = []

                for RI_2 in QAM_4_2:
                    R_2 = np.real(RI_2)
                    I_2 = np.imag(RI_2)

                    if R_2 >= 0 and I_2 >= 0:
                        binary_list_2.append("00")
                    elif R_2 < 0 and I_2 >= 0:
                        binary_list_2.append("10")
                    elif R_2 < 0 and I_2 < 0:
                        binary_list_2.append("11")
                    elif R_2 >= 0 and I_2 < 0:
                        binary_list_2.append("01")
                binary_string_1 = "".join(binary_list_2)

                n_2 = 15
                k_2 = 11
                rs_2 = reedsolo.RSCodec(n_2 - k_2)
                binary_bytes_2 = bytes(
                    int(binary_string_1[i : i + 8], 2)
                    for i in range(0, len(binary_string_1), 8)
                )
                corrupted_bytes_2 = binary_bytes_2
                decoded_tuple_2 = rs_2.decode(corrupted_bytes_2)
                corrected_message_2 = decoded_tuple_2[0]
                decoded_binary_2 = "".join(
                    format(byte, "08b") for byte in corrected_message_2
                )
                corrected_bits_2 = [int(bit_1) for bit_1 in decoded_binary_2]
                chars_2 = []
                for i in range(0, len(corrected_bits_2), 8):
                    byte_2 = corrected_bits_2[i : i + 8]
                    char_2 = chr(int("".join(map(str, byte_2)), 2))
                    chars_2.append(char_2)

                decoded_message_2 = "".join(chars_2)
                from datetime import datetime

                now_2 = datetime.now()
                current_time = now_2.strftime("%Y-%m-%d %H:%M:%S")
                binary_string_2 = "".join(map(str, final_OOK_2))
                decimal_value_2 = int(binary_string_2, 2)
                ascii_character_2 = chr(decimal_value_2)
                print(f"Data link 2: {decoded_message_2}")
                print(f"OOK link 2: {ascii_character_2}")
                print("\n")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()

# PROCESS ROI2

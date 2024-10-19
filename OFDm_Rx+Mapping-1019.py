import cv2
import numpy as np
from pypylon import pylon

# Function to adjust frame rate using a trackbar
# def set_fps(val):
#     global camera
#     fps = val / 3.0  # Divide val to adjust FPS more smoothly
#     camera.AcquisitionFrameRate.SetValue(fps)  # Set FPS on Pylon camera
#     # print(f"Frame rate set to: {fps} FPS")

# Initialize Pylon camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Configure default resolution and frame rate
camera.Open()
camera.Width.Value = 1920  # Set image width
camera.Height.Value = 1080  # Set image height
camera.AcquisitionFrameRateEnable.SetValue(True)
# initial_fps = 9.825  # 8.3 #8.6
initial_fps = 4.54  # 8.3 #8.6

camera.AcquisitionFrameRate.SetValue(initial_fps)  # Default frame rate 8 FPS

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
key_start_threshold = (0, 60)
all_decoded_message = []  # Initialize all_decoded_message as an empty list

# Create a window with a trackbar to adjust frame rate
cv2.namedWindow("Screen with ROI")
# cv2.createTrackbar('FPS', 'Screen with ROI', int(initial_fps * 3), 90, set_fps)  # FPS trackbar with division by 2

# Main loop to capture and process frames
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Convert image to format compatible with OpenCV (BGR)
        image = converter.Convert(grabResult).GetArray()
        # image = cv2.GaussianBlur(image, (11, 11), 5)

        # Define initial coordinates (x1, y1) and the width and height of the bounding box
        x1, y1, width, height = 900, 200, 10, 648  # Monitored area

        # Copy the image and draw a rectangle on it
        rectangle_image = image.copy()
        cv2.rectangle(
            rectangle_image, (x1, y1), (x1 + width, y1 + height), (255, 0, 0), 2
        )

        # Display the original image with the rectangle
        cv2.imshow("Screen with ROI", rectangle_image)

        # Retrieve the intensity values within the ROI (blue channel only)
        # row_sums = [
        #     int(np.sum(row)) for row in image[y1: y1 + height, x1: x1 + width, 2]
        # ]

        row_sums = [
            int(np.sum(row) / width)
            for row in image[y1 : y1 + height, x1 : x1 + width, 2]
        ]

        # Detect when to start capturing data if there are 60 values <= key_start_threshold in row_sums
        if (
            sum(value <= key_start_threshold[1] for value in row_sums) >= 80
            and not capturing_data
            and not data_captured
        ):
            capturing_data = True
            all_value_intensity = []  # Reset previous intensity data
            print("Start capturing data...")

        # New condition: data length must be 624, and the start and end values must be within the key start threshold
        if capturing_data and (
            len(row_sums) == 648
            and all(value <= key_start_threshold[1] for value in row_sums[:1])
            and all(value <= key_start_threshold[1] for value in row_sums[-1:])
        ):
            if (
                any(value > key_start_threshold[1] for value in row_sums)
                and row_sums != last_printed_row_sums
            ):
                while len(row_sums) > 0 and row_sums[0] <= key_start_threshold[1]:
                    row_sums.pop(0)

                while len(row_sums) > 0 and row_sums[-1] <= key_start_threshold[1]:
                    row_sums.pop()

                value_intensity = []

                for i in range(3, 598, 6):
                    pair_avg = int((row_sums[i] + row_sums[i + 1]) / 2)
                    value_intensity.append(pair_avg)

                if value_intensity != last_printed_row_sums:
                    # print("Value Intensity (pair avg): ", value_intensity)
                    all_value_intensity.extend(value_intensity)
                    last_printed_row_sums = value_intensity.copy()

                    data_96 = value_intensity[:-4]  # Take the first 96 elements
                    print("New Value Intensity: ", data_96)  # Print data_96

                    import reedsolo

                    mapping = {
                        200: (65, 77),
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
                        217: (206, 220),
                    }

                    def reverse_map_value(mapped_value):
                        for key, value_range in mapping.items():
                            if value_range[0] <= mapped_value <= value_range[1]:
                                return key
                        return None

                    reversed_values = [reverse_map_value(value) for value in data_96]

                    combine_real_of_ofdm = np.array(reversed_values)
                    complex_ofdm = combine_real_of_ofdm + 0j
                    print(f"Complex OFDM Symbols: {complex_ofdm}")
                    ofdm_symbols_without_bias = complex_ofdm
                    print(f"ofdm_symbols_without_bias: {ofdm_symbols_without_bias}")
                    ofdm_symbols_reshaped = ofdm_symbols_without_bias.reshape(-1, 16)
                    # print(f"ofdm_symbols_reshaped: {ofdm_symbols_reshaped}")
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

                    corrected_bits = [int(bit) for bit in decoded_binary]
                    decoded_message = bits_to_string(corrected_bits)
                    print(f"Decoded message: {decoded_message}")

                    # Add the message to all_decoded_message using extend
                    all_decoded_message.extend(decoded_message)

        # Condition to print "all value intensity" when there are 50 data points <= key_start_threshold in row_sums
        if (
            capturing_data
            and sum(value <= key_start_threshold[1] for value in row_sums) >= 80
            and all_value_intensity
        ):
            print("All Value Intensity: ", all_value_intensity)
            all_value_intensity = []  # Reset after printing

            # Print all decoded messages
            print("All Decoded Messages: ", "".join(all_decoded_message))
            all_decoded_message = []  # Reset after printing

            capturing_data = False  # Done capturing data
            data_captured = True  # Mark that data has been captured
            print("Done capturing data...")

        # Prevent immediate data capture after the process finishes, provide a transition time
        if data_captured:
            data_captured = False  # Reset after one frame to ensure time between captures

        # Wait for 'q' key input to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    grabResult.Release()

# Close all OpenCV windows and the camera
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
# Real time

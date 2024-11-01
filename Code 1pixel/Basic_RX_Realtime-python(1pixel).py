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
last_printed_row_sums = None
last_printed_message = None  # To store the last printed message

# Main loop to capture and process frames
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult).GetArray()
        x1, y1, width, height = 1605, 561, 12, 1  # Monitored area  #560 #565
        rectangle_image = image.copy()
        
        # Draw the monitored area on the image
        cv2.rectangle(rectangle_image, (x1, y1), (x1 + width, y1 + height), (255, 0, 0), 2)
        cv2.imshow("Screen with ROI", rectangle_image)
        
        # Calculate row sums
        row_sums = [int(np.sum(row) / width) for row in image[y1:y1 + height, x1:x1 + width, 0]]
        
        # Check if the average intensity falls within the key_start_threshold range
        if key_start_threshold[0] <= row_sums[0] <= key_start_threshold[1]:
            capturing_data = True  # Start capturing data after threshold condition is met

        # Capture and print row sums if capturing_data is True
        if capturing_data:
            all_row_sums.extend(row_sums)
            
            # Check if the first element is 0, and reset if necessary
            if all_row_sums and all_row_sums[0] == 0:
                captured_arrays.append(all_row_sums.copy())  # Store a copy of current sums
                all_row_sums.clear()  # Reset to start a new array

            # Filter row sums outside the threshold
            filtered_row_sums = [value for value in all_row_sums if value < key_start_threshold[0] or value > key_start_threshold[1]]

            # Print filtered row sums if their count is a multiple of 200
            if len(filtered_row_sums) % 200 == 0 and len(filtered_row_sums) > 0:
                # message = str(filtered_row_sums[:-8])  # Remove the last 8 elements
                message = str(filtered_row_sums)  # Remove the last 8 elements
                print("message\n", message)

                # Check if message is the same as the last printed message
                if message != last_printed_message:
                    print("Filtered Row Sums:\n", message)
                    last_printed_message = message  # Update the last printed message
                    message = ""  # Reset the message after printing


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    grabResult.Release()

# Stop grabbing and clean up
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()

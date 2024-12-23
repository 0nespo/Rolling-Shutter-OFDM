# Rolling-Shutter-OFDM
Code for OCC OFDM


How to run the OFDM:

- Start with the code on the transmitter (tx) side, and copy the output data from the "# Mapping dictionary" section, as the mapping dictionary is the part of the code that connects with the receiver (rx) side.
- We don't directly use the value after performing the (x + 200) operation because the data obtained in a real system is not predictable.
- Instead of using the unpredictable data from x + 200, we perform the mapping again. For example, 200: 73, 201: 81, etc. This means that the data value 200 will be mapped to 73, and the range for 73 will be (200: 65, 77). This happens because, during implementation, we determine the range from the start pixel to the end pixel, where the intensity difference is around 9. Thus, the other data points will be mapped as follows:
  - 201: (78, 85),
  - 202: (86, 93), and so on.

after that, in the reciever side.
we running the code that contain the 2nd mapping (200: 73, 201: 81, ...), so our data can be decoded based on the pixel that we use 


Note.
Kode OFDM = OFDm_Rx+Mapping-1019.py, menggunakan x1, y1, width, height = 900, 200, 10, 648  # Monitored area == 648 pixel, untuk jarak dekat
- kemudian untuk OFDM, data yang dikirim adalah 200 bit, 92+8+92+8 => 92+92 adalah bit asli yang kemudian akan digunakan untuk dikonversi ke ASCII

kode HOOK-OFDM = OFDM-15meter(good Value).py, menggunakan x1, y1, width, height = 980, 500, 12, 1  # Monitored area  == 1 pixel, untuk jarak jauh
- Kemudian untuk HOOK-OFDM, data yang dikirim adalah 200 bit, 192+9 => 8 bit akan dihapus dan 192 bit adalah bit asli yang akan dikonversi ke ASCII




  

// Array of values
int values[] ={119, 144, 191, 129, 119, 93, 119, 180, 155, 155, 119, 68, 155, 155, 119, 170, 191, 155, 83, 119, 119, 155, 155, 119, 155, 104, 119, 119, 155, 206, 119, 119, 155, 144, 155, 180, 83, 93, 155, 129, 155, 206, 119, 119, 155, 104, 119, 119, 155, 129, 155, 93, 83, 180, 155, 144, 155, 68, 119, 155, 155, 170, 119, 155, 119, 170, 155, 155, 119, 68, 155, 155, 119, 155, 155, 119, 191, 155, 83, 119, 119, 170, 155, 155, 119, 68, 155, 155, 119, 129, 191, 144, 119, 180, 119, 93, 155, 170, 119, 155, 155, 68, 119, 155, 155, 93, 155, 180, 155, 144, 83, 129, 83, 144, 155, 180, 155, 93, 155, 129, 83, 155, 119, 119, 155, 155, 191, 119};

int ledPin = 9; // PWM pin (can be 3, 5, 6, 9, 10, or 11 depending on your Arduino)

void setup() {
  // Set LED pin as output
  pinMode(ledPin, OUTPUT);

  // Set the Timer 1 to 16kHz
  TCCR1B = (TCCR1B & 0b11111000) | 0x01;  // Set prescaler to 1, 16 MHz / 1 = 16kHz
}

void loop() {
  // Iterate over the values array
  for (int i = 0; i < sizeof(values) / sizeof(values[0]); i++) {
    
    analogWrite(ledPin, values[i]); // Write PWM value to LED
     // Small delay between updates
    delayMicroseconds(70);

    // Turn off the LED after the loop
    analogWrite(ledPin, 0);  // Set LED brightness to 0 (off)
    // Delay to ensure the LED remains off for a bit before restarting (optional)
    delayMicroseconds(35);
    // delay(1000);
    
  }

  // Turn off the LED after the loop
  analogWrite(ledPin, 0);  // Set LED brightness to 0 (off)

  // Delay to ensure the LED remains off for a bit before restarting (optional)
  delayMicroseconds(700);
  // delay(1000);
}

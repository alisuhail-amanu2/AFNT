#include <SPI.h>
#include <STBLE.h>

#ifndef BLE_DEBUG
#define BLE_DEBUG true
#endif

#if defined (ARDUINO_ARCH_AVR)
#define SerialMonitorInterface Serial
#elif defined(ARDUINO_ARCH_SAMD)
#define SerialMonitorInterface SerialUSB
#endif

uint8_t ble_rx_buffer[21]; // Buffer to store received data.
uint8_t ble_rx_buffer_len = 0; // Length of received data buffer.
uint8_t ble_connection_state = false; // Bluetooth connection state.
#define PIPE_UART_OVER_BTLE_UART_TX_TX 0

void setup() {
  SerialMonitorInterface.begin(9600); // Initialize serial communication with specified baud rate.
  while (!SerialMonitorInterface); // Wait until a serial monitor is opened.
  BLEsetup(); // Initialize Bluetooth Low Energy setup.
}

void loop() {
  aci_loop(); // Process any ACI (Application Control Interface) commands or events from the NRF8001 (Bluetooth module).
  
  if (ble_rx_buffer_len) { // Check if data is available in the receive buffer.
    SerialMonitorInterface.print(ble_rx_buffer_len); // Print the length of received data.
    SerialMonitorInterface.print(" : ");
    SerialMonitorInterface.println((char*)ble_rx_buffer); // Print the received data.
    ble_rx_buffer_len = 0; // Clear the receive buffer after reading.
  }
  
  if (SerialMonitorInterface.available()) { // Check if serial input is available to send.
    delay(10); // Delay to catch input.
    uint8_t sendBuffer[21];
    uint8_t sendLength = 0;
    
    while (SerialMonitorInterface.available() && sendLength < 19) { // Read serial input into sendBuffer.
      sendBuffer[sendLength] = SerialMonitorInterface.read();
      sendLength++;
    }
    
    if (SerialMonitorInterface.available()) { // Check if more data is available (input truncated).
      SerialMonitorInterface.print(F("Input truncated, dropped: "));
      if (SerialMonitorInterface.available()) {
        SerialMonitorInterface.write(SerialMonitorInterface.read()); // Drop excess input characters.
      }
    }
    
    sendBuffer[sendLength] = '\0'; // Terminate string.
    sendLength++;
    
    if (!lib_aci_send_data(PIPE_UART_OVER_BTLE_UART_TX_TX, (uint8_t*)sendBuffer, sendLength)) { // Send data over Bluetooth.
      SerialMonitorInterface.println(F("TX dropped!")); // Print message if data transmission fails.
    }
  }
}

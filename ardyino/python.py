import serial
import pyautogui
import time

# --- CHANGE 'COM3' TO YOUR ARDUINO PORT ---
arduino_port = 'COM3' 
baud_rate = 115200

ser = serial.Serial(arduino_port, baud_rate)
print(f"Connected to {arduino_port}!")
print("Waiting for you to click on the game window...")

while True:
    if ser.in_waiting > 0:
        # Read the sensor
        line = ser.readline().decode('utf-8').strip()
        
        # --- LEFT / RIGHT ---
        if line == "A":
            pyautogui.press('left')
            print("<- Swiped LEFT")
            time.sleep(0.3)  
            ser.reset_input_buffer() 
            
        elif line == "D":
            pyautogui.press('right')
            print("Swiped RIGHT ->")
            time.sleep(0.3)  
            ser.reset_input_buffer()

        # --- UP / DOWN ---
        elif line == "W":
            pyautogui.press('up')
            print("^ Jumped UP")
            time.sleep(0.3)  
            ser.reset_input_buffer()
            
        elif line == "S":
            pyautogui.press('down')
            print("v Rolled DOWN")
            time.sleep(0.3)  
            ser.reset_input_buffer()
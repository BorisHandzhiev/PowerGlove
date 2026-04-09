import serial
import time
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key

# --- Configuration ---
COM_PORT = 'COM3'  # Make sure this matches your RECEIVER Arduino's port
BAUD_RATE = 115200

JOYSTICK_LOWER = 400
JOYSTICK_UPPER = 600
GYRO_DEADZONE = 0.15      
MOUSE_SENSITIVITY = 15.0  

mouse = MouseController()
keyboard = KeyboardController()

# State tracking dictionaries
key_states = {'w': False, 'a': False, 's': False, 'd': False}

glove_button_states = {
    'index': False,
    'middle': False,
    'ring': False,
    'pinky': False,
    'joyClick': False
}

def update_keyboard(key, should_be_pressed):
    is_pressed = key_states.get(key, False)
    if should_be_pressed and not is_pressed:
        keyboard.press(key)
        key_states[key] = True
    elif not should_be_pressed and is_pressed:
        keyboard.release(key)
        key_states[key] = False

def update_mouse_button(btn_name, mouse_button, should_be_pressed):
    is_pressed = glove_button_states[btn_name]
    if should_be_pressed and not is_pressed:
        mouse.press(mouse_button)
        glove_button_states[btn_name] = True
    elif not should_be_pressed and is_pressed:
        mouse.release(mouse_button)
        glove_button_states[btn_name] = False

def main():
    try:
        arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Connected to Dongle on {COM_PORT}. Wireless Glove active!")
        
        while True:
            if arduino.in_waiting > 0:
                raw_data = arduino.readline().decode('utf-8').strip()
                if not raw_data or "Error" in raw_data: continue
                
                data_list = raw_data.split(',')
                
                # We are now looking for exactly 9 values from the Receiver
                if len(data_list) == 9:
                    try:
                        joyX = int(data_list[0])
                        joyY = int(data_list[1])
                        gyroX = float(data_list[2])
                        gyroY = float(data_list[3])
                        
                        btnIndex = int(data_list[4]) == 1
                        btnMiddle = int(data_list[5]) == 1
                        btnRing = int(data_list[6]) == 1
                        btnPinky = int(data_list[7]) == 1
                        btnJoyClick = int(data_list[8]) == 1 
                        
                        # 1. JOYSTICK (WASD)
                        update_keyboard('w', joyX < JOYSTICK_LOWER)
                        update_keyboard('s', joyX > JOYSTICK_UPPER)
                        update_keyboard('d', joyY < JOYSTICK_LOWER)
                        update_keyboard('a', joyY > JOYSTICK_UPPER)

                        # 2. GYRO (MOUSE MOVEMENT)
                        move_x, move_y = 0, 0
                        if abs(gyroX) > GYRO_DEADZONE: move_x = gyroX * MOUSE_SENSITIVITY
                        if abs(gyroY) > GYRO_DEADZONE: move_y = gyroY * MOUSE_SENSITIVITY
                        if move_x != 0 or move_y != 0:
                            mouse.move(int(-move_x), int(move_y)) 
    
                        # 3. FINGER & JOYSTICK BUTTONS
                        update_mouse_button('index', MouseButton.right, btnIndex)
                        update_mouse_button('middle', MouseButton.left, btnMiddle)
                        update_keyboard(Key.space, btnRing)
                        update_keyboard('e', btnPinky)
                        update_keyboard(Key.ctrl_l, btnJoyClick)

                    except ValueError:
                        pass 

    except serial.SerialException as e:
        print(f"Connection error: {e}")
    except KeyboardInterrupt:
        print("\nReleasing keys and closing...")
    finally:
        for k in key_states:
            if key_states[k]: keyboard.release(k)
        for b_name, b_val in zip(['index', 'middle'], [MouseButton.left, MouseButton.right]):
            if glove_button_states[b_name]: mouse.release(b_val)
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()

if __name__ == '__main__':
    main()
import serial
import time
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key

# --- Configuration ---
COM_PORT = 'COM8'  # Update this!
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
    'joyClick': False # NEW Tracker
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
        print(f"Connected to {COM_PORT}. Glove active!")
        
        while True:
            if arduino.in_waiting > 0:
                raw_data = arduino.readline().decode('utf-8').strip()
                if not raw_data or "Error" in raw_data: continue
                
                data_list = raw_data.split(',')
                
                # Now looking for 13 values!
                if len(data_list) == 13:
                    try:
                        joyX = int(data_list[0])
                        joyY = int(data_list[1])
                        gyroX = float(data_list[5])
                        gyroY = float(data_list[6])
                        
                        # Buttons (1 = Pressed, 0 = Released)
                        btnIndex = int(data_list[8]) == 1
                        btnMiddle = int(data_list[9]) == 1
                        btnRing = int(data_list[10]) == 1
                        btnPinky = int(data_list[11]) == 1
                        btnJoyClick = int(data_list[12]) == 1 # NEW Joystick Click
                        
                        # 1. JOYSTICK (WASD)
                        update_keyboard('a', joyX < JOYSTICK_LOWER)
                        update_keyboard('d', joyX > JOYSTICK_UPPER)
                        update_keyboard('w', joyY < JOYSTICK_LOWER)
                        update_keyboard('s', joyY > JOYSTICK_UPPER)

                        # 2. GYRO (MOUSE MOVEMENT)
                        move_x, move_y = 0, 0
                        if abs(gyroX) > GYRO_DEADZONE: move_x = gyroX * MOUSE_SENSITIVITY
                        if abs(gyroY) > GYRO_DEADZONE: move_y = gyroY * MOUSE_SENSITIVITY
                        if move_x != 0 or move_y != 0:
                            mouse.move(int(-move_x), int(-move_y)) 

                        # 3. FINGER & JOYSTICK BUTTONS
                        # Index -> Left Click
                        update_mouse_button('index', MouseButton.left, btnIndex)
                        
                        # Middle -> Right Click
                        update_mouse_button('middle', MouseButton.right, btnMiddle)
                        
                        # Ring -> Spacebar (Jump)
                        update_keyboard(Key.space, btnRing)
                        
                        # Pinky -> 'I' (Interact) - UPDATED!
                        update_keyboard('i', btnPinky)
                        
                        # Joystick Click -> Left Control (Crouch) - NEW!
                        # (Change 'Key.ctrl_l' to 'c' if your game uses C to crouch)
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
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
MOUSE_SENSITIVITY = 10

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

# --- Default Key Bindings ---
ring_key_bind = Key.space
pinky_key_bind = 'e'

def parse_key_input(input_str):
    """Converts user text into a pynput Key object or character."""
    input_str = input_str.strip().lower()
    
    # Dictionary of special keys
    special_keys = {
        'space': Key.space,
        'shift': Key.shift,
        'ctrl': Key.ctrl_l,
        'alt': Key.alt_l,
        'enter': Key.enter,
        'tab': Key.tab,
        'esc': Key.esc,
        'backspace': Key.backspace
    }
    
    if input_str in special_keys:
        return special_keys[input_str]
    elif len(input_str) > 0:
        return input_str[0] 
    return None

def run_startup_menu():
    """Shows a CLI menu to assign keys before the glove starts."""
    global ring_key_bind, pinky_key_bind
    
    print("\n" + "="*30)
    print(" 🎮 SMART GLOVE CONFIGURATOR 🎮")
    print("="*30)
    print("1. Start with Defaults (Ring: Space, Pinky: E)")
    print("2. Custom Key Bindings")
    
    choice = input("\nSelect an option (1 or 2): ").strip()
    
    if choice == '2':
        print("\n(Tip: Type a letter like 'r', 'f', 'q', or a special key like 'space', 'shift', 'ctrl')")
        
        # Get Ring Finger Mapping
        ring_input = input("Enter key for RING finger: ")
        parsed_ring = parse_key_input(ring_input)
        if parsed_ring:
            ring_key_bind = parsed_ring
            
        # Get Pinky Finger Mapping
        pinky_input = input("Enter key for PINKY finger: ")
        parsed_pinky = parse_key_input(pinky_input)
        if parsed_pinky:
            pinky_key_bind = parsed_pinky
            
    # Quick visual confirmation
    print("\n--- Current Key Bindings ---")
    ring_display = ring_key_bind.name if isinstance(ring_key_bind, Key) else ring_key_bind
    pinky_display = pinky_key_bind.name if isinstance(pinky_key_bind, Key) else pinky_key_bind
    print(f"Ring Finger  ->  [{ring_display}]")
    print(f"Pinky Finger ->  [{pinky_display}]")
    print("----------------------------\n")

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
    # Run the menu before looking for the Arduino
    run_startup_menu()

    try:
        arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Connected to Dongle on {COM_PORT}. Wireless Glove active!")
        print("Note: Click the Joystick in to pause the camera! Index is Left Click, Middle is Right Click.")
        
        while True:
            if arduino.in_waiting > 0:
                raw_data = arduino.readline().decode('utf-8').strip()
                if not raw_data or "Error" in raw_data: continue
                
                data_list = raw_data.split(',')
                
                if len(data_list) == 9:
                    try:
                        joyX = int(data_list[0])
                        joyY = int(data_list[1])
                        gyroX = float(data_list[2])
                        gyroY = float(data_list[3])
                        
                        btnIndex = int(data_list[5]) == 1
                        btnMiddle = int(data_list[4]) == 1
                        btnRing = int(data_list[6]) == 1
                        btnPinky = int(data_list[7]) == 1
                        btnJoyClick = int(data_list[8]) == 1 
                        
                        # 1. JOYSTICK (WASD)
                        update_keyboard('w', joyX < JOYSTICK_LOWER)
                        update_keyboard('s', joyX > JOYSTICK_UPPER)
                        update_keyboard('d', joyY < JOYSTICK_LOWER)
                        update_keyboard('a', joyY > JOYSTICK_UPPER)

                        # 2. GYRO (MOUSE MOVEMENT) - WITH JOYSTICK CLUTCH
                        move_x, move_y = 0, 0
                        
                        # Only move the camera if the JOYSTICK CLICK is NOT being pressed
                        if not btnJoyClick:  
                            if abs(gyroX) > GYRO_DEADZONE: move_x = gyroY * MOUSE_SENSITIVITY
                            if abs(gyroY) > GYRO_DEADZONE: move_y = -gyroX * MOUSE_SENSITIVITY
                            if move_x != 0 or move_y != 0:
                                mouse.move(int(-move_x), int(move_y)) 
    
                        # 3. FINGER BUTTONS
                        
                        # Pointer is safely Left Click, Middle is safely Right Click
                        update_mouse_button('index', MouseButton.right, btnIndex)
                        update_mouse_button('middle', MouseButton.left, btnMiddle)
                        
                        # Use the dynamically assigned keys from the menu
                        update_keyboard(ring_key_bind, btnRing)
                        update_keyboard(pinky_key_bind, btnPinky)

                    except ValueError:
                        pass 

    except serial.SerialException as e:
        print(f"Connection error: {e}")
    except KeyboardInterrupt:
        print("\nReleasing keys and closing...")
    finally:
        for k in key_states:
            if key_states[k]: keyboard.release(k)
        for b_name, b_val in zip(['index', 'middle'], [MouseButton.right, MouseButton.left]):
            if glove_button_states[b_name]: mouse.release(b_val)
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()

if __name__ == '__main__':
    main()
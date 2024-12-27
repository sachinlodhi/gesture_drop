# This file works on the ASUS laptop and has the only functionality that it can open the minimized window

import pywinctl as wc
import cv2
import subprocess
import subprocess
import pyautogui

import time

def restore_and_maximize_window(window_title):
    """
    Finding window and maximizing it, returning coordinates after maximization
    """
    try:
        # Searching ID
        cmd = f"xdotool search --name '{window_title}'"
        window_id = subprocess.check_output(cmd, shell=True).decode().strip()
        
        if window_id:
            # open window
            subprocess.run(f"xdotool windowactivate {window_id}", shell=True)
            subprocess.run(f"xdotool windowmap {window_id}", shell=True)
            
            # First maximize attempt with xdotool
            subprocess.run(f"xdotool windowsize {window_id} 100% 100%", shell=True)
            time.sleep(0.5)  # Small delay for first maximize
            
            # Get window and maximize with pywinctl
            window = wc.getWindowsWithTitle(window_title)[0]
            window.maximize()
            time.sleep(1)  # Additional delay to ensure maximize is complete
            
            # Get window again to ensure we have updated coordinates
            window = wc.getWindowsWithTitle(window_title)[0]
            x, y = window.left, window.top
            width, height = window.width, window.height
            
            print(f"Window position: ({x}, {y})")
            print(f"Window size: ({width}, {height})") 
            return window
        else:
            print(f"No window found with title: {window_title}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Make sure xdotool is installed: sudo apt-get install xdotool")
        return None
    except Exception as e:
        print(f"Error handling window: {e}")
        return None

# take the screenshot
def take_screenshot(window):
    x, y = window.left, window.top
    width, height = window.width, window.height
     
    screenshot = pyautogui.screenshot(region=(x,y,width, height))
    screenshot.show()




# Usage
window_title = "hand_drop"
window = restore_and_maximize_window(window_title)
take_screenshot(window=window)

# Now open the camera for image superimposition
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    print(frame.shape)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

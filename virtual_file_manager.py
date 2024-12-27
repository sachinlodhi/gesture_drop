import subprocess
from mss import mss
import cv2
import numpy as np
import time
import glob
import mediapipe as mp

# For now let us stick to the constant screenshot and we will fix the screenshot process later

# Now open the camera for image superimposition
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.namedWindow("file manager", cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)

# loading file manager screen
# file_manager = cv2.imread("manager_screen.png")
files_list= glob.glob('/home/sachin/Desktop/all/projects/tyler/*.*')

# some object intializations
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# function to extract the top of the index finger
def landmarks_extraction(hand_landmarks):
   
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # print(index_finger_mcp.y, index_finger_tip.y)
    return index_finger_tip

# function to detect the gesture so can clean the selection. returns true if the palm is being shown
def gesture_detection(hand_landmarks):
    # getting details of roi landmarks
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    mid_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    mid_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    # print(wrist.z, round(thumb_tip.z,3), round(index_tip.z,3), round(mid_tip.z,3), round(ring_tip.z,3), round(pinky_tip.z,3))
    # print(index_tip.z)

    ''' let us analyze if the palm is being shown. The hypothesis is that the y coordiante of the each fingers TIP will be less than PIP in open position'''
    # print(index_pip.y>index_tip.y, mid_pip.y>mid_tip.y, ring_pip.y>ring_tip.y, pinky_pip.y>pinky_tip.y)
    if index_pip.y>index_tip.y and mid_pip.y>mid_tip.y and ring_pip.y>ring_tip.y and pinky_pip.y>pinky_tip.y:
        return True
    else:
        return False

    # print(index_finger_mcp.y, index_finger_tip.y)

points_to_draw = []

with mp_hands.Hands(
    static_image_mode=False,
    model_complexity = 1,
    min_detection_confidence = 0.90,
    min_tracking_confidence = 0.9,
    max_num_hands = 1) as hands:
    
    while True:
        _, frame = cap.read()
        file_manager = cv2.imread("manager_screen.png")
        # print(frame.shape)
        
        frame_height, frame_width = frame.shape[0], frame.shape[1]
        file_manager_height, file_manager_width = file_manager.shape[0], file_manager.shape[1]
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Drawing landmarks
        frame.flags.writeable = True
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # getting the tips of the fingers and wrist
                index_tip = landmarks_extraction(hand_landmarks)


                x = index_tip.x 
                y = index_tip.y
                # append x,y to the list to draw things
                points_to_draw.append((x,y))
                try: # check if the palm is being shown
                    if gesture_detection(hand_landmarks):
                        points_to_draw.clear()
                        print("True")
                    # iterate over the list to draw over the image
                    for idx in range(1, len(points_to_draw)):
                        # print(points_to_draw[idx])
                        # recalculate pt1 and pt2 for the camera and file manager draw
                        frame_pt1 = (int(points_to_draw[idx][0]*frame_width), int(points_to_draw[idx][1]*frame_height))
                        frame_pt2 = (int(points_to_draw[idx-1][0] * frame_width), int(points_to_draw[idx-1][1] * frame_height))

                        file_manager_pt1 = (int(abs(1-points_to_draw[idx][0])*file_manager_width), int(points_to_draw[idx][1] * file_manager_height))
                        file_manager_pt2 = (int(abs(1-points_to_draw[idx-1][0])*file_manager_width), int(points_to_draw[idx-1][1] * file_manager_height))

                        cv2.line(img=frame, pt1= frame_pt1, pt2 = frame_pt2, color=(0, 0, 255), thickness=5)
                        cv2.line(img=file_manager, pt1= file_manager_pt1, pt2 = file_manager_pt2, color=(0, 0, 255), thickness=5)
                        # cv2.circle(frame, (point[0], point[1]), radius=5, color=(0, 0, 255), thickness=-1) 
                except Exception as e:
                    print(f"Error: {e}")
                    pass

        
        cv2.imshow("frame", cv2.flip(frame,1))
        cv2.imshow("file manager", file_manager)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
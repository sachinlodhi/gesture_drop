import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import receiver
import threading

# some object intializations
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Initialize live plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data, lw=2)

# Set up the plot
ax.set_xlim(0, 100)  # Adjust dynamically
ax.set_ylim(0, 1)   # Adjust based on expected particle range
ax.set_title("Z_analysis")
ax.set_xlabel("Frames")
ax.set_ylabel("Z-vals")
iteration = 0


# function to detect gesture
def gesture_detection(hand_landmarks):
    # getting details of roi landmarks
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    mid_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    # print(wrist.z, round(thumb_tip.z,3), round(index_tip.z,3), round(mid_tip.z,3), round(ring_tip.z,3), round(pinky_tip.z,3))
    # print(index_tip.z)

    # let us extract the finger's top coordinates and joints of the fingers and tips.
    index_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # print(index_finger_mcp.y, index_finger_tip.y)
    return [index_finger_pip.y, index_finger_tip.y]

    # return round(wrist.z*1e9,1)

ctr = 0
old_val = 1
is_open = False
cap = cv2.VideoCapture(0)
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
with mp_hands.Hands(
    model_complexity = 0,
    min_detection_confidence = 0.70,
    min_tracking_confidence = 0.7) as hands:
    while cap.isOpened(): # reading frames
        _, frame = cap.read()
        if not _:
            print("Empty frames dropped")
            continue

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        
        # Drawing landmarks
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # getting the tips of the fingers and wrist
                data = gesture_detection(hand_landmarks)
                if data[0]<data[1] and is_open: # fixed threshold for now
                    print("CLOSE")
                    is_open = False
                    
                    
                elif data[0]>data[1] and is_open == False:
                    print("OPEN")
                    is_open = True
                    t1 = threading.Thread(target = receiver.receive)
                    t1.start()
               
                mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
        cv2.imshow("frame", cv2.flip(frame,1))

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

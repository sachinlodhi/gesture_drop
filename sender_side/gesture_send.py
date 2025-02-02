""" This is sender side script. What it does:
1. Opens the camera
2. Analyse hand landmarks.
3. Allows to take screenshot of the file manager(show three fingers).
4. Allows to hightlight multiple files on the taken screenshot by hand gesture(use index finger).
5. Allows to confirm those selected files to send(use index+middle finger).
6. Grab those files(make grabbing gesture.)
7. On the receiver side show this grabbed hand(fist) and then open it.
8. Done.
"""

import subprocess
from mss import mss
import cv2
import numpy as np
import time
import glob
import mediapipe as mp
import pytesseract
import re
import threading
import sender
import random
import pyautogui
from pathvalidate import is_valid_filename, sanitize_filename

# Now open the camera for image superimposition
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
# cv2.namedWindow("file manager", cv2.WINDOW_NORMAL)
# cv2.namedWindow("selected area", cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)
main_path = "/home/sachin/Desktop/all/projects/tyler/"

# some object intializations
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# function to extract the top of the index finger and draw it
def landmarks_extraction(hand_landmarks):
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    # print(index_finger_mcp.y, index_finger_tip.y)
    return index_finger_tip


""" function to detect the gesture i.e. palm, fist, index finger, index+middle finger detection"""
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

    """ let us analyze if the palm is being shown. The hypothesis is that the y coordiante of the each fingers TIP will be less than PIP in open position
    codes
    -1: palm,
    0: fist,
    1: index,
    2: 2 fingers open
    3: 3 fingers open for screenshot
    """
    # palm
    if (
        index_pip.y > index_tip.y
        and mid_pip.y > mid_tip.y
        and ring_pip.y > ring_tip.y
        and pinky_pip.y > pinky_tip.y
    ):
        return -1
    # fist
    elif (
        index_pip.y < index_tip.y
        and mid_pip.y < mid_tip.y
        and ring_pip.y < ring_tip.y
        and pinky_pip.y < pinky_tip.y
    ):
        return 0
    # index finger
    elif (
        index_pip.y > index_tip.y
        and mid_pip.y < mid_tip.y
        and ring_pip.y < ring_tip.y
        and pinky_pip.y < pinky_tip.y
    ):
        return 1
    # detect index and middle finger open to proceed with the selected files
    elif (
        index_pip.y > index_tip.y
        and mid_pip.y > mid_tip.y
        and ring_pip.y < ring_tip.y
        and pinky_pip.y < pinky_tip.y
    ):
        return 2
    # for screenshot
    elif (
        index_pip.y > index_tip.y
        and mid_pip.y > mid_tip.y
        and ring_pip.y > ring_tip.y
        and pinky_pip.y < pinky_tip.y
    ):
        return 3


"""function to get the selected area, process it using Pytesseract OCR and extract the filename"""
def get_filenames(img, area_pts):
    """section to extract the roi"""

    # creating new black and white image with curve that will serve as mask to extract roi
    img_shape = img.shape[:2]
    new_img = np.zeros(img_shape, dtype=np.uint8)
    cleaned_file_list = []  # to store the filenames(cleaned)
    # setting boundary to white
    for pt in area_pts:
        x, y = pt
        new_img[y, x] = 255

    # creating mask
    _, binary_mask = cv2.threshold(new_img, 0, 255, cv2.THRESH_BINARY)
    filled_mask = binary_mask.copy()
    cv2.floodFill(filled_mask, None, (0, 0), 255)  # Filling outside of the curve
    filled_mask = cv2.bitwise_not(filled_mask)  # Inversion of the mask

    # Applying mask to the colored image
    masked_img = cv2.bitwise_and(img, img, mask=filled_mask)

    # Getting bounding box
    contours, _ = cv2.findContours(
        filled_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        roi = masked_img[y : y + h, x : x + w]

        # zooming in to get the best OCR results
        scale_factor = 2
        height, width = roi.shape[:2]
        new_height, new_width = int(height * scale_factor), int(width * scale_factor)
        zoomed_roi = cv2.resize(
            roi, (new_width, new_height), interpolation=cv2.INTER_CUBIC
        )

        """section to get the text using Pytesseract OCR"""
        custom_config = r"--psm 6 --oem 3"
        text = pytesseract.image_to_string(zoomed_roi, config=custom_config)
        text = text.rstrip()
        print(f"Detected file names: {text}")

        text = text.split(
            "\n"
        )  # gives the list of two lines and first one contains the file names
        # text = text[0].split(" ") # this will make a list with the elements of the valid and invalid file name
        print(f" After splitting by newline : {text} and size of list : {len(text)}")
        for t in text:
            print(t)
            t = t.split(" ")
            for _ in t:
                print(_)

                if is_valid_filename(_) and "." in _:
                    cleaned_file_list.append(_)

    return [roi, cleaned_file_list]


"""function to get the list of the connecting points between two points pt1<->pt2"""
def get_line_points(start, end):  # tuple, tuple and returns list of tuples

    x1, y1 = start
    x2, y2 = end

    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Determine direction of line
    x_step = 1 if x1 < x2 else -1
    y_step = 1 if y1 < y2 else -1

    # Determine whether to drive the algorithm by x or y
    if dx > dy:
        # Drive by x
        err = dx / 2
        x = x1
        y = y1

        while x != x2 + x_step:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += y_step
                err += dx
            x += x_step
    else:
        # Drive by y
        err = dy / 2
        x = x1
        y = y1

        while y != y2 + y_step:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += x_step
                err += dy
            y += y_step

    return points

# some variables to store the status and intermediate data
points_to_draw = []  # stores the mediapipe relative points
points_file_manager = []  # stores the points to be drawn on the file_manager
selected_files = []  # stores the filenames
sending_status = False  # to track if the file sending has been started
screenshot_taken = False # checks if the screenshot has been take 
file_manager_canvas = np.zeros((480, 640, 3), dtype=np.uint8)
with mp_hands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.70,
    min_tracking_confidence=0.7,
    max_num_hands=1,
) as hands:
    while True:

        _, frame = cap.read()
        file_manager = file_manager_canvas.copy()

        frame_height, frame_width = frame.shape[0], frame.shape[1]
        file_manager_height, file_manager_width = (
            file_manager.shape[0],
            file_manager.shape[1],
        )
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
                # circle to track the hand movement with random colors to get the flashing effect
                random_b = random.randint(0, 256)
                random_g = random.randint(0, 256)
                random_r = random.randint(0, 256)
                cv2.circle(
                    img=file_manager,
                    center=(
                        int(abs(1 - x) * file_manager_width),
                        int(y * file_manager_height),
                    ),
                    radius=6,
                    color=(random_b, random_g, random_r),
                    thickness=-1,
                )
                # append x,y to the list to draw things
                points_to_draw.append((x, y))
                try:
                    if (
                        gesture_detection(hand_landmarks) == -1
                    ):  # if palm  or first is being shown then clear every points in each list
                        points_to_draw.clear()
                        points_file_manager.clear()
                        print("Tru")

                    elif (
                        gesture_detection(hand_landmarks) == 2
                    ):  # if 2 fingers are shown then get the cutout
                        ocr_data = get_filenames(
                            img=file_manager, area_pts=points_file_manager
                        )
                        # print(selected_files)
                        roi = ocr_data[0]
                        cv2.imshow("selected area", roi)
                        print(f"Files list {ocr_data[1]}")
                        selected_files = ocr_data[1]
                    elif gesture_detection(hand_landmarks) == 0 and (
                        not sending_status
                    ):  # if the fist is shown then it means user is grabbing files and start sending process but check the sending status_flag too
                        print(
                            f"size of selected file : {len(selected_files)}: {selected_files}"
                        )
                        if (
                            len(selected_files) > 0
                        ):  # this is to reduce the false fist detection in this case the size of the selected_files list is >0 then only proceed
                            t1 = threading.Thread(
                                target=sender.sending,
                                args=(
                                    main_path,
                                    selected_files,
                                ),
                            )
                            t1.start()
                            print("Started Sending")
                            sending_status = True
                    elif (
                        gesture_detection(hand_landmarks) == 3 and not screenshot_taken
                    ):  # see if user is taking screenshot

                        screenshot = pyautogui.screenshot()  # take screenshot
                        # Convert to OpenCV format
                        screenshot = np.array(screenshot)
                        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                        file_manager_canvas = screenshot.copy()
                        screenshot_taken = True

                    # iterate over the list to draw over the image
                    for idx in range(1, len(points_to_draw)):

                        # recalculate pt1 and pt2 for the camera and file manager draw
                        frame_pt1 = (
                            int(points_to_draw[idx][0] * frame_width),
                            int(points_to_draw[idx][1] * frame_height),
                        )
                        frame_pt2 = (
                            int(points_to_draw[idx - 1][0] * frame_width),
                            int(points_to_draw[idx - 1][1] * frame_height),
                        )

                        file_manager_pt1 = (
                            int(abs(1 - points_to_draw[idx][0]) * file_manager_width),
                            int(points_to_draw[idx][1] * file_manager_height),
                        )
                        file_manager_pt2 = (
                            int(
                                abs(1 - points_to_draw[idx - 1][0]) * file_manager_width
                            ),
                            int(points_to_draw[idx - 1][1] * file_manager_height),
                        )
                        points_file_manager.append(file_manager_pt1)

                        cv2.line(
                            img=frame,
                            pt1=frame_pt1,
                            pt2=frame_pt2,
                            color=(0, 0, 255),
                            thickness=2,
                        )
                        cv2.line(
                            img=file_manager,
                            pt1=file_manager_pt1,
                            pt2=file_manager_pt2,
                            color=(0, 0, 255),
                            thickness=2,
                        )

                        # get the intermediate points on the line connecting pt1 and pt2
                        line_points = get_line_points(
                            start=file_manager_pt1, end=file_manager_pt2
                        )
                        # print("appending", len(points_file_manager))
                        for i in line_points:
                            points_file_manager.append(i)
                        # print("appended", len(points_file_manager))

                except Exception as e:
                    print(f"Error: {e}")
                    pass

        cv2.imshow("frame", cv2.flip(frame, 1))
        if (
            screenshot_taken
        ):  # show file manager only if user takes screenshot. This will help to select the files.
            cv2.namedWindow("file manager", cv2.WINDOW_NORMAL)
            cv2.imshow("file manager", file_manager)
        if cv2.waitKey(1) == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()

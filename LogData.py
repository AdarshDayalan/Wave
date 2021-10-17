import cv2
import csv
import mediapipe as mp
import numpy as np
import copy
import itertools

label_num = 11
 
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
 
    landmark_array = np.empty((0, 2), int)
 
    for _, landmark in enumerate(landmarks.landmark):
        # print(landmark)
 
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point = [np.array((landmark_x, landmark_y))]
        landmark_array = np.append(landmark_array, landmark_point, axis=0)
 
    # print("\n")
    x, y, w, h = cv2.boundingRect(landmark_array)
 
    return [x, y, x + w, y + h]
 
def draw_bounding_rect(use_brect, image, brect, text, run):
    if use_brect:
        # Outer rectangle
        cv2.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 0, 0), 1)
        cv2.putText(image, text, (brect[0], brect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
 
    return image
 
def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
 
    landmark_point = []
 
    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z
 
        landmark_point.append([landmark_x, landmark_y])
 
    return landmark_point
 
def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
 
    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]
 
        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y
 
    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))
 
    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))
 
    def normalize_(n):
        return n / max_value
 
    temp_landmark_list = list(map(normalize_, temp_landmark_list))
 
    return temp_landmark_list
 
def logging_csv(number, landmark_list):
    csv_path = 'CSV/hand_landmarks.csv'
    with open(csv_path, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *landmark_list])
 
def main():
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False,max_num_hands=1,min_detection_confidence=0.5)

    cap = cv2.VideoCapture(0)
 
    while (cap.isOpened()):
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
 
        if results.multi_hand_landmarks:
            for handLMS in results.multi_hand_landmarks:
                text = "None"
                lml = calc_landmark_list(img, handLMS)
                pre_lml = pre_process_landmark(lml)

                logging_csv(label_num, pre_lml)
                
                #Draws Box
                b_rect = calc_bounding_rect(img, handLMS)
                img = draw_bounding_rect(True, img, b_rect, text)
        
        cv2.imshow("Image", img)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
if __name__ == '__main__':
    main()
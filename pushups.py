import cv2
import mediapipe as mp
import numpy as np


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


count = 0
position = None

cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Empty camera")
            break


        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        result = pose.process(image)

    
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        imlist = []

        if result.pose_landmarks:
            mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            h, w, _ = image.shape

            for id, lm in enumerate(result.pose_landmarks.landmark):
                X, Y = int(lm.x * w), int(lm.y * h)
                imlist.append([id, X, Y])

        print(imlist)
    
        if len(imlist) != 0:
            left_shoulder_y = imlist[11][2]
            left_elbow_y = imlist[13][2]
            right_shoulder_y = imlist[12][2]
            right_elbow_y = imlist[14][2]

            if left_elbow_y - left_shoulder_y > 15 and right_elbow_y - right_shoulder_y > 15:
                position = "down"
            elif left_elbow_y - left_shoulder_y < 5 and right_elbow_y - right_shoulder_y < 5 and position == "down":
                position = "up"
                count += 1
                print(count)

        # Display the image
        cv2.putText(image, f"Push-ups: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("Push-up counter", cv2.flip(image, 1))

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

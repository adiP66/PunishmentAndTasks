import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def count_pushups(punishment_count):
  """
  Starts a real-time push-up counter using OpenCV and MediaPipe.

  Args:
      punishment_count: The desired number of push-ups for punishment.

  Returns:
      The final push-up count after the user completes the exercise.
  """

  count = 0
  position = None
  completed = False  # Flag to track completion

  cap = cv2.VideoCapture(0)
  with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
    while cap.isOpened() and not completed:
      success, image = cap.read()
      if not success:
        print("Empty camera")
        break

      image = cv2.flip(image, 1)  # Flip horizontally (optional)
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      result = pose.process(image)

      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

      if result.pose_landmarks:
        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        for id, lm in enumerate(result.pose_landmarks.landmark):
          h, w, _ = image.shape
          X, Y = int(lm.x * w), int(lm.y * h)

          # Check push-up position based on elbow and shoulder Y-coordinates
          if id == 13 and position != "down":  # Left elbow
            if Y > result.pose_landmarks.landmark[11].y + 15:  # Lower than shoulder
              position = "down"
          elif id == 14 and position == "down":  # Right elbow
            if Y > result.pose_landmarks.landmark[12].y + 15:
              position = "down"
          elif id in [13, 14] and position == "down":  # Both elbows up
            if Y < result.pose_landmarks.landmark[id - 2].y - 15:  # Higher than shoulder
              position = "up"
              count += 1

      # Display information and handle completion
      cv2.putText(image, f"Push-ups: {count}/{punishment_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
      if count >= punishment_count:
        completed = True
        print(f"Congratulations! You completed {punishment_count} push-ups.")

      cv2.imshow("Push-up counter", image)

      # Break loop if 'q' is pressed or punishment is completed
      if cv2.waitKey(1) & 0xFF == ord('q') or completed:
        break

  cap.release()
  cv2.destroyAllWindows()

  return count  # Return final push-up count

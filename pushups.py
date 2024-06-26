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
    position = "up"  # Initial position should be "up"
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
                landmarks = result.pose_landmarks.landmark

                # Get the Y-coordinates of shoulders and elbows
                left_shoulder_y = landmarks[11].y
                right_shoulder_y = landmarks[12].y
                left_elbow_y = landmarks[13].y
                right_elbow_y = landmarks[14].y

                # Check push-up position
                if left_elbow_y > left_shoulder_y + 0.1 and right_elbow_y > right_shoulder_y + 0.1:
                    position = "down"
                elif left_elbow_y < left_shoulder_y - 0.1 and right_elbow_y < right_shoulder_y - 0.1 and position == "down":
                    position = "up"
                    count += 1
                    print(f"Push-up count: {count}")

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


# Example usage
if __name__ == "__main__":
    count_pushups(10)  # Change 10 to the desired number of push-ups

import cv2
import time
import threading
import os
import numpy as np
from datetime import datetime
from plyer import notification

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Load multiple face detection cascades for better reliability
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
alt_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
alt2_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

# Initialize camera with optimal settings
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)  # Increase brightness slightly
cap.set(cv2.CAP_PROP_CONTRAST, 150)    # Increase contrast slightly

# Notification and logging variables
last_notification_time = 0
notification_cooldown = 3  # seconds between notifications
face_missing_start_time = None
detection_history = [False] * 5  # Track last 5 detection results to smooth detection

# Facial verification variables
reference_face = None
is_same_person = True
similarity_score = 0
verification_threshold = 0.7  # Lower value = stricter verification

def log_missing_face():
    """Log when face is not detected"""
    with open("logs/detection_log.txt", "a") as file:
        file.write(f"No face detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_different_person():
    """Log when a different person is detected"""
    with open("logs/verification_log.txt", "a") as file:
        file.write(f"Different person detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def show_notification(title, message):
    """Show a desktop notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=2
        )
    except Exception as e:
        print(f"Notification error: {e}")

def detect_faces(frame):
    """Enhanced face detection using multiple cascades and parameters"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization to improve detection in poor lighting
    gray = cv2.equalizeHist(gray)
    
    # Improve contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    # Try multiple detection methods with different parameters
    faces = []
    
    # Method 1: Default cascade with standard parameters
    faces1 = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,  # Reduced from 5 for higher sensitivity
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Method 2: Alt cascade with more sensitive parameters
    faces2 = alt_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # More granular scaling for better detection
        minNeighbors=3,    # Even more sensitive
        minSize=(25, 25),  # Detect smaller faces
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Method 3: Alt2 cascade with different parameters
    faces3 = alt2_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=3,
        minSize=(25, 25),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Combine results from all methods
    if len(faces1) > 0:
        faces.extend(faces1)
    if len(faces2) > 0:
        faces.extend(faces2)
    if len(faces3) > 0:
        faces.extend(faces3)
    
    # Remove duplicates by merging overlapping rectangles
    if len(faces) > 0:
        faces, _ = cv2.groupRectangles(list(faces), 1, 0.3)
    
    return faces

def extract_face_features(frame, face_rect):
    """Extract facial features for comparison"""
    x, y, w, h = face_rect
    
    # Ensure the face region is within frame boundaries
    x = max(0, x)
    y = max(0, y)
    w = min(w, frame.shape[1] - x)
    h = min(h, frame.shape[0] - y)
    
    # Extract face region
    face_region = frame[y:y+h, x:x+w]
    
    # Resize to standard size
    face_region = cv2.resize(face_region, (100, 100))
    
    # Convert to grayscale
    gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization
    gray_face = cv2.equalizeHist(gray_face)
    
    # Flatten to feature vector
    features = gray_face.flatten().astype(np.float32)
    
    # Normalize features
    if np.max(features) > 0:
        features = features / np.max(features)
    
    return features

def compare_faces(features1, features2):
    """Compare two face feature vectors and return similarity score"""
    # Calculate correlation coefficient
    correlation = np.corrcoef(features1, features2)[0, 1]
    
    # Calculate mean squared error
    mse = np.mean((features1 - features2) ** 2)
    
    # Normalize MSE to 0-1 range (lower is better)
    mse_normalized = 1 - min(1, mse / 0.5)
    
    # Combine metrics (higher is better)
    similarity = (correlation + mse_normalized) / 2
    
    return max(0, similarity)  # Ensure non-negative

# Main processing loop
try:
    while True:
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            time.sleep(0.1)
            continue
        
        current_time = time.time()
        
        # Detect faces
        faces = detect_faces(frame)
        
        # Update detection history
        detection_history.pop(0)
        detection_history.append(len(faces) > 0)
        
        # Determine if face is consistently detected (at least 2 out of 5 frames)
        face_detected = sum(detection_history) >= 2
        
        # Check if face is detected
        if not face_detected or len(faces) == 0:
            # No face detected
            if face_missing_start_time is None:
                face_missing_start_time = current_time
            
            # If face has been missing for more than notification_cooldown seconds
            if (current_time - face_missing_start_time > notification_cooldown and 
                current_time - last_notification_time > notification_cooldown):
                threading.Thread(target=show_notification, 
                                args=("Face Not Detected!", 
                                      "Please position your face in front of the camera.")).start()
                threading.Thread(target=log_missing_face).start()
                last_notification_time = current_time
                
            # Add status text - red for no face
            cv2.putText(frame, "Status: No Face Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # Face detected
            face_missing_start_time = None
            
            # Get the largest face for verification
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            
            # Extract features from the current face
            current_features = extract_face_features(frame, largest_face)
            
            # If this is the first face detected, save it as reference
            if reference_face is None:
                reference_face = current_features
                is_same_person = True
                similarity_score = 1.0
                
                # Show notification for initial face capture
                threading.Thread(target=show_notification, 
                                args=("Face Registered", 
                                      "Your face has been registered for verification.")).start()
            else:
                # Compare with reference face
                similarity_score = compare_faces(reference_face, current_features)
                is_same_person = similarity_score >= verification_threshold
                
                # If different person detected, show notification
                if not is_same_person and current_time - last_notification_time > notification_cooldown:
                    threading.Thread(target=show_notification, 
                                    args=("Different Person Detected!", 
                                          "Please ensure the same person continues the process.")).start()
                    threading.Thread(target=log_different_person).start()
                    last_notification_time = current_time
            
            # Draw rectangles around all detected faces
            for face_rect in faces:
                # Choose color based on verification result (green for same, red for different)
                # Fix: Compare tuples properly
                if np.array_equal(face_rect, largest_face):
                    color = (0, 255, 0) if is_same_person else (0, 0, 255)
                else:
                    color = (255, 165, 0)  # Orange for additional faces
                
                x, y, w, h = face_rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Add status text
            if is_same_person:
                status = f"Status: Same Person (Score: {similarity_score:.2f})"
                cv2.putText(frame, status, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                status = f"Status: Different Person (Score: {similarity_score:.2f})"
                cv2.putText(frame, status, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display detection confidence
        confidence_text = f"Detection confidence: {sum(detection_history)}/5"
        cv2.putText(frame, confidence_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
        
        # Display the frame
        cv2.imshow("Face Verification", frame)
        
        # Press 'q' to quit, 'r' to reset reference face
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            reference_face = None
            print("Reference face reset")

except Exception as e:
    print(f"Error in main loop: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

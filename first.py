import cv2
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Function to extract features from an image
def extract_features(image):
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Compute the mean value of each channel
    mean_hue = np.mean(hsv[:, :, 0])
    mean_saturation = np.mean(hsv[:, :, 1])
    mean_value = np.mean(hsv[:, :, 2])
    
    return [mean_hue, mean_saturation, mean_value]

# Load training data (replace with your dataset)
# Example: X_train is feature matrix, y_train is labels
# For demonstration, we use dummy data
X_train = np.array([[120, 100, 200], [80, 150, 180], [50, 50, 150]])
y_train = np.array([1, 0, 0])  # 1 for good quality, 0 for bad quality

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train a Support Vector Classifier
clf = SVC(kernel='linear')
clf.fit(X_train_scaled, y_train)

# Load and process the test image
test_image = cv2.imread('2.jpg')
features = extract_features(test_image)
features_scaled = scaler.transform([features])

# Predict quality
prediction = clf.predict(features_scaled)
if prediction == 1:
    print("Crop quality is good")
else:
    print("Crop quality is bad")

# Display the test image
cv2.imshow('Test Image', test_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

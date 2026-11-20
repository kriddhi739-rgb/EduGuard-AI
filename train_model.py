import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Create training data
np.random.seed(42)
n = 500
X_train = pd.DataFrame({
    "Attendance_Rate": np.random.uniform(40, 95, n),
    "CGPA": np.random.uniform(4.5, 9.8, n),
    "LMS_Activity_Score": np.random.uniform(20, 100, n),
    "Fee_Dues": np.random.choice([0, 1], n, p=[0.8, 0.2])
})
y_train = ((X_train["Attendance_Rate"] < 60) | (X_train["CGPA"] < 5.5) | (X_train["Fee_Dues"] == 1)).astype(int)

# Train and save model in the root folder
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, "dropout_model.pkl")
print("Model trained and saved successfully!")
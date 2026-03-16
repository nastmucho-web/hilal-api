import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# قراءة dataset
df = pd.read_csv("dataset.csv")

# الميزات التي يعتمد عليها النموذج
features = [
    "moon_alt",
    "arcv",
    "elongation",
    "moon_age"
]

X = df[features]
y = df["visible"]

# تقسيم البيانات للتدريب والاختبار
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# إنشاء النموذج
model = LogisticRegression()

# تدريب النموذج
model.fit(X_train, y_train)

# اختبار الدقة
accuracy = model.score(X_test, y_test)

print("Model accuracy:", accuracy)

# حفظ النموذج
joblib.dump(model, "hilal_model.pkl")

print("Model saved as hilal_model.pkl")
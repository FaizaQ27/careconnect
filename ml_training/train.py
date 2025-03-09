import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load dataset
data = pd.read_csv('../dataset.csv')

# Preprocessing: Tokenize symptoms
nltk.download('punkt')
nltk.download('punkt_tab')  # Add this line
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def tokenize(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return tokens

# Apply tokenization on symptoms column
data['tokens'] = data['symptoms'].apply(tokenize)
data['symptoms'] = data['tokens'].apply(lambda x: ' '.join(x))

# Splitting the data
X = data['symptoms']
y = data['disease']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# List of models to compare
models = {
    "Random Forest": RandomForestClassifier(),
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier(),
    "SVC": SVC(),
    "Gradient Boosting": GradientBoostingClassifier()
}

accuracies = {}

# Train and evaluate models with class_weight='balanced'
for name, clf in models.items():
    if name == "Random Forest":
        clf = RandomForestClassifier(class_weight='balanced')  # Handle class imbalance for Random Forest
    model = make_pipeline(CountVectorizer(), clf)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    accuracies[name] = acc

# Find the best model
best_model_name = max(accuracies, key=accuracies.get)
best_model = make_pipeline(CountVectorizer(), models[best_model_name])
best_model.fit(X_train, y_train)
y_pred_best = best_model.predict(X_test)

# Save accuracy comparison graph
plt.figure(figsize=(10, 5))
sns.barplot(x=list(accuracies.keys()), y=list(accuracies.values()))
plt.xlabel("Model")
plt.ylabel("Accuracy")
plt.title("Model Comparison")
plt.xticks(rotation=30)
plt.tight_layout()  # Ensure labels are fully visible
plt.savefig("model_comparison.png")

# Save the best model
joblib.dump(best_model, f'{best_model_name.replace(" ", "_").lower()}_model.joblib')

# Save classification report and confusion matrix
report = classification_report(y_test, y_pred_best, zero_division=1)
conf_matrix = confusion_matrix(y_test, y_pred_best)

# Save confusion matrix as an image
plt.figure(figsize=(30, 30))  # Increase figure size
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=models[best_model_name].classes_, yticklabels=models[best_model_name].classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.xticks(rotation=45)  # Rotate X-axis labels
plt.yticks(rotation=45)  # Rotate Y-axis labels
plt.tight_layout()  # Ensure labels are fully visible
plt.savefig("confusion_matrix.png")

# Save classification report
with open("classification_report.txt", "w") as f:
    f.write(report)

print(f"Best Model: {best_model_name} with Accuracy: {accuracies[best_model_name]:.4f}")

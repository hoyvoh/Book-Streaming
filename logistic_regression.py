import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load the data
products = pd.read_csv("./data/product_data.csv", sep=";")
cols = ['PRICE', 'all_time_quantity_sold', 'REVIEW_COUNT', 'RATING_AVERAGE']
df_products = products[cols].dropna()

# Define the sales likelihood based on the condition
df_products['sales_likelihood'] = df_products['all_time_quantity_sold'].apply(lambda x: 1 if x > 1000 else 0)

# Separate features and target variable
X = df_products[cols[:-1]]  # Excluding the target variable
y = df_products['sales_likelihood']

# Split the data into training (80%), validation (10%), and test (10%) sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.1, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Define the logistic regression model
lr = LogisticRegression()

# Fit the model on the training data
lr.fit(X_train_scaled, y_train)

# Make predictions on the training, validation, and test data
train_predictions = lr.predict(X_train_scaled)
val_predictions = lr.predict(X_val_scaled)
test_predictions = lr.predict(X_test_scaled)

# Calculate accuracy for the training, validation, and test sets
train_accuracy = accuracy_score(y_train, train_predictions)
val_accuracy = accuracy_score(y_val, val_predictions)
test_accuracy = accuracy_score(y_test, test_predictions)

print(f"Training Set Accuracy = {train_accuracy}")
print(f"Validation Set Accuracy = {val_accuracy}")
print(f"Test Set Accuracy = {test_accuracy}")

# Optionally, save the trained model
from joblib import dump
path = './model/logistic_regression_model.joblib'
dump(lr, path)
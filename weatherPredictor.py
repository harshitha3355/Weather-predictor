import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# ThingSpeak Config
CHANNEL_ID = "3003731"
READ_API_KEY = "5ITYHYCLFRTELXK2"
WRITE_API_KEY = "2ILFSOB3VVA5D69A"

# Step 1: Fetch Data from ThingSpeak
def fetch_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=1000"
    response = requests.get(url).json()
    data = pd.DataFrame(response['feeds'])
    data = data.astype({'field1': float, 'field2': float, 'field3': float, 'field4': float})  # temp, hum, press, rain
    return data

# Step 2: Train ML Model
def train_model(data):
    # Label data: 1 if rain > threshold (e.g., 500), else 0
    data['rain_label'] = (data['field4'] > 500).astype(int)
    X = data[['field1', 'field2', 'field3']]  # temp, hum, pressure
    y = data['rain_label']

    # Train Random Forest
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    print(f"Model Accuracy: {model.score(X_test, y_test):.2f}")
    return model

# Step 3: Predict & Post to ThingSpeak
def predict_and_post(model):
    # Fetch latest data
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={READ_API_KEY}"
    data = requests.get(url).json()
    temp = float(data['field1'])
    humidity = float(data['field2'])
    pressure = float(data['field3'])

    # Predict
    prediction = model.predict([[temp, humidity, pressure]])[0]
    print(f"Prediction: {'Rain' if prediction == 1 else 'No Rain'}")

    # Post to ThingSpeak (Field 5)
    requests.post(f"https://api.thingspeak.com/update?api_key={WRITE_API_KEY}&field5={prediction}")

# Main Workflow
if __name__ == "__main__":
    data = fetch_data()
    model = train_model(data)
    joblib.dump(model, 'weather_model.pkl')  # Save model
    predict_and_post(model)  # Run prediction
import numpy as np
from sklearn.ensemble import IsolationForest
import configparser
from anomaly_detection_enhanced import AnomalyDetector
from ddos_detection_placeholder_enhanced import DDoSDetector
from encryption_and_rate_limiting_enhanced import EncryptionService, RateLimiter
from flask_app_with_ratelimit_enhanced import create_app

def start_services():
    # Load configurations
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Initialize services
    anomaly_detector = AnomalyDetector(config)
    ddos_detector = DDoSDetector(config)
    encryption_service = EncryptionService(config)
    rate_limiter = RateLimiter(config)

    # Create Flask app
    app = create_app(config)

    # Start Flask app
    app.run(host='0.0.0.0', port=8000)  # Run the Flask app

if __name__ == "__main__":
    # Example data: Replace this with your actual dataset
    data = np.random.rand(100, 2)  # 100 samples with 2 features

    # Creating the IsolationForest model
    model = IsolationForest(n_estimators=100, contamination=0.1)
    model.fit(data)

    # Predicting anomalies
    predictions = model.predict(data)

    # Identifying the anomaly data points
    anomalies = data[predictions == -1]
    print("Anomalies detected:", anomalies)

    # Start your services
    start_services()

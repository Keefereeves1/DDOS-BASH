import numpy as np
from sklearn.ensemble import IsolationForest
import tkinter as tk
from tkinter import scrolledtext

# Example data: Replace this with your actual dataset
data = np.random.rand(100, 2)  # 100 samples with 2 features

# Creating the IsolationForest model
model = IsolationForest(n_estimators=100, contamination=0.1)
model.fit(data)

# Predicting anomalies
predictions = model.predict(data)

# Identifying the anomaly data points
anomalies = data[predictions == -1]

# Function to format anomalies for display
def format_anomalies(anomalies):
    return '\n'.join([f"Anomaly {i+1}: {point}" for i, point in enumerate(anomalies)])

# Setting up the Tkinter window
window = tk.Tk()
window.title("Anomaly Detection Results")

# Adding a scrolled text widget to display the anomalies
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=10)
text_area.grid(column=0, row=0, pady=10, padx=10)
text_area.insert(tk.INSERT, format_anomalies(anomalies))

# Start the Tkinter event loop
window.mainloop()

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
from typing import Dict, List  # ADD THIS LINE


class AIPredictor:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Load pre-trained model or create new one"""
        # Get the correct path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "../ml_model/deadlock_model.pkl")

        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                print(f"Model loaded successfully from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Creating new model...")
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.train_initial_model()
        else:
            print(f"Model not found at {model_path}")
            print("Creating new model...")
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.train_initial_model()

    def train_initial_model(self):
        """Train model with synthetic data"""
        print("Training initial model with synthetic data...")
        X_train, y_train = self.generate_training_data(1000)
        self.model.fit(X_train, y_train)

        # Save model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(current_dir, "../ml_model")
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "deadlock_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {model_path}")

    def generate_training_data(self, n_samples: int):
        """Generate synthetic deadlock scenarios"""
        X = []
        y = []

        for _ in range(n_samples):
            n_processes = np.random.randint(2, 10)
            n_resources = np.random.randint(2, 8)
            avg_wait_time = np.random.uniform(0, 100)
            resource_utilization = np.random.uniform(0, 1)
            circular_wait = np.random.randint(0, 2)

            features = [n_processes, n_resources, avg_wait_time, resource_utilization, circular_wait]

            # Label: deadlock occurs if circular wait and high resource contention
            label = 1 if (circular_wait == 1 and resource_utilization > 0.7) else 0

            X.append(features)
            y.append(label)

        return np.array(X), np.array(y)

    def predict_deadlock(self, processes: Dict, resources: Dict) -> Dict:
        """Predict deadlock probability"""
        try:
            features = self.extract_features(processes, resources)

            if self.model is None:
                return {"deadlock_probability": 0.0, "risk_level": "UNKNOWN"}

            probability = self.model.predict_proba([features])[0][1]

            return {
                "deadlock_probability": float(probability),
                "risk_level": self.get_risk_level(probability)
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"deadlock_probability": 0.0, "risk_level": "ERROR"}

    def extract_features(self, processes: Dict, resources: Dict) -> List[float]:
        """Extract features from current system state"""
        n_processes = len(processes)
        n_resources = len(resources)

        # Calculate average wait time
        total_wait = sum(p.get("wait_time", 0) for p in processes.values())
        avg_wait_time = total_wait / n_processes if n_processes > 0 else 0

        # Calculate resource utilization
        allocated = sum(len(r.get("allocated_to", [])) for r in resources.values())
        total_instances = sum(r.get("instances", 1) for r in resources.values())
        resource_util = allocated / total_instances if total_instances > 0 else 0

        # Check for circular wait pattern
        circular_wait = self.check_circular_wait(processes)

        return [float(n_processes), float(n_resources), float(avg_wait_time),
                float(resource_util), float(circular_wait)]

    def check_circular_wait(self, processes: Dict) -> int:
        """Check if circular wait condition exists"""
        for proc in processes.values():
            if proc.get("allocated") and proc.get("requested"):
                return 1
        return 0

    def get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability < 0.3:
            return "LOW"
        elif probability < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"

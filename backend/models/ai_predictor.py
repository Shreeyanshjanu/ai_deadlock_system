import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
from typing import Dict, List


class AIPredictor:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Load pre-trained model or create new one"""
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
        """Train model with realistic deadlock scenarios"""
        print("Training model with realistic deadlock scenarios...")
        X_train, y_train = self.generate_realistic_training_data(3000)
        self.model.fit(X_train, y_train)

        # Save model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(current_dir, "../ml_model")
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "deadlock_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {model_path}")

    def generate_realistic_training_data(self, n_samples: int):
        """Generate realistic deadlock training scenarios"""
        X = []
        y = []

        for _ in range(n_samples):
            n_processes = np.random.randint(2, 15)
            n_resources = np.random.randint(2, 12)
            avg_wait_time = np.random.uniform(0, 150)
            resource_utilization = np.random.uniform(0, 1)
            circular_wait = np.random.randint(0, 2)

            features = [n_processes, n_resources, avg_wait_time, resource_utilization, circular_wait]

            # IMPROVED LOGIC: More realistic deadlock conditions
            deadlock_score = 0

            # Factor 1: Circular wait is CRITICAL (50% weight)
            if circular_wait == 1:
                deadlock_score += 50

            # Factor 2: High resource utilization (30% weight)
            if resource_utilization > 0.8:
                deadlock_score += 30
            elif resource_utilization > 0.6:
                deadlock_score += 20
            elif resource_utilization > 0.4:
                deadlock_score += 10

            # Factor 3: Long wait times indicate blocking (15% weight)
            if avg_wait_time > 100:
                deadlock_score += 15
            elif avg_wait_time > 70:
                deadlock_score += 10
            elif avg_wait_time > 40:
                deadlock_score += 5

            # Factor 4: Process/Resource ratio (5% weight)
            if n_processes >= n_resources:
                deadlock_score += 5

            # Determine label based on total score
            if deadlock_score >= 70:
                label = 1  # High chance of deadlock
            elif deadlock_score >= 50:
                label = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% deadlock
            elif deadlock_score >= 30:
                label = np.random.choice([0, 1], p=[0.6, 0.4])  # 40% deadlock
            else:
                label = 0  # Safe state

            X.append(features)
            y.append(label)

        return np.array(X), np.array(y)

    def predict_deadlock(self, processes: Dict, resources: Dict) -> Dict:
        """Predict deadlock probability with improved logic"""
        try:
            features = self.extract_features(processes, resources)

            if self.model is None:
                return {"deadlock_probability": 0.0, "risk_level": "UNKNOWN"}

            # Get base probability from model
            base_probability = self.model.predict_proba([features])[0][1]

            # Apply rule-based boost for critical conditions
            adjusted_probability = self.apply_rule_based_boost(features, base_probability)

            return {
                "deadlock_probability": float(adjusted_probability),
                "risk_level": self.get_risk_level(adjusted_probability)
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"deadlock_probability": 0.0, "risk_level": "ERROR"}

    def apply_rule_based_boost(self, features: List[float], base_prob: float) -> float:
        """Apply rule-based boost for known critical conditions"""
        n_processes, n_resources, avg_wait_time, resource_util, circular_wait = features

        # Strong boost if circular wait detected
        if circular_wait == 1:
            base_prob = max(base_prob, 0.75)  # At least 75% if circular wait

            # Even higher if also high resource utilization
            if resource_util > 0.8:
                base_prob = max(base_prob, 0.90)  # At least 90%
            elif resource_util > 0.6:
                base_prob = max(base_prob, 0.85)  # At least 85%

        # Boost for high resource contention
        if resource_util > 0.9 and avg_wait_time > 80:
            base_prob = max(base_prob, 0.70)  # At least 70%

        # Boost for many processes competing
        if n_processes >= 5 and resource_util > 0.7:
            base_prob = min(base_prob + 0.15, 1.0)

        # Boost for very long wait times
        if avg_wait_time > 100:
            base_prob = min(base_prob + 0.10, 1.0)

        return min(base_prob, 1.0)  # Cap at 100%

    def extract_features(self, processes: Dict, resources: Dict) -> List[float]:
        """Extract features from current system state"""
        n_processes = len(processes)
        n_resources = len(resources)

        # Calculate average wait time
        total_wait = sum(p.get("wait_time", 0) for p in processes.values())
        avg_wait_time = total_wait / n_processes if n_processes > 0 else 0

        # Calculate resource utilization
        total_allocated = 0
        total_available = 0
        for r in resources.values():
            instances = r.get("instances", 1)
            available = r.get("available", instances)
            allocated = instances - available
            total_allocated += allocated
            total_available += instances

        resource_util = total_allocated / total_available if total_available > 0 else 0

        # Check for circular wait pattern (CRITICAL FEATURE)
        circular_wait = self.check_circular_wait_advanced(processes)

        return [float(n_processes), float(n_resources), float(avg_wait_time),
                float(resource_util), float(circular_wait)]

    def check_circular_wait_advanced(self, processes: Dict) -> int:
        """
        Advanced circular wait detection
        Returns 1 if ANY process holds AND requests resources
        """
        for proc in processes.values():
            allocated = proc.get("allocated", [])
            requested = proc.get("requested", [])

            # If a process holds resources AND is waiting for more
            if allocated and requested:
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

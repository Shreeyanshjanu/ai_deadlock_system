import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os


def generate_synthetic_data(n_samples=2000):
    """
    Generate synthetic deadlock training data
    Features: [n_processes, n_resources, avg_wait_time, resource_utilization, circular_wait]
    Labels: 0 (no deadlock), 1 (deadlock)
    """
    X = []
    y = []

    for _ in range(n_samples):
        # Generate random features
        n_processes = np.random.randint(2, 15)
        n_resources = np.random.randint(2, 10)
        avg_wait_time = np.random.uniform(0, 150)
        resource_utilization = np.random.uniform(0.0, 1.0)
        circular_wait = np.random.randint(0, 2)  # Binary: 0 or 1

        features = [n_processes, n_resources, avg_wait_time, resource_utilization, circular_wait]

        # Deadlock conditions (simplified logic):
        # High probability if: circular_wait AND high resource_utilization AND high wait_time
        if circular_wait == 1 and resource_utilization > 0.75 and avg_wait_time > 80:
            label = 1  # Deadlock
        elif circular_wait == 1 and resource_utilization > 0.6 and avg_wait_time > 60:
            label = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% deadlock
        elif resource_utilization > 0.85 and avg_wait_time > 100:
            label = np.random.choice([0, 1], p=[0.4, 0.6])  # 60% deadlock
        else:
            label = 0  # No deadlock

        X.append(features)
        y.append(label)

    return np.array(X), np.array(y)


def train_model():
    """Train Random Forest model for deadlock prediction"""
    print("Generating training data...")
    X, y = generate_synthetic_data(n_samples=2000)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    print(f"Deadlock cases in training: {sum(y_train)}/{len(y_train)} ({sum(y_train) / len(y_train) * 100:.1f}%)")

    # Train Random Forest Classifier
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )

    model.fit(X_train, y_train)

    # Evaluate model
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Deadlock', 'Deadlock']))

    # Feature importance
    feature_names = ['n_processes', 'n_resources', 'avg_wait_time', 'resource_util', 'circular_wait']
    importances = model.feature_importances_
    print("\nFeature Importances:")
    for name, importance in zip(feature_names, importances):
        print(f"  {name}: {importance:.4f}")

    # Save model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, 'deadlock_model.pkl')

    print(f"\nSaving model to: {model_path}")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    print("Model saved successfully!")
    return model


if __name__ == "__main__":
    print("=" * 50)
    print("AI Deadlock Detection - Model Training")
    print("=" * 50)
    train_model()

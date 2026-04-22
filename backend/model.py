"""
Zemythra - AI Core (Block A)
Static Risk Intelligence
"""

# import pandas as pd
# import numpy as np
# import joblib
# import shap

# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import roc_auc_score

# # -------------------------
# # Paths
# # -------------------------
# DATA_PATH = "backend/data/raw/clinical_risk_data.csv"
# MODEL_PATH = "backend/data/raw/risk_model.pkl"

# # -------------------------
# # Load Data
# # -------------------------
# def load_data():
#     df = pd.read_csv(DATA_PATH)
#     return df

# # -------------------------
# # Train Risk Model
# # -------------------------
# def train_model():
#     df = load_data()

#     X = df.drop(["patient_id", "disease"], axis=1)
#     y = df["disease"]

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.3, random_state=42
#     )

#     pipeline = Pipeline([
#         ("scaler", StandardScaler()),
#         ("clf", LogisticRegression(max_iter=1000))
#     ])

#     pipeline.fit(X_train, y_train)

#     preds = pipeline.predict_proba(X_test)[:, 1]
#     auc = roc_auc_score(y_test, preds)

#     print("ROC-AUC:", round(auc, 3))

#     joblib.dump(pipeline, MODEL_PATH)
#     return pipeline

# # -------------------------
# # Load Model
# # -------------------------
# def load_model():
#     return joblib.load(MODEL_PATH)

# # -------------------------
# # Uncertainty Estimation
# # -------------------------
# def predict_with_uncertainty(model, X, runs=25):
#     samples = []
#     for _ in range(runs):
#         samples.append(model.predict_proba(X)[:, 1])
#     samples = np.array(samples)
#     return samples.mean(axis=0), samples.std(axis=0)

# # -------------------------
# # Explainability
# # -------------------------
# def explain(model, X_sample):
#     explainer = shap.Explainer(model.named_steps["clf"], X_sample)
#     return explainer(X_sample)



# # =========================
# # UNIFIED AI INTERFACE
# # =========================

# def unified_predict(input_df):
#     """
#     Single entry point for risk prediction + uncertainty
#     Used by backend API
#     """
#     model = load_model()
#     risk, uncertainty = predict_with_uncertainty(model, input_df)
#     return float(risk[0]), float(uncertainty[0])

# # -------------------------
# # Manual Test
# # -------------------------
# if __name__ == "__main__":
#     model = train_model()


"""
Zemythra - AI Core (Block A)
Static Risk Intelligence
Updated for scikit-learn 1.8.0+
"""

import pandas as pd
import numpy as np
import joblib
import warnings
import shap

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

# Suppress version warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

DATA_PATH = "backend/data/raw/clinical_risk_data.csv"
MODEL_PATH = "backend/data/raw/risk_model.pkl"

def load_data():
    """Load clinical risk data from CSV"""
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✓ Data loaded: {df.shape[0]} samples, {df.shape[1]} features")
        return df
    except FileNotFoundError:
        print(f"✗ Error: {DATA_PATH} not found")
        raise

def train_model():
    """Train binary classification model"""
    print("\n🚀 Starting model training...")
    
    df = load_data()
    
    # Convert to binary classification
    df['disease'] = (df['disease'] > 0).astype(int)
    
    print(f"✓ Binary classification: {df['disease'].value_counts().to_dict()}")
    
    X = df.drop(["patient_id", "disease"], axis=1)
    y = df["disease"]
    
    print(f"✓ Features: {X.shape[1]}, Target: {y.shape[0]}")
    
    # Train-test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"✓ Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    
    # Create pipeline - EXPLICIT parameters for sklearn 1.8.0+
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',  # Explicit solver
            n_jobs=-1,       # Use all cores
            verbose=0
        ))
    ])
    
    print("\n🔄 Training pipeline...")
    pipeline.fit(X_train, y_train)
    print("✓ Training complete")
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    
    print(f"\n📊 Model Performance:")
    print(f"  ROC-AUC Score: {auc:.4f}")
    print(f"  Accuracy: {pipeline.score(X_test, y_test):.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Healthy', 'Disease'])}")
    
    # Save model
    try:
        joblib.dump(pipeline, MODEL_PATH)
        print(f"\n✓ Model saved to: {MODEL_PATH}")
    except Exception as e:
        print(f"✗ Error saving model: {e}")
        raise
    
    return pipeline

def load_model():
    """Load trained model with error handling"""
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✓ Model loaded successfully")
        return model
    except FileNotFoundError:
        print(f"✗ Model file not found: {MODEL_PATH}")
        print("  Please train first: python ai_core.py")
        raise

def predict_with_uncertainty(model, X, runs=10):
    """Estimate uncertainty through multiple predictions"""
    samples = []
    for _ in range(runs):
        proba = model.predict_proba(X)[:, 1]
        samples.append(proba)
    
    samples = np.array(samples)
    mean_pred = samples.mean(axis=0)
    std_pred = samples.std(axis=0)
    
    return mean_pred, std_pred

def explain(model, X_sample):
    """Generate SHAP explanations"""
    try:
        explainer = shap.Explainer(model.named_steps["clf"], X_sample)
        return explainer(X_sample)
    except Exception as e:
        print(f"⚠️  SHAP explanation failed: {e}")
        return None

def unified_predict(input_df):
    """
    Single entry point for risk prediction + uncertainty
    Used by backend API
    """
    try:
        model = load_model()
        risk, uncertainty = predict_with_uncertainty(model, input_df, runs=10)
        return float(risk[0]), float(uncertainty[0])
    except Exception as e:
        print(f"✗ Prediction error: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Zemythra AI Core - Model Training & Validation")
    print("=" * 60)
    
    try:
        # Train model
        model = train_model()
        
        # Load and test
        print("\n🧪 Testing model...")
        loaded_model = load_model()
        print("✓ Model loaded and ready for API")
        
        # Test prediction
        print("\n🔬 Test prediction:")
        test_data = pd.DataFrame([{
            'age': 55,
            'gender': 1,
            'sys_bp': 140,
            'dia_bp': 90,
            'glucose': 180,
            'cholesterol': 250,
            'bmi': 32.5,
            'heart_rate': 85
        }])
        
        risk, uncertainty = unified_predict(test_data)
        print(f"  Risk Score: {risk:.4f}")
        print(f"  Uncertainty: {uncertainty:.4f}")
        
        print("\n" + "=" * 60)
        print("✓ Training pipeline complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
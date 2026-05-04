import os
import pickle
import numpy as np

class MLPSynthesizer:
    def __init__(self, model_path="models/mlp_fusion.pkl"):
        self.model = None
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

    def score(self, features):
        # If MLP not available, fall back to rule-based fusion with enhanced accuracy
        if self.model is None:
            # Handle both old (5 features) and new (6 features) formats
            if len(features) == 5:
                weapon_conf, people_count, avg_conf, motion, density = features
                weapon_count = 1 if weapon_conf > 0 else 0
            else:
                weapon_conf, people_count, avg_conf, motion, density, weapon_count = features
            
            # Enhanced threat scoring with weapon-specific logic
            # Weapon confidence is heavily weighted
            weapon_threat = 1.0 - np.exp(-weapon_conf * 4.0)  # Increased from 3.0
            
            # Multiple weapons increase threat exponentially
            multi_weapon_bonus = min(weapon_count * 0.15, 0.5) if weapon_count > 1 else 0
            
            # Context: weapon + person = high threat
            context_threat = 0.0
            if people_count > 0 and weapon_conf > 0.3:
                context_threat = min(people_count / 3.0, 1.0) * 0.4
            
            # Activity and density
            activity = motion * 0.15 + density * 0.05
            
            # Combine all factors
            total_threat = weapon_threat + multi_weapon_bonus + context_threat + activity
            return float(np.clip(total_threat, 0.0, 1.0))
        else:
            try:
                s = self.model.predict_proba([features])[0][1]  # assume binary threat class
                return float(np.clip(s, 0.0, 1.0))
            except:
                # Fallback if MLP prediction fails
                return float(np.clip(features[0] / 2.0, 0.0, 1.0))

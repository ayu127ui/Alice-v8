import numpy as np

class ThreatScorer:
    def __init__(self, thresholds=None, buffer_size=5, enable_ppe_scoring=True):
        """
        Initialize threat scorer with weapon and PPE detection
        
        Args:
            thresholds: Class confidence thresholds
            buffer_size: Temporal smoothing buffer size
            enable_ppe_scoring: Include PPE violations in threat score
        """
        # Per-class thresholds - OPTIMIZED FOR GUN & KNIFE DETECTION
        self.thresholds = thresholds or {
            "person": 0.5,
            "knife": 0.35,      # Aggressive knife detection with shape verification
            "gun": 0.40,        # Aggressive gun detection with shape verification
            "pistol": 0.40,
            "rifle": 0.40,
            "sword": 0.35,
            "firearm": 0.40,
            "axe": 0.35,
            "fight": 0.7,
            "robbery": 0.7,
            "helmet": 0.5,
            "safety_vest": 0.5,
            "gloves": 0.5,
            "ppe_violation": 0.3
        }
        self.frame_buffer = []
        self.buffer_size = buffer_size
        self.enable_ppe_scoring = enable_ppe_scoring

    def score_frame(self, detections, ppe_violations=None):
        """
        Score frame based on weapon detections and PPE compliance
        
        Args:
            detections: List of weapon/person detections
            ppe_violations: List of PPE compliance violations
            
        Returns:
            Normalized threat score (0-1)
        """
        score = 0.0
        weapon_count = 0

        # Per-class confidence checks with weapon boost
        for det in detections:
            cls = det.get("class") or det.get("label")
            conf = det["conf"]
            
            if cls and cls.lower() in self.thresholds:
                threshold = self.thresholds[cls.lower()]
                
                if conf > threshold:
                    # WEAPON DETECTION: Significantly boost threat score
                    if cls.lower() in ["knife", "gun", "sword", "firearm", "pistol", "rifle", "axe"]:
                        # Heavy weight on weapon detection
                        score += conf * 2.0  # 100% boost for weapons
                        weapon_count += 1
                    elif cls.lower() == "person":
                        score += conf * 0.3  # Low base score for person
                    else:
                        score += conf

        # Contextual boost: weapon + person nearby = SEVERE THREAT
        persons = [d for d in detections if (d.get("class") or d.get("label")) == "person"]
        weapons = [d for d in detections if (d.get("class") or d.get("label")).lower() 
                   in ["knife", "gun", "sword", "firearm", "pistol", "rifle", "axe"]]
        
        if persons and weapons:
            score += 1.2  # Critical threat indicator
        
        # Multiple weapons exponential increase
        if weapon_count > 1:
            score += weapon_count * 0.4
        
        # PPE VIOLATION SCORING
        if self.enable_ppe_scoring and ppe_violations:
            ppe_threat = self._score_ppe_violations(ppe_violations)
            score += ppe_threat * 0.3  # PPE adds up to 30% of threat
        
        # Normalize score
        score = min(score, 1.0)

        # Temporal smoothing
        self.frame_buffer.append(score)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)

        avg_score = np.mean(self.frame_buffer)
        return avg_score

    def _score_ppe_violations(self, ppe_violations):
        """
        Calculate threat score from PPE violations
        
        Args:
            ppe_violations: List of PPE compliance checks
            
        Returns:
            PPE threat score (0-1)
        """
        if not ppe_violations:
            return 0.0
        
        total_violations = 0
        critical_count = 0
        
        for violation in ppe_violations:
            if not violation["all_required_met"]:
                missing_count = len(violation["missing_ppe"])
                compliance = violation["compliance_score"]
                
                # Higher threat for lower compliance
                violation_threat = (1.0 - compliance) * missing_count * 0.25
                
                # Critical: Missing helmet or vest (head/torso protection)
                if any(ppe in violation["missing_ppe"] for ppe in ["helmet", "hard_hat", "safety_vest", "vest"]):
                    violation_threat *= 1.5
                    critical_count += 1
                
                total_violations += violation_threat
        
        # Average violation threat
        if ppe_violations:
            ppe_threat = total_violations / len(ppe_violations)
            # Boost if multiple critical violations
            if critical_count > 1:
                ppe_threat *= 1.3
        else:
            ppe_threat = 0.0
        
        return min(ppe_threat, 1.0)

    def score_combined(self, detections, ppe_violations=None, violence_score=0.0):
        """
        Score combining weapon detection, PPE violations, and violence
        
        Args:
            detections: Weapon/person detections
            ppe_violations: PPE compliance violations
            violence_score: Violence detection score (0-1)
            
        Returns:
            Combined threat score (0-1)
        """
        # Base threat from weapons and PPE
        base_threat = self.score_frame(detections, ppe_violations)
        
        # Add violence component
        if violence_score > 0:
            base_threat = min(base_threat + violence_score * 0.4, 1.0)
        
        return base_threat


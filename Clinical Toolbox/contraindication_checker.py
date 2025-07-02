class ContraindicationChecker:
    """
    A deterministic, rule-based tool to check for absolute contraindications
    for proposed medications based on patient data.

    The logic is derived from the Lumina AI Health Institute's
    Medical Knowledge Base and Clinical Guidelines (Document 3).
    """

    def __init__(self):
        """
        Initializes the checker with a knowledge base of contraindication rules.
        This dictionary stores the core logic derived from Document 3.
        """
        self.contraindication_rules = {
            "metformin": {
                "egfr_threshold": 30,
                "message": "Metformin is contraindicated in patients with an eGFR < 30 mL/min/1.73m² (severe CKD)."
            }
            # Future contraindications for other drugs can be added here.
            # For example:
            # "glp-1_ra": {
            #     "history_condition": "medullary_thyroid_carcinoma",
            #     "message": "GLP-1 Receptor Agonists are contraindicated in patients with a personal or family history of Medullary Thyroid Carcinoma (MTC)."
            # }
        }

    def check_contraindications(self, egfr: int, proposed_medication: str) -> dict:
        """
        Checks a proposed medication against a patient's data for absolute contraindications.

        Args:
            egfr (int): The patient's estimated Glomerular Filtration Rate, a key measure of kidney function.
            proposed_medication (str): The name of the medication to check.

        Returns:
            dict: A dictionary containing a boolean flag and a list of contraindication messages.
                  - 'is_safe' (bool): True if no contraindications are found, False otherwise.
                  - 'messages' (list): A list of strings, each describing a specific contraindication.
                                       The list is empty if the medication is safe.
        """
        # Standardize the medication name to lowercase for reliable dictionary lookups.
        med_lower = proposed_medication.lower()
        
        # Initialize the output structure. We assume the medication is safe until a rule proves otherwise.
        output = {
            "is_safe": True,
            "messages": []
        }

        # --- Rule Check for Metformin ---
        # This is the primary example from the project description and Document 3.
        if med_lower == "metformin":
            rule = self.contraindication_rules.get(med_lower)
            if rule and egfr < rule["egfr_threshold"]:
                # The patient's eGFR is below the critical threshold for Metformin.
                # This indicates severe Chronic Kidney Disease (CKD).
                # According to the 'Metformin Profile' in Document 3, this is an absolute contraindication.
                output["is_safe"] = False
                output["messages"].append(rule["message"])

        # --- Placeholder for Future Rule Checks ---
        # Additional 'if' or 'elif' blocks for other medications would go here.
        # For example, checking for a history of pancreatitis with GLP-1 RAs, etc.
        # if med_lower in ["semaglutide", "dulaglutide", "liraglutide"]:
        #     # Fictional example: check for a history of pancreatitis
        #     if patient_history.get("pancreatitis"):
        #         output["is_safe"] = False
        #         output["messages"].append("Use GLP-1 RAs with caution in patients with a history of pancreatitis.")

        return output

# --- Example Usage ---

# 1. Create an instance of the checker.
checker = ContraindicationChecker()

# 2. Define patient data and the proposed medication.

# Scenario 1: A patient with severe kidney disease (eGFR = 25).
patient_egfr_severe_ckd = 25
proposed_med_metformin = "Metformin"

# Check for contraindications.
result1 = checker.check_contraindications(
    egfr=patient_egfr_severe_ckd,
    proposed_medication=proposed_med_metformin
)
print(f"Checking '{proposed_med_metformin}' for patient with eGFR {patient_egfr_severe_ckd}:")
print(result1)
# Expected Output: {'is_safe': False, 'messages': ["Metformin is contraindicated..."]}
print("-" * 20)


# Scenario 2: A patient with healthy kidney function (eGFR = 95).
patient_egfr_healthy = 95

# Check the same medication for this patient.
result2 = checker.check_contraindications(
    egfr=patient_egfr_healthy,
    proposed_medication=proposed_med_metformin
)
print(f"Checking '{proposed_med_metformin}' for patient with eGFR {patient_egfr_healthy}:")
print(result2)
# Expected Output: {'is_safe': True, 'messages': []}
print("-" * 20)


# Scenario 3: Checking a different medication for which no rules are currently defined.
proposed_med_other = "Empagliflozin"
result3 = checker.check_contraindications(
    egfr=patient_egfr_severe_ckd, # Using the same patient with severe CKD
    proposed_medication=proposed_med_other
)
print(f"Checking '{proposed_med_other}' for patient with eGFR {patient_egfr_severe_ckd}:")
print(result3)
# Expected Output: {'is_safe': True, 'messages': []}
print("-" * 20)


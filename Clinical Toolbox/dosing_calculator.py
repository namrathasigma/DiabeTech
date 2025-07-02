class DosingCalculator:
    """
    A collection of non-AI Python functions for safety-critical
    medication dosing calculations. The logic herein is based on the
    Lumina AI Health Institute's Medical Knowledge Base (Document 3).
    """

    def __init__(self):
        # Data sourced from 'SGLT2 Inhibitor Profiles' in the knowledge base
        self.sglt2i_doses = {
            "empagliflozin": {"doses": ["10mg", "25mg"], "starting_dose": "10mg"},
            "dapagliflozin": {"doses": ["5mg", "10mg"], "starting_dose": "5mg"},
            "canagliflozin": {"doses": ["100mg", "300mg"], "starting_dose": "100mg"},
            "ertugliflozin": {"doses": ["5mg", "15mg"], "starting_dose": "5mg"}
        }
        # Data sourced from 'GLP-1 Receptor Agonists Profiles' in the knowledge base
        self.glp1ra_doses = {
            "semaglutide (ozempic)": {"starting_dose": "0.25mg", "frequency": "weekly"},
            "semaglutide (rybelsus)": {"starting_dose": "3mg", "frequency": "daily oral"},
            "dulaglutide": {"starting_dose": "0.75mg", "frequency": "weekly"},
            "liraglutide": {"starting_dose": "0.6mg", "frequency": "daily"},
            "tirzepatide": {"starting_dose": "2.5mg", "frequency": "weekly"}
        }

    def calculate_metformin_dose(self, current_dose_mg: int, is_extended_release: bool = False) -> str:
        """
        Calculates starting and titration doses for Metformin based on the
        'Metformin Profile' and 'Medication Algorithm' sections of Document 3.
        """
        if current_dose_mg == 0:
            # Per guideline, the standard starting dose is 500mg.
            return "Starting dose: 500mg daily or BID with meals."

        # Maximum dose is 2000mg for ER and 2550mg for IR, per Metformin Profile.
        max_dose = 2000 if is_extended_release else 2550
        next_dose = current_dose_mg + 500

        if current_dose_mg >= max_dose:
            return f"Max dose of {max_dose}mg reached."
        else:
            # Titration logic follows the ADA guideline to increase by 500mg weekly.
            return f"Recommended next titration: Increase dose to {min(next_dose, max_dose)}mg."

    def get_agent_starting_dose(self, medication_name: str) -> str:
        """
        Provides the starting dose for SGLT2i and GLP-1 RA medications
        using the data in the SGLT2i and GLP-1 Agonist profile sections.
        """
        med_name_lower = medication_name.lower()
        # Check against SGLT2 inhibitor dictionary
        if med_name_lower in self.sglt2i_doses:
            dose_info = self.sglt2i_doses[med_name_lower]
            return f"Starting dose for {medication_name}: {dose_info['starting_dose']} daily."
        # Check against GLP-1 receptor agonist dictionary
        elif med_name_lower in self.glp1ra_doses:
            dose_info = self.glp1ra_doses[med_name_lower]
            return f"Starting dose for {medication_name}: {dose_info['starting_dose']} {dose_info['frequency']}."
        else:
            return "Dosing information not found for this medication."

    def calculate_basal_insulin_initiation_dose(self, weight_kg: float) -> str:
        """
        Calculates the initial daily dose for basal insulin.
        Logic is derived from the 'Insulin Initiation and Titration' section.
        """
        # Guideline specifies a start of 10 units or a weight-based calculation.
        dose_range_lower = 0.1 * weight_kg
        dose_range_upper = 0.2 * weight_kg
        return f"Starting dose: 10 units OR {dose_range_lower:.1f}-{dose_range_upper:.1f} units daily."

    def calculate_basal_insulin_titration(self, fasting_blood_glucose: int, current_dose: int) -> str:
        """
        Calculates the adjustment for a basal insulin dose based on fasting glucose.
        Logic is based on the titration rules in the 'InsulinAlgorithms' class.
        """
        # Titration rules target a fasting blood glucose of 80-130 mg/dL.
        if fasting_blood_glucose > 180:
            adjustment = 4
            new_dose = current_dose + adjustment
            return f"FBG > 180 mg/dL. Increase dose by {adjustment} units to {new_dose} units."
        elif 140 <= fasting_blood_glucose <= 180:
            adjustment = 2
            new_dose = current_dose + adjustment
            return f"FBG is 140-180 mg/dL. Increase dose by {adjustment} units to {new_dose} units."
        elif fasting_blood_glucose < 80:
            adjustment = -2
            new_dose = max(0, current_dose + adjustment)
            return f"FBG < 80 mg/dL. Decrease dose by 2 units to {new_dose} units."
        else: # FBG is within the 80-130 mg/dL target range
            return "FBG is within target range (80-130 mg/dL). No change in dose."

    def calculate_prandial_insulin_initiation_dose(self, basal_dose: int) -> str:
        """
        Calculates the starting dose for prandial insulin.
        Logic follows the 'Prandial Addition' rules in the guidelines.
        """
        # Prandial insulin starts at 4 units or 10% of the current basal dose.
        dose_from_basal = 0.10 * basal_dose
        return f"Starting dose: 4 units OR {dose_from_basal:.1f} units with the largest meal."
import math

class DosingCalculator:
    """
    A calculator for medication dosing in both Type 1 and Type 2 Diabetes.
    """

    def __init__(self):
        """
        Initializes the calculator
        """
        # --- Data for Type 2 Diabetes Medications ---

        # Sourced from 'SGLT2 Inhibitor Profiles'
        self.sglt2i_doses = {
            "empagliflozin": {"doses": ["10mg", "25mg"], "starting_dose": "10mg"},
            "dapagliflozin": {"doses": ["5mg", "10mg"], "starting_dose": "5mg"},
            "canagliflozin": {"doses": ["100mg", "300mg"], "starting_dose": "100mg"},
            "ertugliflozin": {"doses": ["5mg", "15mg"], "starting_dose": "5mg"}
        }
        # Sourced from 'GLP-1 Receptor Agonists Profiles'
        self.glp1ra_doses = {
            "semaglutide (ozempic)": {"starting_dose": "0.25mg", "frequency": "weekly"},
            "semaglutide (rybelsus)": {"starting_dose": "3mg", "frequency": "daily oral"},
            "dulaglutide": {"starting_dose": "0.75mg", "frequency": "weekly"},
            "liraglutide": {"starting_dose": "0.6mg", "frequency": "daily"},
            "tirzepatide": {"starting_dose": "2.5mg", "frequency": "weekly"}
        }

        # --- Constants for Type 1 Diabetes Calculations ---

        # Sourced from 'Type 1 Insulin Algorithms' class
        self.t1d_tdd_factors = {
            "initial": {"min": 0.4, "max": 0.5},
            "honeymoon": {"min": 0.2, "max": 0.4},
            "established": {"min": 0.5, "max": 1.0},
            "insulin_resistant": {"min": 1.0, "max": 100.0} # Max is now hard-coded
        }
        self.t1d_basal_bolus_split = {"basal_percentage": 0.4, "bolus_percentage": 0.6}
        self.t1d_carb_ratio_constant = {"rapid_acting": 500, "regular": 450}
        self.t1d_correction_factor_constant = {"rapid_acting": 1800, "regular": 1700}


    # ==========================================================================
    # == TYPE 2 DIABETES DOSING FUNCTIONS
    # ==========================================================================

    def calculate_metformin_dose(self, current_dose_mg: int, is_extended_release: bool = False) -> str:
        """
        Calculates starting and titration doses for Metformin for Type 2 Diabetes.

        Args:
            current_dose_mg (int): The patient's current daily dose of Metformin in mg.
                                   Use 0 for a new patient.
            is_extended_release (bool): True if the formulation is extended-release (ER/XR),
                                        False for immediate-release (IR). Defaults to False.

        Returns:
            str: A human-readable string with the recommended starting or titration dose.

        Medical Logic (from Document 3, 'Metformin Profile'):
        - Starting Dose: 500mg daily or BID.
        - Titration: Increase by 500mg weekly.
        - Max Dose (IR): 2550mg.
        - Max Dose (ER): 2000mg.
        """
        if current_dose_mg == 0:
            return "Starting dose: 500mg daily or BID with meals."

        max_dose = 2000 if is_extended_release else 2550
        next_dose = current_dose_mg + 500

        if current_dose_mg >= max_dose:
            return f"Max dose of {max_dose}mg reached."
        else:
            return f"Recommended next titration: Increase dose to {min(next_dose, max_dose)}mg."

    def get_t2d_agent_starting_dose(self, medication_name: str) -> str:
        """
        Provides the starting dose for common non-insulin T2D medications.

        Args:
            medication_name (str): The name of the medication (case-insensitive).

        Returns:
            str: A string with the recommended starting dose and frequency.

        Medical Logic (from Document 3, 'SGLT2 Inhibitor' and 'GLP-1 Agonist' Profiles):
        - Looks up the provided medication name in the internal knowledge base
          and returns the stored starting dose and frequency.
        """
        med_name_lower = medication_name.lower()
        if med_name_lower in self.sglt2i_doses:
            dose_info = self.sglt2i_doses[med_name_lower]
            return f"Starting dose for {medication_name}: {dose_info['starting_dose']} daily."
        elif med_name_lower in self.glp1ra_doses:
            dose_info = self.glp1ra_doses[med_name_lower]
            return f"Starting dose for {medication_name}: {dose_info['starting_dose']} {dose_info['frequency']}."
        else:
            return "Dosing information not found for this medication."

    def calculate_t2d_basal_insulin_initiation(self, weight_kg: float) -> str:
        """
        Calculates the initial daily dose for basal insulin for Type 2 Diabetes.

        Args:
            weight_kg (float): The patient's weight in kilograms.

        Returns:
            str: A string detailing the recommended starting dose options.

        Medical Logic (from Document 3, 'InsulinAlgorithms' class):
        - Starting Dose: "10 units or 0.1-0.2 units/kg".
        """
        dose_range_lower = 0.1 * weight_kg
        dose_range_upper = 0.2 * weight_kg
        return f"Starting dose: 10 units OR {dose_range_lower:.1f}-{dose_range_upper:.1f} units daily."

    def calculate_t2d_basal_insulin_titration(self, fasting_blood_glucose: int, current_dose: int) -> str:
        """
        Calculates the adjustment for a T2D basal insulin dose based on fasting glucose.

        Args:
            fasting_blood_glucose (int): The patient's fasting blood glucose in mg/dL.
            current_dose (int): The patient's current daily dose of basal insulin.

        Returns:
            str: A string recommending the dose adjustment.

        Medical Logic (from Document 3, 'InsulinAlgorithms' class, target 80-130 mg/dL):
        - FBG > 180: Increase by 4 units.
        - FBG 140-180: Increase by 2 units.
        - FBG < 80: Decrease by 2 units.
        """
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
            new_dose = max(0, current_dose + adjustment) # Safety clamp to prevent negative dose
            return f"FBG < 80 mg/dL. Decrease dose by 2 units to {new_dose} units."
        else:
            return "FBG is within target range (80-130 mg/dL). No change in dose."

    def calculate_t2d_prandial_insulin_initiation(self, basal_dose: int) -> str:
        """
        Calculates the starting dose for prandial (mealtime) insulin for Type 2 Diabetes.

        Args:
            basal_dose (int): The patient's total daily dose of basal insulin.

        Returns:
            str: A string with the recommended starting dose options.

        Medical Logic (from Document 3, 'prandial_addition' rules):
        - Starting Dose: "4 units or 10% of basal dose" with the largest meal.
        """
        dose_from_basal = 0.10 * basal_dose
        return f"Starting dose: 4 units OR {dose_from_basal:.1f} units with the largest meal."


    # ==========================================================================
    # == TYPE 1 DIABETES DOSING FUNCTIONS
    # ==========================================================================

    def calculate_t1d_total_daily_dose(self, weight_kg: float, status: str = "initial") -> str:
        """
        Calculates the estimated Total Daily Dose (TDD) of insulin for Type 1 Diabetes.

        Args:
            weight_kg (float): The patient's weight in kilograms.
            status (str): The patient's clinical status. Must be one of:
                          'initial', 'honeymoon', 'established', 'insulin_resistant'.
                          Defaults to 'initial'.

        Returns:
            str: A string describing the calculated TDD range in units.

        Medical Logic (from Document 3, 'Type1InsulinAlgorithms' class):
        - Calculates TDD based on weight and a factor determined by clinical status.
        """
        status_lower = status.lower()
        if status_lower not in self.t1d_tdd_factors:
            return f"Error: Invalid status '{status}'. Must be one of {list(self.t1d_tdd_factors.keys())}."

        factors = self.t1d_tdd_factors[status_lower]
        tdd_lower = factors["min"] * weight_kg
        tdd_upper = factors["max"] * weight_kg
        return f"Estimated TDD for '{status}' status: {tdd_lower:.1f}-{tdd_upper:.1f} units/day."

    def calculate_t1d_basal_bolus_split(self, total_daily_dose: float) -> str:
        """
        Splits the Total Daily Dose (TDD) into basal and bolus components for T1D.

        Args:
            total_daily_dose (float): The patient's estimated TDD of insulin.

        Returns:
            str: A string detailing the split in units for basal and bolus insulin.

        Medical Logic (from Document 3, 'basal_bolus_split' rules):
        - Basal: 40-50% of TDD.
        - Bolus: 50-60% of TDD.
        - This implementation uses a 40% basal / 60% bolus split for a conservative start.
        """
        basal_dose = self.t1d_basal_bolus_split["basal_percentage"] * total_daily_dose
        bolus_dose = self.t1d_basal_bolus_split["bolus_percentage"] * total_daily_dose
        return (f"Basal dose: {basal_dose:.1f} units/day. "
                f"Total Bolus dose: {bolus_dose:.1f} units/day (to be divided among meals).")

    def calculate_t1d_insulin_to_carb_ratio(self, total_daily_dose: float, is_rapid_acting: bool = True) -> str:
        """
        Calculates the Insulin-to-Carbohydrate Ratio (ICR) for T1D.

        Args:
            total_daily_dose (float): The patient's estimated TDD of insulin.
            is_rapid_acting (bool): True if the patient uses rapid-acting insulin (e.g., Lispro),
                                    False for regular human insulin. Defaults to True.

        Returns:
            str: A string stating the ICR.

        Medical Logic (from Document 3, 'carb_ratios' calculation):
        - ICR = 500 / TDD for rapid-acting insulin.
        - ICR = 450 / TDD for regular insulin.
        """
        constant = self.t1d_carb_ratio_constant["rapid_acting"] if is_rapid_acting else self.t1d_carb_ratio_constant["regular"]
        icr = constant / total_daily_dose
        return f"Insulin-to-Carb Ratio (ICR): 1 unit of insulin covers {math.ceil(icr)} grams of carbohydrates."

    def calculate_t1d_correction_factor(self, total_daily_dose: float, is_rapid_acting: bool = True) -> str:
        """
        Calculates the Correction Factor (CF) or Insulin Sensitivity Factor (ISF) for T1D.

        Args:
            total_daily_dose (float): The patient's estimated TDD of insulin.
            is_rapid_acting (bool): True if the patient uses rapid-acting insulin,
                                    False for regular human insulin. Defaults to True.

        Returns:
            str: A string stating the Correction Factor.

        Medical Logic (from Document 3, 'correction_factors' calculation):
        - CF = 1800 / TDD for rapid-acting insulin.
        - CF = 1700 / TDD for regular insulin.
        """
        constant = self.t1d_correction_factor_constant["rapid_acting"] if is_rapid_acting else self.t1d_correction_factor_constant["regular"]
        cf = constant / total_daily_dose
        return f"Correction Factor (CF): 1 unit of insulin will lower blood glucose by approximately {math.ceil(cf)} mg/dL."
Technical Documentation: DosingCalculator
1. Overview
The DosingCalculator is a deterministic Python class designed for safety-critical medication dosing calculations. It provides a reliable, non-AI tool for other agents and services within the clinical decision support system.
All logic and data are strictly derived from the Lumina AI Health Institute's Medical Knowledge Base and Clinical Guidelines (Document 3). This ensures that all calculations are transparent, verifiable, and based on approved clinical standards.
2. Initialization
To use the calculator, first create an instance of the class. It does not require any parameters upon initialization.
# Create an instance of the calculator
calculator = DosingCalculator()


3. API Reference (Methods)
calculate_metformin_dose()
Calculates the starting or next titration dose for Metformin.
Parameters:
current_dose_mg (int): The patient's current daily dose of Metformin in milligrams. Use 0 for a new patient.
is_extended_release (bool): Set to True if the formulation is extended-release. Defaults to False.
Returns: (str) A human-readable string with the recommended dose.
Example Usage:
# Get starting dose
print(calculator.calculate_metformin_dose(current_dose_mg=0))
# > Starting dose: 500mg daily or BID with meals.

# Titrate an existing dose
print(calculator.calculate_metformin_dose(current_dose_mg=1000, is_extended_release=True))
# > Recommended next titration: Increase dose to 1500mg.


get_agent_starting_dose()
Retrieves the standard starting dose for common SGLT2 inhibitor and GLP-1 receptor agonist medications.
Parameters:
medication_name (str): The name of the medication (case-insensitive).
Returns: (str) A string with the recommended starting dose and frequency.
Example Usage:
print(calculator.get_agent_starting_dose("Empagliflozin"))
# > Starting dose for Empagliflozin: 10mg daily.

print(calculator.get_agent_starting_dose("tirzepatide"))
# > Starting dose for tirzepatide: 2.5mg weekly.


calculate_basal_insulin_initiation_dose()
Calculates the initial daily starting dose for basal insulin, providing either a fixed dose or a weight-based range.
Parameters:
weight_kg (float): The patient's weight in kilograms.
Returns: (str) A string detailing the recommended starting dose options.
Example Usage:
print(calculator.calculate_basal_insulin_initiation_dose(weight_kg=90))
# > Starting dose: 10 units OR 9.0-18.0 units daily.


calculate_basal_insulin_titration()
Recommends an adjustment to a patient's basal insulin dose based on their fasting blood glucose (FBG) level.
Parameters:
fasting_blood_glucose (int): The patient's fasting blood glucose reading in mg/dL.
current_dose (int): The patient's current daily dose of basal insulin.
Returns: (str) A string recommending the dose adjustment.
Example Usage:
# FBG is high, needs increase
print(calculator.calculate_basal_insulin_titration(fasting_blood_glucose=192, current_dose=20))
# > FBG > 180 mg/dL. Increase dose by 4 units to 24 units.

# FBG is in range
print(calculator.calculate_basal_insulin_titration(fasting_blood_glucose=110, current_dose=20))
# > FBG is within target range (80-130 mg/dL). No change in dose.


calculate_prandial_insulin_initiation_dose()
Calculates the starting dose for prandial (mealtime) insulin, which is typically added when basal insulin alone is not sufficient.
Parameters:
basal_dose (int): The patient's total daily dose of basal insulin.
Returns: (str) A string with the recommended starting dose options for prandial insulin.
Example Usage:
print(calculator.calculate_prandial_insulin_initiation_dose(basal_dose=30))
# > Starting dose: 4 units OR 3.0 units with the largest meal.

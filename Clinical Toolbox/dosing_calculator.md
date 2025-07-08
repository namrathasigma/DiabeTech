# User Guide: `DosingCalculator`

## 1. Overview

The `DosingCalculator` is a comprehensive, deterministic, rule-based tool for calculating medication doses for patients with **Type 1** and **Type 2 Diabetes**. It is designed to be a reliable component within a larger clinical decision support system.

All logic and data are strictly derived from the official clinical guidelines found in **Document 3: Medical Knowledge Base and Clinical Guidelines**.

This document provides a guide on how to use each function within the class, with clear examples for various clinical situations.

## 2. Initialization

To begin, import the `DosingCalculator` class from its file (`dosing_calculator.py`) and create an instance. No parameters are needed for initialization.

```python
# The DosingCalculator class is located in the dosing_calculator.py file.
from dosing_calculator import DosingCalculator

# Create an instance of the calculator
calculator = DosingCalculator()
```

## 3. Type 2 Diabetes Dosing Functions

These functions correspond to the decision points in the ADA Type 2 Diabetes treatment algorithm.

---

### `calculate_metformin_dose`
**Job:** Calculates starting or titration doses for Metformin.

* **`Args`**:
    * `current_dose_mg` (int): Patient's current daily dose. Use `0` if new to Metformin.
    * `is_extended_release` (bool): `True` for XR/ER versions, `False` for immediate-release.
* **`Returns`**: (str) A recommendation.

**Examples:**

```python
# Scenario: A patient newly diagnosed with Type 2 Diabetes.
new_patient_dose = calculator.calculate_metformin_dose(current_dose_mg=0)
print(new_patient_dose)
# Expected Output: "Starting dose: 500mg daily or BID with meals."

# Scenario: A patient is on 1000mg of Metformin XR and needs their dose increased.
titration_dose = calculator.calculate_metformin_dose(current_dose_mg=1000, is_extended_release=True)
print(titration_dose)
# Expected Output: "Recommended next titration: Increase dose to 1500mg."
```

---

### `get_t2d_agent_starting_dose`
**Job:** Retrieves the starting dose for common non-insulin medications used after Metformin.

* **`Args`**:
    * `medication_name` (str): Name of the drug (e.g., "Empagliflozin", "Tirzepatide").
* **`Returns`**: (str) The starting dose and frequency.

**Examples:**

```python
# Scenario: A patient with heart failure needs to start an SGLT2 inhibitor.
sglt2i_dose = calculator.get_t2d_agent_starting_dose("Dapagliflozin")
print(sglt2i_dose)
# Expected Output: "Starting dose for Dapagliflozin: 5mg daily."

# Scenario: A patient's primary goal is weight loss, so they will start a GLP-1 RA.
glp1_dose = calculator.get_t2d_agent_starting_dose("semaglutide (ozempic)")
print(glp1_dose)
# Expected Output: "Starting dose for semaglutide (ozempic): 0.25mg weekly."
```

---

### `calculate_t2d_basal_insulin_initiation`
**Job:** Calculates the starting dose for long-acting (basal) insulin.

* **`Args`**:
    * `weight_kg` (float): Patient's weight in kilograms.
* **`Returns`**: (str) The recommended starting dose options.

**Example:**

```python
# Scenario: A 100kg patient with Type 2 Diabetes needs to start basal insulin.
basal_start_dose = calculator.calculate_t2d_basal_insulin_initiation(weight_kg=100)
print(basal_start_dose)
# Expected Output: "Starting dose: 10 units OR 10.0-20.0 units daily."
```

---

### `calculate_t2d_basal_insulin_titration`
**Job:** Adjusts the basal insulin dose based on fasting blood glucose (FBG).

* **`Args`**:
    * `fasting_blood_glucose` (int): Patient's FBG reading in mg/dL.
    * `current_dose` (int): Patient's current daily basal insulin dose.
* **`Returns`**: (str) The recommended adjustment.

**Examples:**

```python
# Scenario: Patient's FBG is 195 mg/dL (too high) on 20 units of basal insulin.
high_fbg_adjustment = calculator.calculate_t2d_basal_insulin_titration(fasting_blood_glucose=195, current_dose=20)
print(high_fbg_adjustment)
# Expected Output: "FBG > 180 mg/dL. Increase dose by 4 units to 24 units."

# Scenario: Patient's FBG is 75 mg/dL (too low) on 15 units of basal insulin.
low_fbg_adjustment = calculator.calculate_t2d_basal_insulin_titration(fasting_blood_glucose=75, current_dose=15)
print(low_fbg_adjustment)
# Expected Output: "FBG < 80 mg/dL. Decrease dose by 2 units to 13 units."
```

---

### `calculate_t2d_prandial_insulin_initiation`
**Job:** Calculates the starting dose for mealtime (prandial) insulin.

* **`Args`**:
    * `basal_dose` (int): Patient's total daily dose of basal insulin.
* **`Returns`**: (str) The recommended starting dose options.

**Example:**

```python
# Scenario: A patient on 50 units of basal insulin needs to add mealtime insulin.
prandial_start_dose = calculator.calculate_t2d_prandial_insulin_initiation(basal_dose=50)
print(prandial_start_dose)
# Expected Output: "Starting dose: 4 units OR 5.0 units with the largest meal."
```

---

## 4. Type 1 Diabetes Dosing Functions

These functions are designed to be used in a sequence to create a complete insulin regimen for a patient with Type 1 Diabetes.

### The Complete T1D Workflow Example

This example shows how to use all the T1D functions together for a single patient.

**Scenario:** A 65kg patient was diagnosed some time ago and is considered to have "established" Type 1 Diabetes.

#### Step 1: Calculate Total Daily Dose (TDD)
**Function:** `calculate_t1d_total_daily_dose`

```python
patient_weight = 65
patient_status = "established"

tdd_range = calculator.calculate_t1d_total_daily_dose(weight_kg=patient_weight, status=patient_status)
print(tdd_range)
# Expected Output: "Estimated TDD for 'established' status: 32.5-65.0 units/day."

# A clinician would select a starting TDD from this range for the subsequent steps.
# For this example, a TDD of 45 units is used.
chosen_tdd = 45.0
```

#### Step 2: Split TDD into Basal and Bolus
**Function:** `calculate_t1d_basal_bolus_split`

```python
split_doses = calculator.calculate_t1d_basal_bolus_split(total_daily_dose=chosen_tdd)
print(split_doses)
# Expected Output: "Basal dose: 18.0 units/day. Total Bolus dose: 27.0 units/day (to be divided among meals)."
```

#### Step 3: Calculate Insulin-to-Carb Ratio (ICR)
**Function:** `calculate_t1d_insulin_to_carb_ratio`

```python
# The calculation uses the default for rapid-acting insulin.
carb_ratio = calculator.calculate_t1d_insulin_to_carb_ratio(total_daily_dose=chosen_tdd)
print(carb_ratio)
# Expected Output: "Insulin-to-Carb Ratio (ICR): 1 unit of insulin covers 12 grams of carbohydrates."
```

#### Step 4: Calculate Correction Factor (CF)
**Function:** `calculate_t1d_correction_factor`

```python
# The calculation uses the default for rapid-acting insulin.
correction_factor = calculator.calculate_t1d_correction_factor(total_daily_dose=chosen_tdd)
print(correction_factor)
# Expected Output: "Correction Factor (CF): 1 unit of insulin will lower blood glucose by approximately 35 mg/dL."

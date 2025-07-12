#!/usr/bin/env python3
"""
Diabetes Database Population Script
Populates PostgreSQL database with synthetic patient data covering 5 key phenotypes:
1. Type 1 Diabetes - Autoimmune
2. Type 2 Diabetes - Insulin Resistant
3. Gestational Diabetes
4. MODY (Maturity Onset Diabetes of the Young)
5. LADA (Latent Autoimmune Diabetes in Adults)
"""

import psycopg2
import random
from datetime import datetime, date, timedelta
import uuid
from faker import Faker
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Faker for generating realistic data
fake = Faker()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'diabetes_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def connect_to_db():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def insert_phenotypes(conn):
    """Insert the 5 key diabetes phenotypes"""
    phenotypes = [
        {
            'name': 'Type 1 Diabetes - Autoimmune',
            'description': 'Autoimmune destruction of pancreatic beta cells leading to absolute insulin deficiency',
            'criteria': 'Positive autoantibodies, C-peptide < 0.6 ng/mL, typically diagnosed < 30 years',
            'severity': 'Severe'
        },
        {
            'name': 'Type 2 Diabetes - Insulin Resistant',
            'description': 'Insulin resistance with relative insulin deficiency, often associated with obesity',
            'criteria': 'Insulin resistance, elevated C-peptide, typically diagnosed > 40 years, family history',
            'severity': 'Moderate'
        },
        {
            'name': 'Gestational Diabetes',
            'description': 'Diabetes diagnosed during pregnancy, usually resolves postpartum',
            'criteria': 'Diagnosed during pregnancy, OGTT > 140 mg/dL, typically resolves after delivery',
            'severity': 'Mild'
        },
        {
            'name': 'MODY (Maturity Onset Diabetes of the Young)',
            'description': 'Monogenic form of diabetes with autosomal dominant inheritance',
            'criteria': 'Family history, diagnosed 25-45 years, non-obese, C-peptide present',
            'severity': 'Mild'
        },
        {
            'name': 'LADA (Latent Autoimmune Diabetes in Adults)',
            'description': 'Slowly progressive autoimmune diabetes in adults',
            'criteria': 'Positive autoantibodies, age > 30, gradual progression to insulin requirement',
            'severity': 'Moderate'
        }
    ]
    
    cursor = conn.cursor()
    phenotype_ids = {}
    
    for phenotype in phenotypes:
        cursor.execute("""
            INSERT INTO phenotypes (phenotype_name, description, criteria, severity_level, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (phenotype_name) DO NOTHING
            RETURNING phenotype_id;
        """, (
            phenotype['name'],
            phenotype['description'],
            phenotype['criteria'],
            phenotype['severity'],
            datetime.now()
        ))
        result = cursor.fetchone()
        if result:
            phenotype_ids[phenotype['name']] = result[0]
        else:
            cursor.execute("SELECT phenotype_id FROM phenotypes WHERE phenotype_name = %s", (phenotype['name'],))
            phenotype_ids[phenotype['name']] = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    return phenotype_ids

def generate_patient_data(phenotype_name):
    """Generate patient data based on phenotype characteristics"""
    patient = {}
    
    # Base demographics
    patient['first_name'] = fake.first_name()
    patient['last_name'] = fake.last_name()
    patient['gender'] = random.choice(['Male', 'Female'])
    patient['ethnicity'] = random.choice(['Caucasian', 'African American', 'Hispanic', 'Asian', 'Other'])
    # Format phone numbers: digits only, max 20 chars
    patient['phone'] = ''.join(filter(str.isdigit, fake.phone_number()))[:20]
    patient['email'] = fake.email()
    patient['address'] = fake.address()
    patient['emergency_contact_name'] = fake.name()
    patient['emergency_contact_phone'] = ''.join(filter(str.isdigit, fake.phone_number()))[:20]
    patient['insurance_provider'] = random.choice(['Blue Cross', 'Aetna', 'Cigna', 'UnitedHealth', 'Kaiser'])
    # Format insurance_id: alphanumeric, max 20 chars
    patient['insurance_id'] = ''.join(filter(str.isalnum, fake.uuid4()))[:20].upper()
    
    # Phenotype-specific characteristics
    if phenotype_name == 'Type 1 Diabetes - Autoimmune':
        patient['date_of_birth'] = fake.date_between(start_date='-40y', end_date='-15y')
        patient['height_cm'] = random.uniform(150, 190)
        patient['weight_kg'] = random.uniform(50, 80)  # Typically lean
        patient['bmi'] = round(patient['weight_kg'] / ((patient['height_cm']/100) ** 2), 2)
        
    elif phenotype_name == 'Type 2 Diabetes - Insulin Resistant':
        patient['date_of_birth'] = fake.date_between(start_date='-70y', end_date='-40y')
        patient['height_cm'] = random.uniform(150, 190)
        patient['weight_kg'] = random.uniform(70, 120)  # Often overweight
        patient['bmi'] = round(patient['weight_kg'] / ((patient['height_cm']/100) ** 2), 2)
        
    elif phenotype_name == 'Gestational Diabetes':
        patient['gender'] = 'Female'  # Only females can have gestational diabetes
        patient['date_of_birth'] = fake.date_between(start_date='-45y', end_date='-25y')
        patient['height_cm'] = random.uniform(150, 175)
        patient['weight_kg'] = random.uniform(60, 100)
        patient['bmi'] = round(patient['weight_kg'] / ((patient['height_cm']/100) ** 2), 2)
        
    elif phenotype_name == 'MODY (Maturity Onset Diabetes of the Young)':
        patient['date_of_birth'] = fake.date_between(start_date='-50y', end_date='-25y')
        patient['height_cm'] = random.uniform(150, 190)
        patient['weight_kg'] = random.uniform(50, 85)  # Typically normal weight
        patient['bmi'] = round(patient['weight_kg'] / ((patient['height_cm']/100) ** 2), 2)
        
    elif phenotype_name == 'LADA (Latent Autoimmune Diabetes in Adults)':
        patient['date_of_birth'] = fake.date_between(start_date='-60y', end_date='-30y')
        patient['height_cm'] = random.uniform(150, 190)
        patient['weight_kg'] = random.uniform(55, 90)  # Often normal weight
        patient['bmi'] = round(patient['weight_kg'] / ((patient['height_cm']/100) ** 2), 2)
    
    return patient

def insert_patients_and_phenotypes(conn, phenotype_ids):
    """Insert 20 patients with phenotype assignments (4 patients per phenotype)"""
    cursor = conn.cursor()
    
    for phenotype_name, phenotype_id in phenotype_ids.items():
        print(f"Creating patients for phenotype: {phenotype_name}")
        
        for i in range(4):  # 4 patients per phenotype
            # Generate patient data
            patient_data = generate_patient_data(phenotype_name)
            
            # Insert patient
            cursor.execute("""
                INSERT INTO patients (
                    mrn, first_name, last_name, date_of_birth, gender, ethnicity,
                    height_cm, weight_kg, bmi, phone, email, address,
                    emergency_contact_name, emergency_contact_phone,
                    insurance_provider, insurance_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id
            """, (
                f"MRN{fake.unique.random_number(digits=5)}",
                patient_data['first_name'], patient_data['last_name'],
                patient_data['date_of_birth'], patient_data['gender'],
                patient_data['ethnicity'], patient_data['height_cm'],
                patient_data['weight_kg'], patient_data['bmi'],
                patient_data['phone'], patient_data['email'],
                patient_data['address'], patient_data['emergency_contact_name'],
                patient_data['emergency_contact_phone'],
                patient_data['insurance_provider'], patient_data['insurance_id']
            ))
            
            patient_id = cursor.fetchone()[0]
            
            # Assign phenotype
            confidence_score = random.uniform(0.7, 1.0)
            cursor.execute("""
                INSERT INTO patient_phenotypes (
                    patient_id, phenotype_id, assigned_date, confidence_score, notes
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                patient_id, phenotype_id, date.today(),
                round(confidence_score, 2),
                f"Assigned based on clinical presentation and diagnostic criteria"
            ))
            
            # Add medical history
            add_medical_history(cursor, patient_id, phenotype_name)
            
            # Add lab results
            add_lab_results(cursor, patient_id, phenotype_name)
            
            # Add glucose readings
            add_glucose_readings(cursor, patient_id, phenotype_name)
            
            # Add vital signs
            add_vital_signs(cursor, patient_id)
            
            # Add medications
            add_medications(cursor, patient_id, phenotype_name)
    
    conn.commit()
    cursor.close()

def add_medical_history(cursor, patient_id, phenotype_name):
    """Add relevant medical history based on phenotype"""
    conditions = []
    
    if phenotype_name == 'Type 1 Diabetes - Autoimmune':
        conditions = ['Type 1 Diabetes', 'Autoimmune Disease']
    elif phenotype_name == 'Type 2 Diabetes - Insulin Resistant':
        conditions = ['Type 2 Diabetes', 'Hypertension', 'Dyslipidemia']
    elif phenotype_name == 'Gestational Diabetes':
        conditions = ['Gestational Diabetes', 'Pregnancy']
    elif phenotype_name == 'MODY (Maturity Onset Diabetes of the Young)':
        conditions = ['MODY', 'Family History of Diabetes']
    elif phenotype_name == 'LADA (Latent Autoimmune Diabetes in Adults)':
        conditions = ['LADA', 'Autoimmune Disease']
    
    for condition in conditions:
        diagnosis_date = fake.date_between(start_date='-5y', end_date='-1y')
        cursor.execute("""
            INSERT INTO medical_history (
                patient_id, condition_name, diagnosis_date, status, severity, notes
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            patient_id, condition, diagnosis_date, 'Active',
            random.choice(['Mild', 'Moderate', 'Severe']),
            f"Diagnosed based on {phenotype_name} criteria"
        ))

def add_lab_results(cursor, patient_id, phenotype_name):
    """Add relevant laboratory results based on phenotype"""
    # HbA1c
    if phenotype_name in ['Type 1 Diabetes - Autoimmune', 'Type 2 Diabetes - Insulin Resistant']:
        hba1c_value = random.uniform(7.0, 12.0)
    elif phenotype_name == 'Gestational Diabetes':
        hba1c_value = random.uniform(5.7, 8.0)
    else:
        hba1c_value = random.uniform(6.5, 9.0)
    
    cursor.execute("""
        INSERT INTO lab_results (
            patient_id, test_date, test_name, test_value, unit,
            reference_range_low, reference_range_high, is_abnormal, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        patient_id, fake.date_between(start_date='-30d', end_date='today'),
        'HbA1c', round(hba1c_value, 1), '%', 4.0, 5.6, True,
        f"Elevated HbA1c consistent with {phenotype_name}"
    ))
    
    # Fasting Glucose
    if phenotype_name in ['Type 1 Diabetes - Autoimmune', 'Type 2 Diabetes - Insulin Resistant']:
        fasting_glucose = random.uniform(120, 300)
    elif phenotype_name == 'Gestational Diabetes':
        fasting_glucose = random.uniform(95, 140)
    else:
        fasting_glucose = random.uniform(100, 200)
    
    cursor.execute("""
        INSERT INTO lab_results (
            patient_id, test_date, test_name, test_value, unit,
            reference_range_low, reference_range_high, is_abnormal, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        patient_id, fake.date_between(start_date='-30d', end_date='today'),
        'Fasting Glucose', round(fasting_glucose, 0), 'mg/dL', 70, 99, True,
        f"Elevated fasting glucose consistent with {phenotype_name}"
    ))

def add_glucose_readings(cursor, patient_id, phenotype_name):
    """Add glucose readings for the past 30 days"""
    for i in range(30):
        reading_date = datetime.now() - timedelta(days=i)
        
        # Generate glucose values based on phenotype
        if phenotype_name in ['Type 1 Diabetes - Autoimmune', 'Type 2 Diabetes - Insulin Resistant']:
            glucose_value = random.uniform(80, 350)
        elif phenotype_name == 'Gestational Diabetes':
            glucose_value = random.uniform(70, 200)
        else:
            glucose_value = random.uniform(90, 250)
        
        reading_type = random.choice(['Fasting', 'Postprandial', 'Random', 'Bedtime'])
        
        cursor.execute("""
            INSERT INTO glucose_readings (
                patient_id, reading_date, glucose_value, reading_type, meal_context, notes
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            patient_id, reading_date, round(glucose_value, 0),
            reading_type, random.choice(['Breakfast', 'Lunch', 'Dinner', 'Snack', None]),
            f"Home glucose monitoring - {phenotype_name}"
        ))

def add_vital_signs(cursor, patient_id):
    """Add vital signs for the past 30 days"""
    for i in range(10):  # 10 measurements over 30 days
        measurement_date = datetime.now() - timedelta(days=i*3)
        
        cursor.execute("""
            INSERT INTO vital_signs (
                patient_id, measurement_date, systolic_bp, diastolic_bp,
                heart_rate, temperature, respiratory_rate, oxygen_saturation, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_id, measurement_date,
            random.randint(110, 160), random.randint(70, 100),
            random.randint(60, 100), round(random.uniform(36.5, 37.5), 1),
            random.randint(12, 20), round(random.uniform(95.0, 99.9), 1),
            "Routine vital signs measurement"
        ))

def add_medications(cursor, patient_id, phenotype_name):
    """Add relevant medications based on phenotype"""
    medications = {
        'Type 1 Diabetes - Autoimmune': ['Insulin Glargine', 'Insulin Lispro'],
        'Type 2 Diabetes - Insulin Resistant': ['Metformin', 'Glipizide', 'Insulin Glargine'],
        'Gestational Diabetes': ['Insulin Lispro', 'Metformin'],
        'MODY (Maturity Onset Diabetes of the Young)': ['Sulfonylurea', 'Metformin'],
        'LADA (Latent Autoimmune Diabetes in Adults)': ['Metformin', 'Insulin Glargine']
    }
    
    med_list = medications.get(phenotype_name, ['Metformin'])
    
    for med_name in med_list:
        # Check if medication exists, if not insert it
        cursor.execute("SELECT medication_id FROM medications WHERE medication_name = %s", (med_name,))
        result = cursor.fetchone()
        
        if result:
            medication_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO medications (medication_name, generic_name, medication_class, dosage_form, strength)
                VALUES (%s, %s, %s, %s, %s) RETURNING medication_id
            """, (med_name, med_name, 'Antidiabetic', 'Tablet', '500mg'))
            medication_id = cursor.fetchone()[0]
        
        # Prescribe medication
        prescribed_date = fake.date_between(start_date='-6m', end_date='-1m')
        cursor.execute("""
            INSERT INTO patient_medications (
                patient_id, medication_id, prescribed_date, start_date, dosage,
                frequency, route, status, prescribed_by, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_id, medication_id, prescribed_date, prescribed_date,
            '500mg', 'Twice daily', 'Oral', 'Active',
            'Dr. Smith', f"Prescribed for {phenotype_name} management"
        ))

def main():
    """Main function to populate the database"""
    print("Connecting to database...")
    conn = connect_to_db()
    
    print("Inserting phenotypes...")
    phenotype_ids = insert_phenotypes(conn)
    
    print("Inserting patients and related data...")
    insert_patients_and_phenotypes(conn, phenotype_ids)
    
    print("Database population completed successfully!")
    print(f"Created {len(phenotype_ids)} phenotypes")
    print(f"Created {len(phenotype_ids) * 4} patients (4 per phenotype)")
    
    conn.close()

if __name__ == "__main__":
    main() 
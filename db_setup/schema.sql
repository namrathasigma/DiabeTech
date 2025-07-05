-- Diabetes Management System PostgreSQL Schema
-- This schema supports patient management, medical records, and phenotype analysis

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Patient Demographics Table
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mrn VARCHAR(20) UNIQUE NOT NULL, -- Medical Record Number
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    ethnicity VARCHAR(50),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(4,2),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    insurance_provider VARCHAR(100),
    insurance_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Diabetes Phenotypes Table
CREATE TABLE phenotypes (
    phenotype_id SERIAL PRIMARY KEY,
    phenotype_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    criteria TEXT,
    severity_level VARCHAR(20) CHECK (severity_level IN ('Mild', 'Moderate', 'Severe')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient Phenotype Assignment
CREATE TABLE patient_phenotypes (
    patient_phenotype_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    phenotype_id INTEGER REFERENCES phenotypes(phenotype_id) ON DELETE CASCADE,
    assigned_date DATE NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(patient_id, phenotype_id)
);

-- Medical History Table
CREATE TABLE medical_history (
    history_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    condition_name VARCHAR(100) NOT NULL,
    diagnosis_date DATE,
    status VARCHAR(20) CHECK (status IN ('Active', 'Resolved', 'Chronic')),
    severity VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Laboratory Results Table
CREATE TABLE lab_results (
    lab_result_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    test_date DATE NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    test_value DECIMAL(10,3),
    unit VARCHAR(20),
    reference_range_low DECIMAL(10,3),
    reference_range_high DECIMAL(10,3),
    is_abnormal BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blood Glucose Readings Table
CREATE TABLE glucose_readings (
    reading_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    reading_date TIMESTAMP NOT NULL,
    glucose_value DECIMAL(5,2) NOT NULL,
    reading_type VARCHAR(20) CHECK (reading_type IN ('Fasting', 'Postprandial', 'Random', 'Bedtime')),
    meal_context VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medications Table
CREATE TABLE medications (
    medication_id SERIAL PRIMARY KEY,
    medication_name VARCHAR(100) NOT NULL,
    generic_name VARCHAR(100),
    medication_class VARCHAR(100),
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient Medications Table
CREATE TABLE patient_medications (
    patient_medication_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    medication_id INTEGER REFERENCES medications(medication_id) ON DELETE CASCADE,
    prescribed_date DATE NOT NULL,
    start_date DATE,
    end_date DATE,
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    route VARCHAR(20),
    status VARCHAR(20) CHECK (status IN ('Active', 'Discontinued', 'Completed')),
    prescribed_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vital Signs Table
CREATE TABLE vital_signs (
    vital_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    measurement_date TIMESTAMP NOT NULL,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    heart_rate INTEGER,
    temperature DECIMAL(4,2),
    respiratory_rate INTEGER,
    oxygen_saturation DECIMAL(4,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments Table
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    appointment_type VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'No-show')),
    provider_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_patients_mrn ON patients(mrn);
CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_patient_phenotypes_patient ON patient_phenotypes(patient_id);
CREATE INDEX idx_patient_phenotypes_phenotype ON patient_phenotypes(phenotype_id);
CREATE INDEX idx_lab_results_patient_date ON lab_results(patient_id, test_date);
CREATE INDEX idx_glucose_readings_patient_date ON glucose_readings(patient_id, reading_date);
CREATE INDEX idx_medical_history_patient ON medical_history(patient_id);
CREATE INDEX idx_vital_signs_patient_date ON vital_signs(patient_id, measurement_date);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for patient summary
CREATE VIEW patient_summary AS
SELECT 
    p.patient_id,
    p.mrn,
    p.first_name,
    p.last_name,
    p.date_of_birth,
    p.gender,
    p.bmi,
    COUNT(DISTINCT pp.phenotype_id) as phenotype_count,
    STRING_AGG(DISTINCT ph.phenotype_name, ', ') as phenotypes,
    MAX(gr.reading_date) as last_glucose_reading,
    MAX(vs.measurement_date) as last_vital_signs
FROM patients p
LEFT JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
LEFT JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
LEFT JOIN glucose_readings gr ON p.patient_id = gr.patient_id
LEFT JOIN vital_signs vs ON p.patient_id = vs.patient_id
GROUP BY p.patient_id, p.mrn, p.first_name, p.last_name, p.date_of_birth, p.gender, p.bmi; 
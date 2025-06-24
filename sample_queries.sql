-- Sample Queries for Diabetes Management Database
-- These queries demonstrate the database functionality and data analysis capabilities

-- 1. Patient Summary by Phenotype
SELECT 
    ph.phenotype_name,
    COUNT(p.patient_id) as patient_count,
    ROUND(AVG(p.bmi), 2) as avg_bmi,
    ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth))), 1) as avg_age,
    ph.severity_level
FROM patients p
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
GROUP BY ph.phenotype_name, ph.severity_level
ORDER BY patient_count DESC;

-- 2. Recent Glucose Readings (Last 7 days)
SELECT 
    p.first_name,
    p.last_name,
    ph.phenotype_name,
    gr.glucose_value,
    gr.reading_type,
    gr.reading_date,
    CASE 
        WHEN gr.glucose_value < 70 THEN 'Low'
        WHEN gr.glucose_value > 180 THEN 'High'
        ELSE 'Normal'
    END as glucose_status
FROM patients p
JOIN glucose_readings gr ON p.patient_id = gr.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
WHERE gr.reading_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY gr.reading_date DESC, p.last_name;

-- 3. Abnormal Lab Results
SELECT 
    p.first_name,
    p.last_name,
    ph.phenotype_name,
    lr.test_name,
    lr.test_value,
    lr.unit,
    lr.reference_range_low,
    lr.reference_range_high,
    lr.test_date
FROM patients p
JOIN lab_results lr ON p.patient_id = lr.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
WHERE lr.is_abnormal = true
ORDER BY lr.test_date DESC;

-- 4. Medication Analysis by Phenotype
SELECT 
    ph.phenotype_name,
    m.medication_name,
    COUNT(pm.patient_medication_id) as prescription_count,
    pm.dosage,
    pm.frequency
FROM patient_medications pm
JOIN patients p ON pm.patient_id = p.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
JOIN medications m ON pm.medication_id = m.medication_id
WHERE pm.status = 'Active'
GROUP BY ph.phenotype_name, m.medication_name, pm.dosage, pm.frequency
ORDER BY ph.phenotype_name, prescription_count DESC;

-- 5. Vital Signs Summary
SELECT 
    ph.phenotype_name,
    ROUND(AVG(vs.systolic_bp), 1) as avg_systolic,
    ROUND(AVG(vs.diastolic_bp), 1) as avg_diastolic,
    ROUND(AVG(vs.heart_rate), 1) as avg_heart_rate,
    COUNT(DISTINCT p.patient_id) as patient_count
FROM vital_signs vs
JOIN patients p ON vs.patient_id = p.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
WHERE vs.measurement_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ph.phenotype_name
ORDER BY ph.phenotype_name;

-- 6. Glucose Control Analysis
SELECT 
    ph.phenotype_name,
    COUNT(DISTINCT p.patient_id) as patient_count,
    ROUND(AVG(gr.glucose_value), 1) as avg_glucose,
    ROUND(MIN(gr.glucose_value), 1) as min_glucose,
    ROUND(MAX(gr.glucose_value), 1) as max_glucose,
    COUNT(CASE WHEN gr.glucose_value < 70 THEN 1 END) as low_readings,
    COUNT(CASE WHEN gr.glucose_value > 180 THEN 1 END) as high_readings,
    COUNT(CASE WHEN gr.glucose_value BETWEEN 70 AND 180 THEN 1 END) as normal_readings
FROM glucose_readings gr
JOIN patients p ON gr.patient_id = p.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
WHERE gr.reading_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ph.phenotype_name
ORDER BY ph.phenotype_name;

-- 7. Patient Demographics Analysis
SELECT 
    ph.phenotype_name,
    p.gender,
    p.ethnicity,
    COUNT(p.patient_id) as patient_count,
    ROUND(AVG(p.bmi), 2) as avg_bmi,
    ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth))), 1) as avg_age
FROM patients p
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
GROUP BY ph.phenotype_name, p.gender, p.ethnicity
ORDER BY ph.phenotype_name, patient_count DESC;

-- 8. Medical History Summary
SELECT 
    ph.phenotype_name,
    mh.condition_name,
    COUNT(mh.history_id) as condition_count,
    mh.status,
    mh.severity
FROM medical_history mh
JOIN patients p ON mh.patient_id = p.patient_id
JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
GROUP BY ph.phenotype_name, mh.condition_name, mh.status, mh.severity
ORDER BY ph.phenotype_name, condition_count DESC;

-- 9. Phenotype Confidence Analysis
SELECT 
    ph.phenotype_name,
    COUNT(pp.patient_phenotype_id) as total_assignments,
    ROUND(AVG(pp.confidence_score), 3) as avg_confidence,
    ROUND(MIN(pp.confidence_score), 3) as min_confidence,
    ROUND(MAX(pp.confidence_score), 3) as max_confidence,
    COUNT(CASE WHEN pp.confidence_score >= 0.9 THEN 1 END) as high_confidence,
    COUNT(CASE WHEN pp.confidence_score < 0.8 THEN 1 END) as low_confidence
FROM patient_phenotypes pp
JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id
GROUP BY ph.phenotype_name
ORDER BY avg_confidence DESC;

-- 10. Recent Activity Summary (Last 30 days)
SELECT 
    'Patients' as data_type,
    COUNT(DISTINCT p.patient_id) as count
FROM patients p
WHERE p.created_at >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'Glucose Readings' as data_type,
    COUNT(gr.reading_id) as count
FROM glucose_readings gr
WHERE gr.reading_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'Lab Results' as data_type,
    COUNT(lr.lab_result_id) as count
FROM lab_results lr
WHERE lr.test_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'Vital Signs' as data_type,
    COUNT(vs.vital_id) as count
FROM vital_signs vs
WHERE vs.measurement_date >= CURRENT_DATE - INTERVAL '30 days'

ORDER BY count DESC; 
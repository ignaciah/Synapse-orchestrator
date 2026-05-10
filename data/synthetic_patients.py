
```python
import json
import random
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.medicationrequest import MedicationRequest
from datetime import datetime, timedelta

class SyntheticFHIRGenerator:
    def __init__(self):
        self.patients = []
        
    def generate_patient(self, patient_id):
        """Generate a synthetic patient with FHIR compliance"""
        patient = Patient({
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [{
                "system": "http://hospital.org/medical-records",
                "value": f"MRN{random.randint(10000, 99999)}"
            }],
            "name": [{
                "use": "official",
                "family": random.choice(["Smith", "Johnson", "Williams", "Brown"]),
                "given": [random.choice(["James", "Maria", "Robert", "Patricia"])]
            }],
            "gender": random.choice(["male", "female"]),
            "birthDate": f"{random.randint(1940, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "address": [{
                "line": [f"{random.randint(100, 999)} Main St"],
                "city": random.choice(["Boston", "Seattle", "Austin", "Denver"]),
                "state": random.choice(["MA", "WA", "TX", "CO"]),
                "postalCode": str(random.randint(10000, 99999))
            }]
        })
        return patient.dict()

    def generate_vitals(self, patient_id):
        """Generate realistic vital signs"""
        vitals = []
        base_bp_sys = random.randint(110, 140)
        base_bp_dia = random.randint(70, 90)
        
        observations = [
            {
                "code": "85354-9",  # Blood pressure
                "value": f"{base_bp_sys}/{base_bp_dia}",
                "interpretation": "N" if base_bp_sys < 130 else "H"
            },
            {
                "code": "8867-4",   # Heart rate
                "value": random.randint(60, 100),
                "interpretation": "N"
            },
            {
                "code": "4548-4",   # Hemoglobin A1c
                "value": round(random.uniform(4.5, 10.5), 1),
                "interpretation": "H" if random.random() > 0.7 else "N"
            }
        ]
        
        for obs in observations:
            observation = Observation({
                "resourceType": "Observation",
                "id": f"obs-{random.randint(1000,9999)}",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": obs["code"]
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": datetime.now().isoformat(),
                "valueQuantity": {
                    "value": obs["value"] if isinstance(obs["value"], (int, float)) else None,
                    "unit": obs["code"] == "85354-9" and "mmHg" or "bpm",
                    "system": "http://unitsofmeasure.org"
                } if isinstance(obs["value"], (int, float)) else None,
                "valueString": obs["value"] if isinstance(obs["value"], str) else None,
                "interpretation": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "code": obs["interpretation"]
                    }]
                }]
            })
            vitals.append(observation.dict())
        return vitals

    def save_dataset(self):
        """Generate full synthetic dataset"""
        dataset = {"patients": [], "observations": [], "medications": []}
        
        for i in range(1, 11):  # 10 patients
            patient_id = f"patient-{i}"
            dataset["patients"].append(self.generate_patient(patient_id))
            dataset["observations"].extend(self.generate_vitals(patient_id))
            
        with open("data/synthetic_ehr.json", "w") as f:
            json.dump(dataset, f, indent=2)
        print("✅ Generated synthetic EHR data for 10 patients")

if __name__ == "__main__":
    generator = SyntheticFHIRGenerator()
    generator.save_dataset()

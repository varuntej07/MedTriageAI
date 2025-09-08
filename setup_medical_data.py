"""
Setup script for MedTriageAI medical knowledge base
This script creates the medical data structure as specified
"""
import os
import requests
import time
from pathlib import Path

def create_medical_data_structure():
    """Create the medical data directory structure"""
    medical_dir = Path("medical")
    input_dir = medical_dir / "input"
    
    # Create directories
    medical_dir.mkdir(exist_ok=True)
    input_dir.mkdir(exist_ok=True)
    
    print(f"Created medical data directories: {medical_dir}")
    return input_dir

def create_sample_medical_files(input_dir: Path):
    """Create sample medical knowledge files for the specified topics"""
    
    medical_topics = {
        "fever_adult": {
            "title": "Fever in Adults",
            "source": "MedlinePlus",
            "body": """
            Fever is a temperature of 100.4F (38C) or higher. It's usually a sign that your body is fighting an infection.
            
            Common causes include:
            - Viral infections (like colds or flu)
            - Bacterial infections
            - Heat exhaustion
            - Certain medications
            - Inflammatory conditions
            
            When to seek immediate care:
            - Temperature over 103F (39.4C)
            - Fever with severe headache, stiff neck, confusion, or difficulty breathing
            - Signs of dehydration
            - Fever that lasts more than 3 days
            
            Treatment typically involves rest, fluids, and fever-reducing medications like acetaminophen or ibuprofen.
            """
        },
        "cough": {
            "title": "Cough",
            "source": "MedlinePlus", 
            "body": """
            A cough is a reflex that helps clear your airways of mucus, irritants, and foreign particles.
            
            Types of coughs:
            - Dry cough: No mucus production
            - Productive cough: Brings up mucus or phlegm
            - Acute: Lasts less than 3 weeks
            - Chronic: Lasts more than 8 weeks
            
            Common causes:
            - Viral infections (common cold, flu)
            - Bacterial infections
            - Allergies
            - Asthma
            - GERD (acid reflux)
            
            Seek medical attention if:
            - Cough produces blood
            - Difficulty breathing
            - High fever
            - Cough lasts more than 3 weeks
            - Wheezing or chest pain
            """
        },
        "sore_throat": {
            "title": "Sore Throat",
            "source": "MedlinePlus",
            "body": """
            A sore throat is pain, scratchiness, or irritation of the throat that often worsens when you swallow.
            
            Most common causes:
            - Viral infections (70-85% of cases)
            - Bacterial infections (especially strep throat)
            - Allergies
            - Dry air
            - Irritants (smoke, chemicals)
            
            Strep throat symptoms:
            - Severe throat pain
            - Fever over 101F
            - Swollen lymph nodes
            - Red, swollen tonsils with white patches
            
            Seek medical care if:
            - Severe difficulty swallowing
            - High fever
            - Symptoms persist over a week
            - Signs of strep throat
            """
        },
        "headache": {
            "title": "Headache", 
            "source": "MedlinePlus",
            "body": """
            Headaches are one of the most common health complaints. Most are not serious, but some require immediate attention.
            
            Types:
            - Tension headaches: Most common, feel like a tight band around head
            - Migraines: Severe, often with nausea and light sensitivity
            - Cluster headaches: Severe pain around one eye
            - Secondary headaches: Caused by underlying condition
            
            Red flag symptoms requiring immediate care:
            - Sudden, severe headache (worst headache of my life)
            - Headache with fever and stiff neck
            - Headache after head injury
            - Sudden headache with confusion, vision changes, or weakness
            - Headache that gets progressively worse
            
            Most headaches can be treated with rest, hydration, and over-the-counter pain relievers.
            """
        },
        "vomiting": {
            "title": "Vomiting",
            "source": "MedlinePlus",
            "body": """
            Vomiting is the forceful expulsion of stomach contents through the mouth. It's often preceded by nausea.
            
            Common causes:
            - Viral gastroenteritis (stomach flu)
            - Food poisoning
            - Motion sickness
            - Pregnancy (morning sickness)
            - Medications
            - Migraines
            
            Concerning symptoms requiring medical attention:
            - Blood in vomit
            - Signs of dehydration
            - Severe abdominal pain
            - High fever
            - Unable to keep fluids down for 24 hours
            - Projectile vomiting in infants
            
            Treatment focuses on preventing dehydration with small, frequent sips of clear fluids.
            """
        },
        "diarrhea": {
            "title": "Diarrhea",
            "source": "MedlinePlus", 
            "body": """
            Diarrhea is loose, watery stools occurring more frequently than normal.
            
            Common causes:
            - Viral infections
            - Bacterial infections
            - Food poisoning
            - Medications (especially antibiotics)
            - Food intolerances
            - Inflammatory bowel disease
            
            Types:
            - Acute: Lasts 1-2 days, usually viral
            - Persistent: Lasts 2-4 weeks
            - Chronic: Lasts more than 4 weeks
            
            Seek medical care for:
            - Signs of severe dehydration
            - Blood or mucus in stool
            - High fever (over 102F)
            - Severe abdominal or rectal pain
            - Diarrhea lasting more than 3 days
            """
        },
        "dehydration": {
            "title": "Dehydration",
            "source": "MedlinePlus",
            "body": """
            Dehydration occurs when you lose more fluids than you take in, and your body doesn't have enough water to function normally.
            
            Causes:
            - Diarrhea and vomiting
            - Fever
            - Excessive sweating
            - Increased urination
            - Not drinking enough fluids
            
            Mild to moderate symptoms:
            - Thirst
            - Dry mouth
            - Less frequent urination
            - Dark-colored urine
            - Fatigue
            - Dizziness
            
            Severe dehydration (medical emergency):
            - Extreme thirst
            - Little or no urination
            - Sunken eyes
            - Rapid heartbeat
            - Confusion
            - Unconsciousness
            """
        },
        "rash": {
            "title": "Rash",
            "source": "MedlinePlus",
            "body": """
            A rash is a change in the skin's color, appearance, or texture. Rashes can be localized or widespread.
            
            Common types:
            - Contact dermatitis: From irritants or allergens
            - Eczema: Chronic inflammatory skin condition
            - Heat rash: From blocked sweat ducts
            - Viral rashes: Associated with infections
            
            Concerning features requiring immediate care:
            - Rapid spread
            - Associated with difficulty breathing
            - High fever
            - Purple spots that don't blanch
            - Signs of infection (pus, red streaking)
            - Severe itching affecting sleep
            
            Most rashes are minor and resolve on their own or with basic care.
            """
        },
        "urinary_tract_infection": {
            "title": "Urinary Tract Infection",
            "source": "MedlinePlus",
            "body": """
            A urinary tract infection (UTI) is an infection in any part of your urinary system - kidneys, ureters, bladder, or urethra.
            
            Common symptoms:
            - Burning sensation during urination
            - Frequent, urgent need to urinate
            - Cloudy or strong-smelling urine
            - Pelvic pain (in women)
            - Blood in urine
            
            Risk factors:
            - Female anatomy
            - Sexual activity
            - Certain birth control methods
            - Menopause
            - Kidney stones
            
            Seek immediate care for:
            - High fever and chills
            - Nausea and vomiting
            - Back or side pain (possible kidney infection)
            - Blood in urine
            
            UTIs are typically treated with antibiotics and usually resolve within a few days of treatment.
            """
        }
    }
    
    # Create files for each topic
    for topic_id, topic_data in medical_topics.items():
        file_path = input_dir / f"{topic_id}.txt"
        
        content = f"""TITLE: {topic_data['title']}
SOURCE: {topic_data['source']}
SECTION: MedlinePlus: FullSummary
BODY: {topic_data['body'].strip()}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created: {file_path}")

def main():
    """Main setup function"""
    print("Setting up MedTriageAI medical knowledge base...")
    
    # Create directory structure
    input_dir = create_medical_data_structure()
    
    # Create sample medical files
    create_sample_medical_files(input_dir)
    
    print("\nMedical knowledge base setup complete!")
    print(f"Medical files created in: {input_dir}")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your API keys")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python main.py")

if __name__ == "__main__":
    main()
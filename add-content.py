#!/usr/bin/env python3
"""
MedExit - Content Management Script
Add MCQs, Q&A, Flashcards, and Mnemonics to your JSON file
Supports creating categories, subjects, and topics via JSON structure
"""

import json
import sys
import os
import subprocess
from datetime import datetime

# ==================== CONFIG ====================
JSON_FILE = 'mcqs_q_a_flashcards_andetc.json'
STRUCTURE_FILE = 'content_structure.json'

# ==================== FUNCTIONS ====================

def load_json(filename):
    """Load a JSON file"""
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(data, filename):
    """Save a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved to {filename}")

def find_or_create_category(data, cat_id, cat_name, cat_icon='📚'):
    """Find or create a category"""
    for cat in data['categories']:
        if cat['id'] == cat_id:
            return cat
    new_cat = {
        "id": cat_id,
        "name": cat_name,
        "icon": cat_icon,
        "description": "",
        "subjects": []
    }
    data['categories'].append(new_cat)
    print(f"✅ Created new category: {cat_name}")
    return new_cat

def find_or_create_subject(category, subject_id, subject_name, subject_icon='📖'):
    """Find or create a subject within a category"""
    for subj in category['subjects']:
        if subj['id'] == subject_id:
            return subj
    new_subj = {
        "id": subject_id,
        "name": subject_name,
        "icon": subject_icon,
        "topics": []
    }
    category['subjects'].append(new_subj)
    print(f"✅ Created new subject: {subject_name}")
    return new_subj

def find_or_create_topic(subject, topic_id, topic_name, topic_icon='📝'):
    """Find or create a topic within a subject"""
    for topic in subject['topics']:
        if topic['id'] == topic_id:
            return topic
    new_topic = {
        "id": topic_id,
        "name": topic_name,
        "icon": topic_icon,
        "description": "",
        "content": {
            "mcqs": [],
            "qa": [],
            "flashcards": [],
            "mnemonics": []
        }
    }
    subject['topics'].append(new_topic)
    print(f"✅ Created new topic: {topic_name}")
    return new_topic

def add_mcq(topic, question, options, answer, explanation=''):
    """Add an MCQ to a topic"""
    mcq = {
        "q": question,
        "options": options,
        "answer": answer,
        "explanation": explanation
    }
    topic['content']['mcqs'].append(mcq)
    print("✅ Added MCQ")

def add_qa(topic, question, answer):
    """Add a Q&A to a topic"""
    qa = {
        "q": question,
        "a": answer
    }
    topic['content']['qa'].append(qa)
    print("✅ Added Q&A")

def add_flashcard(topic, front, back):
    """Add a Flashcard to a topic"""
    flashcard = {
        "front": front,
        "back": back
    }
    topic['content']['flashcards'].append(flashcard)
    print("✅ Added Flashcard")

def add_mnemonic(topic, title, code, items, icon='🧠'):
    """Add a Mnemonic to a topic"""
    mnemonic = {
        "title": title,
        "icon": icon,
        "code": code,
        "items": items
    }
    topic['content']['mnemonics'].append(mnemonic)
    print("✅ Added Mnemonic")

def auto_update_github():
    """Auto-update GitHub"""
    print("\n🔄 Pushing to GitHub...")
    try:
        subprocess.run(['git', 'add', JSON_FILE], capture_output=True, text=True, check=False)
        subprocess.run(['git', 'commit', '-m', f'📝 Auto-update content - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], capture_output=True, text=True, check=False)
        result = subprocess.run(['git', 'push'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ Changes pushed to GitHub!")
        else:
            print("⚠️  Push may have issues. Check manually.")
    except Exception as e:
        print(f"⚠️  Could not auto-push: {e}")

def create_from_structure_file():
    """Create categories, subjects, topics from a structure file"""
    print("\n📄 Creating from structure file...")
    
    if not os.path.exists(STRUCTURE_FILE):
        print(f"❌ {STRUCTURE_FILE} not found!")
        print("   Creating a template...")
        create_structure_template()
        return
    
    # Load structure
    structure = load_json(STRUCTURE_FILE)
    if not structure:
        return
    
    # Load main data
    data = load_json(JSON_FILE)
    if not data:
        print("❌ Could not load main JSON file!")
        return
    
    # Process each category
    for cat_data in structure.get('categories', []):
        cat_id = cat_data.get('id')
        cat_name = cat_data.get('name', cat_id.title())
        cat_icon = cat_data.get('icon', '📚')
        
        category = find_or_create_category(data, cat_id, cat_name, cat_icon)
        
        # Process each subject
        for subj_data in cat_data.get('subjects', []):
            subj_id = subj_data.get('id')
            subj_name = subj_data.get('name', subj_id.replace('_', ' ').title())
            subj_icon = subj_data.get('icon', '📖')
            
            subject = find_or_create_subject(category, subj_id, subj_name, subj_icon)
            
            # Process each topic
            for topic_data in subj_data.get('topics', []):
                topic_id = topic_data.get('id')
                topic_name = topic_data.get('name', topic_id.replace('_', ' ').title())
                topic_icon = topic_data.get('icon', '📝')
                topic_desc = topic_data.get('description', '')
                
                topic = find_or_create_topic(subject, topic_id, topic_name, topic_icon)
                if topic_desc:
                    topic['description'] = topic_desc
                
                # Add content if provided
                content = topic_data.get('content', {})
                
                # Add MCQs
                for mcq in content.get('mcqs', []):
                    add_mcq(topic, mcq.get('q'), mcq.get('options', []), mcq.get('answer'), mcq.get('explanation', ''))
                
                # Add Q&A
                for qa in content.get('qa', []):
                    add_qa(topic, qa.get('q'), qa.get('a'))
                
                # Add Flashcards
                for flash in content.get('flashcards', []):
                    add_flashcard(topic, flash.get('front'), flash.get('back'))
                
                # Add Mnemonics
                for mnem in content.get('mnemonics', []):
                    add_mnemonic(topic, mnem.get('title'), mnem.get('code'), mnem.get('items', []), mnem.get('icon', '🧠'))
    
    # Save the updated data
    save_json(data, JSON_FILE)
    
    # Auto-update GitHub
    auto_update_github()
    
    print("\n🌐 Live URL: https://imran362-arch.github.io/ExitMed/")
    print("⏱️  Wait 1-2 minutes for GitHub Pages to update")

def create_structure_template():
    """Create a template structure file"""
    template = {
        "categories": [
            {
                "id": "clinic",
                "name": "Clinic",
                "icon": "🏥",
                "description": "Clinical medicine and patient care",
                "subjects": [
                    {
                        "id": "internal_medicine",
                        "name": "Internal Medicine",
                        "icon": "🩺",
                        "topics": [
                            {
                                "id": "cardiology",
                                "name": "Cardiology",
                                "icon": "❤️",
                                "description": "Heart and cardiovascular system",
                                "content": {
                                    "mcqs": [],
                                    "qa": [],
                                    "flashcards": [],
                                    "mnemonics": []
                                }
                            }
                        ]
                    },
                    {
                        "id": "pediatrics",
                        "name": "Pediatrics",
                        "icon": "👶",
                        "topics": []
                    }
                ]
            },
            {
                "id": "paraclinic",
                "name": "Paraclinic",
                "icon": "🔬",
                "description": "Basic medical sciences",
                "subjects": [
                    {
                        "id": "anatomy",
                        "name": "Anatomy",
                        "icon": "🫀",
                        "topics": []
                    },
                    {
                        "id": "physiology",
                        "name": "Physiology",
                        "icon": "⚡",
                        "topics": []
                    }
                ]
            },
            {
                "id": "nmle",
                "name": "NMLE Qbanks",
                "icon": "📝",
                "description": "National Medical Licensing Exam questions",
                "subjects": [
                    {
                        "id": "nmle_step1",
                        "name": "NMLE Step 1",
                        "icon": "📗",
                        "topics": []
                    }
                ]
            }
        ]
    }
    
    save_json(template, STRUCTURE_FILE)
    print(f"✅ Created template at: {STRUCTURE_FILE}")
    print("\n📝 Edit this file to add your content structure:")
    print("   nano content_structure.json")
    print("\nThen run: python add-content.py --structure")

def manual_add_mode():
    """Manual mode - add content interactively"""
    data = load_json(JSON_FILE)
    if not data:
        print("❌ Could not load main JSON file!")
        return
    
    # Show current stats
    total_cats = len(data['categories'])
    total_subjects = sum(len(cat['subjects']) for cat in data['categories'])
    total_topics = sum(
        sum(len(subj['topics']) for subj in cat['subjects']) 
        for cat in data['categories']
    )
    print(f"\n📊 Current Stats:")
    print(f"   Categories: {total_cats}")
    print(f"   Subjects: {total_subjects}")
    print(f"   Topics: {total_topics}\n")
    
    # Get user input
    print("📍 Where to add content?")
    print("   (You can use existing or create new)\n")
    
    cat_id = input("Category ID (e.g., clinic): ").strip()
    cat_name = input("Category Name (e.g., Clinic): ").strip()
    if not cat_name:
        cat_name = cat_id.title()
    
    subject_id = input("Subject ID (e.g., pediatrics): ").strip()
    subject_name = input("Subject Name (e.g., Pediatrics): ").strip()
    if not subject_name:
        subject_name = subject_id.replace('_', ' ').title()
    
    topic_id = input("Topic ID (e.g., vaccination): ").strip()
    topic_name = input("Topic Name (e.g., Vaccination Schedule): ").strip()
    if not topic_name:
        topic_name = topic_id.replace('_', ' ').title()
    
    # Find or create
    category = find_or_create_category(data, cat_id, cat_name)
    subject = find_or_create_subject(category, subject_id, subject_name)
    topic = find_or_create_topic(subject, topic_id, topic_name)
    
    print(f"\n✅ Now adding to: {cat_name} → {subject_name} → {topic_name}\n")
    
    # Show menu
    while True:
        print("\n" + "-"*30)
        print("What do you want to add?")
        print("  1) MCQ")
        print("  2) Q&A")
        print("  3) Flashcard")
        print("  4) Mnemonic")
        print("  5) Done - Save and exit")
        print("  6) Cancel - Exit without saving")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            q = input("Question: ").strip()
            print("Options (comma separated):")
            opts = input("> ").strip().split(',')
            opts = [o.strip() for o in opts]
            print("Correct answer (0-based index):")
            ans = int(input("> ").strip())
            exp = input("Explanation (optional): ").strip()
            add_mcq(topic, q, opts, ans, exp)
            
        elif choice == '2':
            q = input("Question: ").strip()
            a = input("Answer: ").strip()
            add_qa(topic, q, a)
            
        elif choice == '3':
            front = input("Front: ").strip()
            back = input("Back: ").strip()
            add_flashcard(topic, front, back)
            
        elif choice == '4':
            title = input("Mnemonic Title: ").strip()
            code = input("Mnemonic Code (e.g., 3-2-3-3): ").strip()
            print("Items (letter: text format)")
            print("Press Enter twice when done:")
            items = []
            while True:
                line = input("> ").strip()
                if not line:
                    break
                if ':' in line:
                    letter, text = line.split(':', 1)
                    items.append({'letter': letter.strip(), 'text': text.strip()})
            if items:
                add_mnemonic(topic, title, code, items)
            
        elif choice == '5':
            save_json(data, JSON_FILE)
            print("\n" + "="*50)
            print("✅ Content added successfully!")
            print("="*50)
            auto_update_github()
            print("\n🌐 Live URL: https://imran362-arch.github.io/ExitMed/")
            print("⏱️  Wait 1-2 minutes for GitHub Pages to update")
            break
            
        elif choice == '6':
            print("❌ Cancelled. No changes saved.")
            break
            
        else:
            print("❌ Invalid choice. Try again.")

def show_help():
    """Show help menu"""
    print("""
╔══════════════════════════════════════════════════════════╗
║              MedExit - Content Manager                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  USAGE:                                                  ║
║                                                          ║
║  python add-content.py           - Manual interactive    ║
║  python add-content.py --structure  - Use structure file ║
║  python add-content.py --template   - Create template    ║
║  python add-content.py --help      - Show this help      ║
║                                                          ║
║  STRUCTURE FILE:                                         ║
║  Create content_structure.json with your categories,     ║
║  subjects, topics, and content (MCQs, Q&A, etc.)        ║
║                                                          ║
║  FILE FORMAT:                                            ║
║  {                                                       ║
║    "categories": [                                       ║
║      {                                                   ║
║        "id": "clinic",                                   ║
║        "name": "Clinic",                                 ║
║        "icon": "🏥",                                     ║
║        "subjects": [                                     ║
║          {                                               ║
║            "id": "pediatrics",                           ║
║            "name": "Pediatrics",                         ║
║            "icon": "👶",                                 ║
║            "topics": [                                   ║
║              {                                           ║
║                "id": "vaccinations",                     ║
║                "name": "Vaccinations",                   ║
║                "icon": "💉",                             ║
║                "content": {                              ║
║                  "mcqs": [...],                          ║
║                  "qa": [...],                           ║
║                  "flashcards": [...],                   ║
║                  "mnemonics": [...]                     ║
║                }                                         ║
║              }                                           ║
║            ]                                             ║
║          }                                               ║
║        ]                                                 ║
║      }                                                   ║
║    ]                                                     ║
║  }                                                       ║
╚══════════════════════════════════════════════════════════╝
    """)

# ==================== MAIN ====================

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            show_help()
        elif sys.argv[1] == '--template':
            create_structure_template()
        elif sys.argv[1] == '--structure':
            create_from_structure_file()
        else:
            print("❌ Unknown option. Use --help for usage.")
    else:
        manual_add_mode()

if __name__ == "__main__":
    main()





















#!/usr/bin/env python3
"""
MedExit - Content Management Script
Add MCQs, Q&A, Flashcards, and Mnemonics to your JSON file
"""

import json
import sys
import os
import subprocess
from datetime import datetime

# ==================== CONFIG ====================
JSON_FILE = 'mcqs_q_a_flashcards_andetc.json'

# ==================== FUNCTIONS ====================

def load_json():
    """Load the JSON file"""
    if not os.path.exists(JSON_FILE):
        print(f"❌ Error: {JSON_FILE} not found!")
        return None
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

def save_json(data):
    """Save the JSON file"""
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print("✅ Saved to", JSON_FILE)

def find_or_create_category(data, cat_id, cat_name, cat_icon='📚'):
    """Find or create a category"""
    for cat in data['categories']:
        if cat['id'] == cat_id:
            return cat
    # Create new category
    new_cat = {
        "id": cat_id,
        "name": cat_name,
        "icon": cat_icon,
        "description": "",
        "subjects": []
    }
    data['categories'].append(new_cat)
    print(f"✅ Created new category: {cat_name}")
    return new_cat

def find_or_create_subject(category, subject_id, subject_name, subject_icon='📖'):
    """Find or create a subject within a category"""
    for subj in category['subjects']:
        if subj['id'] == subject_id:
            return subj
    # Create new subject
    new_subj = {
        "id": subject_id,
        "name": subject_name,
        "icon": subject_icon,
        "topics": []
    }
    category['subjects'].append(new_subj)
    print(f"✅ Created new subject: {subject_name}")
    return new_subj

def find_or_create_topic(subject, topic_id, topic_name, topic_icon='📝'):
    """Find or create a topic within a subject"""
    for topic in subject['topics']:
        if topic['id'] == topic_id:
            return topic
    # Create new topic
    new_topic = {
        "id": topic_id,
        "name": topic_name,
        "icon": topic_icon,
        "description": "",
        "content": {
            "mcqs": [],
            "qa": [],
            "flashcards": [],
            "mnemonics": []
        }
    }
    subject['topics'].append(new_topic)
    print(f"✅ Created new topic: {topic_name}")
    return new_topic

def add_mcq(topic, question, options, answer, explanation=''):
    """Add an MCQ to a topic"""
    mcq = {
        "q": question,
        "options": options,
        "answer": answer,
        "explanation": explanation
    }
    topic['content']['mcqs'].append(mcq)
    print("✅ Added MCQ")

def add_qa(topic, question, answer):
    """Add a Q&A to a topic"""
    qa = {
        "q": question,
        "a": answer
    }
    topic['content']['qa'].append(qa)
    print("✅ Added Q&A")

def add_flashcard(topic, front, back):
    """Add a Flashcard to a topic"""
    flashcard = {
        "front": front,
        "back": back
    }
    topic['content']['flashcards'].append(flashcard)
    print("✅ Added Flashcard")

def add_mnemonic(topic, title, code, items, icon='🧠'):
    """Add a Mnemonic to a topic"""
    mnemonic = {
        "title": title,
        "icon": icon,
        "code": code,
        "items": items
    }
    topic['content']['mnemonics'].append(mnemonic)
    print("✅ Added Mnemonic")

def auto_update_github():
    """Auto-update GitHub"""
    print("\n🔄 Pushing to GitHub...")
    try:
        result = subprocess.run(['git', 'add', JSON_FILE], capture_output=True, text=True)
        result = subprocess.run(['git', 'commit', '-m', f'📝 Auto-update content - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], capture_output=True, text=True)
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Changes pushed to GitHub!")
        else:
            print("⚠️  Push may have issues. Check manually.")
    except Exception as e:
        print(f"⚠️  Could not auto-push: {e}")

# ==================== MAIN MENU ====================

def main():
    print("\n" + "="*50)
    print("      MedExit - Content Manager")
    print("="*50 + "\n")
    
    # Load JSON
    data = load_json()
    if not data:
        return
    
    # Show current stats
    total_cats = len(data['categories'])
    total_subjects = sum(len(cat['subjects']) for cat in data['categories'])
    total_topics = sum(
        sum(len(subj['topics']) for subj in cat['subjects']) 
        for cat in data['categories']
    )
    print(f"📊 Current Stats:")
    print(f"   Categories: {total_cats}")
    print(f"   Subjects: {total_subjects}")
    print(f"   Topics: {total_topics}\n")
    
    # Get user input
    print("📍 Where to add content?")
    print("   (You can use existing or create new)")
    print()
    
    cat_id = input("Category ID (e.g., clinic, paraclinic, nmle): ").strip()
    cat_name = input("Category Name (e.g., Clinic, Paraclinic, NMLE): ").strip()
    if not cat_name:
        cat_name = cat_id.title()
    
    subject_id = input("Subject ID (e.g., internal_medicine): ").strip()
    subject_name = input("Subject Name (e.g., Internal Medicine): ").strip()
    if not subject_name:
        subject_name = subject_id.replace('_', ' ').title()
    
    topic_id = input("Topic ID (e.g., heart_anatomy): ").strip()
    topic_name = input("Topic Name (e.g., Heart Anatomy): ").strip()
    if not topic_name:
        topic_name = topic_id.replace('_', ' ').title()
    
    # Find or create
    category = find_or_create_category(data, cat_id, cat_name)
    subject = find_or_create_subject(category, subject_id, subject_name)
    topic = find_or_create_topic(subject, topic_id, topic_name)
    
    print(f"\n✅ Now adding to: {cat_name} → {subject_name} → {topic_name}\n")
    
    # Show menu
    while True:
        print("\n" + "-"*30)
        print("What do you want to add?")
        print("  1) MCQ")
        print("  2) Q&A")
        print("  3) Flashcard")
        print("  4) Mnemonic")
        print("  5) Done - Save and exit")
        print("  6) Cancel - Exit without saving")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            # Add MCQ
            q = input("Question: ").strip()
            print("Options (comma separated):")
            opts = input("> ").strip().split(',')
            opts = [o.strip() for o in opts]
            print("Correct answer (0-based index):")
            ans = int(input("> ").strip())
            exp = input("Explanation (optional): ").strip()
            add_mcq(topic, q, opts, ans, exp)
            
        elif choice == '2':
            # Add Q&A
            q = input("Question: ").strip()
            a = input("Answer: ").strip()
            add_qa(topic, q, a)
            
        elif choice == '3':
            # Add Flashcard
            front = input("Front: ").strip()
            back = input("Back: ").strip()
            add_flashcard(topic, front, back)
            
        elif choice == '4':
            # Add Mnemonic
            title = input("Mnemonic Title: ").strip()
            code = input("Mnemonic Code (e.g., 3-2-3-3): ").strip()
            print("Items (letter and text, one per line)")
            print("Format: 'letter: text' (e.g., '3: Tricuspid = 3 cusps')")
            print("Press Enter twice when done:")
            items = []
            while True:
                line = input("> ").strip()
                if not line:
                    break
                if ':' in line:
                    letter, text = line.split(':', 1)
                    items.append({'letter': letter.strip(), 'text': text.strip()})
            if items:
                add_mnemonic(topic, title, code, items)
            
        elif choice == '5':
            # Save and exit
            save_json(data)
            print("\n" + "="*50)
            print("✅ Content added successfully!")
            print("="*50)
            
            # Auto-update GitHub
            auto_update_github()
            
            print("\n🌐 Live URL: https://imran362-arch.github.io/ExitMed/")
            print("⏱️  Wait 1-2 minutes for GitHub Pages to update")
            break
            
        elif choice == '6':
            # Cancel
            print("❌ Cancelled. No changes saved.")
            break
            
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()

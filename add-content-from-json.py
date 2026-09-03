#!/usr/bin/env python3
import json
import sys
import os
import subprocess
from datetime import datetime

JSON_FILE = 'mcqs_q_a_flashcards_andetc.json'

if not os.path.exists(JSON_FILE):
    print(f"❌ Error: {JSON_FILE} not found!")
    sys.exit(1)

if len(sys.argv) > 1:
    try:
        with open(sys.argv[1], 'r') as f:
            new_content = json.load(f)
        print(f"📄 Loaded content from: {sys.argv[1]}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
else:
    print("📝 Paste your content JSON below (press Ctrl+D when done):")
    try:
        json_str = sys.stdin.read()
        if not json_str.strip():
            print("❌ No input provided!")
            sys.exit(1)
        new_content = json.loads(json_str)
    except Exception as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

with open(JSON_FILE, 'r') as f:
    data = json.load(f)

counters = {'categories': 0, 'subjects': 0, 'topics': 0, 'subtopics': 0, 'mcqs': 0, 'qa': 0, 'flashcards': 0, 'mnemonics': 0}

def find_or_create_category(cat_id, cat_name, cat_icon='📚'):
    for cat in data.get('categories', []):
        if cat.get('id') == cat_id:
            return cat, False
    new_cat = {"id": cat_id, "name": cat_name, "icon": cat_icon, "description": "", "subjects": []}
    if 'categories' not in data:
        data['categories'] = []
    data['categories'].append(new_cat)
    counters['categories'] += 1
    print(f"✅ Created category: {cat_name}")
    return new_cat, True

def find_or_create_subject(category, subj_id, subj_name, subj_icon='📖'):
    for subj in category.get('subjects', []):
        if subj.get('id') == subj_id:
            return subj, False
    new_subj = {"id": subj_id, "name": subj_name, "icon": subj_icon, "topics": []}
    category['subjects'].append(new_subj)
    counters['subjects'] += 1
    print(f"  ✅ Created subject: {subj_name}")
    return new_subj, True

def find_or_create_topic(subject, topic_id, topic_name, topic_icon='📝'):
    for topic in subject.get('topics', []):
        if topic.get('id') == topic_id:
            return topic, False
    new_topic = {"id": topic_id, "name": topic_name, "icon": topic_icon, "description": "", "subtopics": []}
    subject['topics'].append(new_topic)
    counters['topics'] += 1
    print(f"    ✅ Created topic: {topic_name}")
    return new_topic, True

def find_or_create_subtopic(topic, subtopic_id, subtopic_name, subtopic_icon='📌'):
    # Ensure subtopics exists
    if 'subtopics' not in topic:
        topic['subtopics'] = []
    for sub in topic.get('subtopics', []):
        if sub.get('id') == subtopic_id:
            return sub, False
    new_subtopic = {
        "id": subtopic_id,
        "name": subtopic_name,
        "icon": subtopic_icon,
        "description": "",
        "content": {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    }
    topic['subtopics'].append(new_subtopic)
    counters['subtopics'] += 1
    print(f"        ✅ Created subtopic: {subtopic_name}")
    return new_subtopic, True

def add_mcq(target, question, options, answer, explanation=''):
    if 'content' not in target:
        target['content'] = {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    for existing in target['content']['mcqs']:
        if existing.get('q') == question:
            print(f"            ⚠️  MCQ already exists")
            return False
    target['content']['mcqs'].append({"q": question, "options": options, "answer": answer, "explanation": explanation})
    counters['mcqs'] += 1
    print(f"            ✅ Added MCQ: {question[:40]}...")
    return True

def add_qa(target, question, answer):
    if 'content' not in target:
        target['content'] = {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    for existing in target['content']['qa']:
        if existing.get('q') == question:
            print(f"            ⚠️  Q&A already exists")
            return False
    target['content']['qa'].append({"q": question, "a": answer})
    counters['qa'] += 1
    print(f"            ✅ Added Q&A: {question[:40]}...")
    return True

def add_flashcard(target, front, back):
    if 'content' not in target:
        target['content'] = {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    for existing in target['content']['flashcards']:
        if existing.get('front') == front:
            print(f"            ⚠️  Flashcard already exists")
            return False
    target['content']['flashcards'].append({"front": front, "back": back})
    counters['flashcards'] += 1
    print(f"            ✅ Added Flashcard: {front[:40]}...")
    return True

def add_mnemonic(target, title, code, items, icon='🧠'):
    if 'content' not in target:
        target['content'] = {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    for existing in target['content']['mnemonics']:
        if existing.get('title') == title:
            print(f"            ⚠️  Mnemonic already exists")
            return False
    target['content']['mnemonics'].append({"title": title, "icon": icon, "code": code, "items": items})
    counters['mnemonics'] += 1
    print(f"            ✅ Added Mnemonic: {title}")
    return True

def process_content(target, content):
    """Process content and add to target (topic or subtopic)"""
    if not content:
        return
    if 'content' not in target:
        target['content'] = {"mcqs": [], "qa": [], "flashcards": [], "mnemonics": []}
    for mcq in content.get('mcqs', []):
        add_mcq(target, mcq.get('q', ''), mcq.get('options', []), mcq.get('answer', 0), mcq.get('explanation', ''))
    for qa in content.get('qa', []):
        add_qa(target, qa.get('q', ''), qa.get('a', ''))
    for flash in content.get('flashcards', []):
        add_flashcard(target, flash.get('front', ''), flash.get('back', ''))
    for mnem in content.get('mnemonics', []):
        add_mnemonic(target, mnem.get('title', ''), mnem.get('code', ''), mnem.get('items', []), mnem.get('icon', '🧠'))

print("\n" + "="*50)
print("      MedExit - Content Importer")
print("="*50 + "\n")

for cat_data in new_content.get('categories', []):
    cat_id = cat_data.get('id')
    cat_name = cat_data.get('name', cat_id.title())
    cat_icon = cat_data.get('icon', '📚')
    category, cat_created = find_or_create_category(cat_id, cat_name, cat_icon)
    
    for subj_data in cat_data.get('subjects', []):
        subj_id = subj_data.get('id')
        subj_name = subj_data.get('name', subj_id.replace('_', ' ').title())
        subj_icon = subj_data.get('icon', '📖')
        subject, subj_created = find_or_create_subject(category, subj_id, subj_name, subj_icon)
        
        for topic_data in subj_data.get('topics', []):
            topic_id = topic_data.get('id')
            topic_name = topic_data.get('name', topic_id.replace('_', ' ').title())
            topic_icon = topic_data.get('icon', '📝')
            topic_desc = topic_data.get('description', '')
            
            topic, topic_created = find_or_create_topic(subject, topic_id, topic_name, topic_icon)
            if topic_desc and not topic.get('description'):
                topic['description'] = topic_desc
            
            # Check if this topic has subtopics
            if 'subtopics' in topic_data and topic_data['subtopics']:
                # Process subtopics
                for subtopic_data in topic_data.get('subtopics', []):
                    subtopic_id = subtopic_data.get('id')
                    subtopic_name = subtopic_data.get('name', subtopic_id.replace('_', ' ').title())
                    subtopic_icon = subtopic_data.get('icon', '📌')
                    subtopic_desc = subtopic_data.get('description', '')
                    
                    subtopic, sub_created = find_or_create_subtopic(topic, subtopic_id, subtopic_name, subtopic_icon)
                    if subtopic_desc and not subtopic.get('description'):
                        subtopic['description'] = subtopic_desc
                    
                    # Process content in subtopic
                    content = subtopic_data.get('content', {})
                    process_content(subtopic, content)
            else:
                # Process content directly in topic (no subtopics)
                content = topic_data.get('content', {})
                process_content(topic, content)

with open(JSON_FILE, 'w') as f:
    json.dump(data, f, indent=2)

print("\n📊 SUMMARY")
print("="*50)
print(f"   Categories added: {counters['categories']}")
print(f"   Subjects added: {counters['subjects']}")
print(f"   Topics added: {counters['topics']}")
print(f"   Subtopics added: {counters['subtopics']}")
print(f"   MCQs added: {counters['mcqs']}")
print(f"   Q&A added: {counters['qa']}")
print(f"   Flashcards added: {counters['flashcards']}")
print(f"   Mnemonics added: {counters['mnemonics']}")

print("\n🔄 Auto-updating GitHub...")
try:
    subprocess.run(['git', 'add', JSON_FILE], capture_output=True, text=True, check=False)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subprocess.run(['git', 'commit', '-m', f'📝 Auto-update content - {timestamp}'], capture_output=True, text=True, check=False)
    result = subprocess.run(['git', 'push'], capture_output=True, text=True, check=False)
    if result.returncode == 0:
        print("✅ Pushed to GitHub successfully!")
    else:
        print("⚠️  Push had issues. Please run 'git push' manually.")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Content import complete!")
print(f"🌐 Live URL: https://imran362-arch.github.io/ExitMed/")

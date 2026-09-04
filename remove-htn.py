#!/usr/bin/env python3
import json

# Load the JSON file
with open('mcqs_q_a_flashcards_andetc.json', 'r') as f:
    data = json.load(f)

# Track if we found and removed HTN
removed = False

# Find Clinic → Internal Medicine → Cardiovascular Disease → HTN
for cat in data.get('categories', []):
    if cat.get('id') == 'clinic':
        for subj in cat.get('subjects', []):
            if subj.get('id') == 'internal_medicine':
                for topic in subj.get('topics', []):
                    if topic.get('id') == 'cardiovascular_disease':
                        # Check if there are subtopics
                        if 'subtopics' in topic:
                            # Count before removal
                            original_count = len(topic['subtopics'])
                            # Remove HTN subtopic
                            topic['subtopics'] = [s for s in topic['subtopics'] if s.get('id') != 'hypertension']
                            removed_count = original_count - len(topic['subtopics'])
                            if removed_count > 0:
                                removed = True
                                print(f"✅ Removed Hypertension (HTN) subtopic")
                                print(f"   Removed {removed_count} item")
                                print(f"   Remaining subtopics: {len(topic['subtopics'])}")
                            else:
                                print("⚠️  HTN subtopic not found in subtopics list")
                        else:
                            print("⚠️  No subtopics found in Cardiovascular Disease")
                        break
                break
        break

if not removed:
    print("❌ Could not find HTN subtopic to remove")

# Save the updated file
if removed:
    with open('mcqs_q_a_flashcards_andetc.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("✅ File updated successfully!")
else:
    print("❌ No changes made")

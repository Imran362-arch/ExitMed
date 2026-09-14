#!/usr/bin/env python3
"""Import text.json into mcqs_q_a_flashcards_andetc.json (recursive children structure)"""
import json, os, subprocess
from datetime import datetime

MAIN = 'mcqs_q_a_flashcards_andetc.json'
SRC  = 'text.json'

if not os.path.exists(MAIN):
    print(f"❌ {MAIN} not found!"); raise SystemExit(1)
if not os.path.exists(SRC):
    print(f"❌ {SRC} not found!"); raise SystemExit(1)

with open(MAIN, 'r', encoding='utf-8') as f: data = json.load(f)
with open(SRC,  'r', encoding='utf-8') as f: src  = json.load(f)

counters = {'categories':0,'subjects':0,'topics':0,'subtopics':0,
            'mcqs':0,'qa':0,'flashcards':0,'mnemonics':0,
            'images':0,'videos':0,'links':0,'notes':0}

def find_or_create_category(cid, name, icon='📚', desc=''):
    for c in data.get('categories', []):
        if c.get('id') == cid:
            if desc and not c.get('description'): c['description'] = desc
            return c
    new = {"id":cid,"name":name,"icon":icon,"description":desc,"subjects":[]}
    data.setdefault('categories', []).append(new)
    counters['categories'] += 1
    print(f"✅ Category: {name}")
    return new

def find_or_create_subject(cat, sid, name, icon='📖', desc=''):
    for s in cat.get('subjects', []):
        if s.get('id') == sid:
            if desc and not s.get('description'): s['description'] = desc
            return s
    new = {"id":sid,"name":name,"icon":icon,"description":desc,"topics":[]}
    cat.setdefault('subjects', []).append(new)
    counters['subjects'] += 1
    print(f"  ✅ Subject: {name}")
    return new

def find_or_create_topic(subj, tid, name, icon='📝', desc=''):
    for t in subj.get('topics', []):
        if t.get('id') == tid:
            if desc and not t.get('description'): t['description'] = desc
            return t
    new = {"id":tid,"name":name,"icon":icon,"description":desc,"subtopics":[]}
    subj.setdefault('topics', []).append(new)
    counters['topics'] += 1
    print(f"    ✅ Topic: {name}")
    return new

def find_or_create_subtopic(topic, sid, name, icon='📌', desc=''):
    for s in topic.get('subtopics', []):
        if s.get('id') == sid:
            if desc and not s.get('description'): s['description'] = desc
            return s
    new = {"id":sid,"name":name,"icon":icon,"description":desc,
           "content":{"mcqs":[],"qa":[],"flashcards":[],"mnemonics":[]}}
    topic.setdefault('subtopics', []).append(new)
    counters['subtopics'] += 1
    print(f"      ✅ Subtopic: {name}")
    return new

def merge_content(target, content):
    if not content: return
    if 'content' not in target:
        target['content'] = {"mcqs":[],"qa":[],"flashcards":[],"mnemonics":[]}

    for m in content.get('mcqs', []):
        if m.get('q') not in [x.get('q') for x in target['content']['mcqs']]:
            target['content']['mcqs'].append(m); counters['mcqs'] += 1
    for q in content.get('qa', []):
        if q.get('q') not in [x.get('q') for x in target['content']['qa']]:
            target['content']['qa'].append(q); counters['qa'] += 1
    for f in content.get('flashcards', []):
        if f.get('front') not in [x.get('front') for x in target['content']['flashcards']]:
            target['content']['flashcards'].append(f); counters['flashcards'] += 1
    for mn in content.get('mnemonics', []):
        if mn.get('title') not in [x.get('title') for x in target['content']['mnemonics']]:
            target['content']['mnemonics'].append(mn); counters['mnemonics'] += 1

    if content.get('notes'):
        target.setdefault('notes', [])
        for n in content['notes']:
            if n.get('title') not in [x.get('title') for x in target['notes']]:
                target['notes'].append(n); counters['notes'] += 1
    if content.get('images'):
        target.setdefault('images', [])
        for img in content['images']:
            if img.get('src') not in [x.get('src') for x in target['images']]:
                target['images'].append(img); counters['images'] += 1
    if content.get('videos'):
        target.setdefault('videos', [])
        for v in content['videos']:
            if v.get('src') not in [x.get('src') for x in target['videos']]:
                target['videos'].append(v); counters['videos'] += 1
    if content.get('links'):
        target.setdefault('links', [])
        for l in content['links']:
            if l.get('url') not in [x.get('url') for x in target['links']]:
                target['links'].append(l); counters['links'] += 1

def process_node(node, parent, level):
    nid = node.get('id'); name = node.get('name', nid)
    icon = node.get('icon', '📝'); desc = node.get('description', '')
    content = node.get('content', {}); children = node.get('children', [])

    if level == 1:   current = find_or_create_subject(parent, nid, name, icon, desc)
    elif level == 2: current = find_or_create_topic(parent, nid, name, icon, desc)
    else:            current = find_or_create_subtopic(parent, nid, name, icon, desc)

    if content: merge_content(current, content)
    for child in children:
        process_node(child, current, level + 1)

print("\n" + "="*50)
print("   MedExit – Recursive Importer")
print("="*50 + "\n")

for cat in src.get('categories', []):
    cid = cat.get('id'); cname = cat.get('name', cid.title())
    cicon = cat.get('icon', '📚'); cdesc = cat.get('description', '')
    category = find_or_create_category(cid, cname, cicon, cdesc)
    for child in cat.get('children', []):
        process_node(child, category, level=1)

with open(MAIN, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n📊 SUMMARY")
print("="*50)
for k, v in counters.items():
    if v: print(f"   {k.capitalize()}: {v}")

print("\n🔄 Auto-updating GitHub...")
try:
    subprocess.run(['git','add',MAIN], check=False)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subprocess.run(['git','commit','-m',f'📝 Import content – {ts}'], check=False)
    r = subprocess.run(['git','push'], capture_output=True, text=True)
    print("✅ Pushed!" if r.returncode == 0 else "⚠️  Push issue. Run 'git push' manually.")
except Exception as e:
    print(f"❌ Git error: {e}")

print("\n✅ Import complete!")
print("🌐 https://imran362-arch.github.io/ExitMed/")

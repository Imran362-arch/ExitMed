#!/bin/bash

echo "🔄 Updating index.html to support subtopics..."

# Backup original file
cp index.html index.html.backup
echo "✅ Backup created: index.html.backup"

# Check if subtopic support already exists
if grep -q "subtopic-grid" index.html; then
    echo "⚠️  Subtopics already supported in index.html"
    exit 0
fi

# Find the renderTopicView function line number
LINE=$(grep -n "function renderTopicView() {" index.html | cut -d: -f1)
if [ -z "$LINE" ]; then
    echo "❌ Could not find renderTopicView function"
    exit 1
fi

# Find the end of the function (next function definition)
END_LINE=$(tail -n +$LINE index.html | grep -n "function " | tail -1 | cut -d: -f1)
END_LINE=$((LINE + END_LINE - 1))

echo "📝 Found renderTopicView at line $LINE"

# Create the new renderTopicView function with subtopic support
cat > /tmp/new_render_topic.txt << 'FUNC'
function renderTopicView() {
  const content = document.getElementById('content');
  const topic = getTopic(state.categoryId, state.subjectId, state.topicId);
  if (!topic) return;
  
  // Check if topic has subtopics
  const subtopics = topic.subtopics || [];
  
  // If there are subtopics, render them as a list
  if (subtopics.length > 0) {
    const cat = getCategory(state.categoryId);
    const sub = getSubject(state.categoryId, state.subjectId);
    
    let html = `
      <div class="content-viewer">
        <div class="content-hero">
          <div class="ch-top">
            <div class="ch-icon-wrap">${topic.icon || '📌'}</div>
            <div class="ch-info">
              <h1 class="${dirClass(topic.name)}">${escapeHtml(topic.name)}</h1>
              <div class="ch-path">
                <span>${getCategoryIcon(cat.id)} ${escapeHtml(cat.name)}</span>
                <span style="color:var(--text-dim)">›</span>
                <span>${sub?.icon || '📖'} ${escapeHtml(sub.name)}</span>
              </div>
            </div>
          </div>
          ${topic.description ? `<div class="ch-description ${dirClass(topic.description)}">${escapeHtml(topic.description)}</div>` : ''}
        </div>
        <div class="subtopic-grid">
    `;
    
    subtopics.forEach(subtopic => {
      const c = subtopic.content || {};
      const mcqs = c.mcqs || [];
      const qa = c.qa || [];
      const flashcards = c.flashcards || [];
      const mnemonics = c.mnemonics || [];
      
      html += `
        <div class="subtopic-card" onclick="selectSubtopic('${subtopic.id}')">
          <div class="subtopic-icon">${subtopic.icon || '📌'}</div>
          <div class="subtopic-info">
            <div class="subtopic-name ${dirClass(subtopic.name)}">${escapeHtml(subtopic.name)}</div>
            ${subtopic.description ? `<div class="subtopic-desc ${dirClass(subtopic.description)}">${escapeHtml(subtopic.description)}</div>` : ''}
            <div class="subtopic-stats">
              ${mcqs.length ? `<span>📋 ${mcqs.length}</span>` : ''}
              ${qa.length ? `<span>💬 ${qa.length}</span>` : ''}
              ${flashcards.length ? `<span>🎴 ${flashcards.length}</span>` : ''}
              ${mnemonics.length ? `<span>🧠 ${mnemonics.length}</span>` : ''}
            </div>
          </div>
          <div class="subtopic-arrow">›</div>
        </div>
      `;
    });
    
    html += `
        </div>
      </div>
    `;
    
    content.innerHTML = html;
    return;
  }
  
  // If no subtopics, render content directly
  const c = topic.content || {};
  const mcqs = c.mcqs || [];
  const qa = c.qa || [];
  const flashcards = c.flashcards || [];
  const mnemonics = c.mnemonics || [];
  const topicKey = `${state.categoryId}_${state.subjectId}_${state.topicId}`;
  const cat = getCategory(state.categoryId);
  const sub = getSubject(state.categoryId, state.subjectId);
  
  let html = `
    <div class="content-viewer">
      <div class="content-hero">
        <div class="ch-top">
          <div class="ch-icon-wrap">${topic.icon || '📌'}</div>
          <div class="ch-info">
            <h1 class="${dirClass(topic.name)}">${escapeHtml(topic.name)}</h1>
            <div class="ch-path">
              <span>${getCategoryIcon(cat.id)} ${escapeHtml(cat.name)}</span>
              <span style="color:var(--text-dim)">›</span>
              <span>${sub?.icon || '📖'} ${escapeHtml(sub.name)}</span>
            </div>
          </div>
        </div>
        ${topic.description ? `<div class="ch-description ${dirClass(topic.description)}">${escapeHtml(topic.description)}</div>` : ''}
        <div class="ch-badges">
          ${mcqs.length ? `<div class="ch-badge mcq">📋 ${mcqs.length} ${t('mcqs')}</div>` : ''}
          ${qa.length ? `<div class="ch-badge qa">💬 ${qa.length} ${t('qa')}</div>` : ''}
          ${flashcards.length ? `<div class="ch-badge flash">🎴 ${flashcards.length} ${t('flashcards')}</div>` : ''}
          ${mnemonics.length ? `<div class="ch-badge mnem">🧠 ${mnemonics.length} ${t('mnemonics')}</div>` : ''}
        </div>
      </div>

      <div class="content-tabs">
        <button class="content-tab ${state.currentTab === 'mcqs' ? 'active' : ''}" onclick="switchTab('mcqs')" ${!mcqs.length ? 'disabled' : ''}>
          📋 ${t('mcqs')} <span class="tab-count">${mcqs.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'qa' ? 'active' : ''}" onclick="switchTab('qa')" ${!qa.length ? 'disabled' : ''}>
          💬 ${t('qa')} <span class="tab-count">${qa.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'flashcards' ? 'active' : ''}" onclick="switchTab('flashcards')" ${!flashcards.length ? 'disabled' : ''}>
          🎴 ${t('flashcards')} <span class="tab-count">${flashcards.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'mnemonics' ? 'active' : ''}" onclick="switchTab('mnemonics')" ${!mnemonics.length ? 'disabled' : ''}>
          🧠 ${t('mnemonics')} <span class="tab-count">${mnemonics.length}</span>
        </button>
      </div>

      <div class="content-panel ${state.currentTab === 'mcqs' ? 'active' : ''}" id="panel-mcqs">
        ${mcqs.length ? renderMCQs(mcqs, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'qa' ? 'active' : ''}" id="panel-qa">
        ${qa.length ? renderQA(qa, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'flashcards' ? 'active' : ''}" id="panel-flashcards">
        ${flashcards.length ? renderFlashcards(flashcards, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'mnemonics' ? 'active' : ''}" id="panel-mnemonics">
        ${mnemonics.length ? renderMnemonics(mnemonics) : renderEmpty()}
      </div>
    </div>
  `;

  content.innerHTML = html;
}

function selectSubtopic(subtopicId) {
  state.subtopicId = subtopicId;
  renderSubtopicView();
}

function renderSubtopicView() {
  const content = document.getElementById('content');
  const topic = getTopic(state.categoryId, state.subjectId, state.topicId);
  if (!topic) return;
  
  const subtopics = topic.subtopics || [];
  const subtopic = subtopics.find(s => s.id === state.subtopicId);
  if (!subtopic) return;
  
  const c = subtopic.content || {};
  const mcqs = c.mcqs || [];
  const qa = c.qa || [];
  const flashcards = c.flashcards || [];
  const mnemonics = c.mnemonics || [];
  const topicKey = `${state.categoryId}_${state.subjectId}_${state.topicId}_${state.subtopicId}`;
  const cat = getCategory(state.categoryId);
  const sub = getSubject(state.categoryId, state.subjectId);
  
  let html = `
    <div class="content-viewer">
      <div class="content-hero">
        <div class="ch-top">
          <div class="ch-icon-wrap">${subtopic.icon || '📌'}</div>
          <div class="ch-info">
            <h1 class="${dirClass(subtopic.name)}">${escapeHtml(subtopic.name)}</h1>
            <div class="ch-path">
              <span>${getCategoryIcon(cat.id)} ${escapeHtml(cat.name)}</span>
              <span style="color:var(--text-dim)">›</span>
              <span>${sub?.icon || '📖'} ${escapeHtml(sub.name)}</span>
              <span style="color:var(--text-dim)">›</span>
              <span>${topic.icon || '📌'} ${escapeHtml(topic.name)}</span>
            </div>
          </div>
        </div>
        ${subtopic.description ? `<div class="ch-description ${dirClass(subtopic.description)}">${escapeHtml(subtopic.description)}</div>` : ''}
        <div class="ch-badges">
          ${mcqs.length ? `<div class="ch-badge mcq">📋 ${mcqs.length} ${t('mcqs')}</div>` : ''}
          ${qa.length ? `<div class="ch-badge qa">💬 ${qa.length} ${t('qa')}</div>` : ''}
          ${flashcards.length ? `<div class="ch-badge flash">🎴 ${flashcards.length} ${t('flashcards')}</div>` : ''}
          ${mnemonics.length ? `<div class="ch-badge mnem">🧠 ${mnemonics.length} ${t('mnemonics')}</div>` : ''}
        </div>
      </div>

      <div class="content-tabs">
        <button class="content-tab ${state.currentTab === 'mcqs' ? 'active' : ''}" onclick="switchTab('mcqs')" ${!mcqs.length ? 'disabled' : ''}>
          📋 ${t('mcqs')} <span class="tab-count">${mcqs.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'qa' ? 'active' : ''}" onclick="switchTab('qa')" ${!qa.length ? 'disabled' : ''}>
          💬 ${t('qa')} <span class="tab-count">${qa.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'flashcards' ? 'active' : ''}" onclick="switchTab('flashcards')" ${!flashcards.length ? 'disabled' : ''}>
          🎴 ${t('flashcards')} <span class="tab-count">${flashcards.length}</span>
        </button>
        <button class="content-tab ${state.currentTab === 'mnemonics' ? 'active' : ''}" onclick="switchTab('mnemonics')" ${!mnemonics.length ? 'disabled' : ''}>
          🧠 ${t('mnemonics')} <span class="tab-count">${mnemonics.length}</span>
        </button>
      </div>

      <div class="content-panel ${state.currentTab === 'mcqs' ? 'active' : ''}" id="panel-mcqs">
        ${mcqs.length ? renderMCQs(mcqs, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'qa' ? 'active' : ''}" id="panel-qa">
        ${qa.length ? renderQA(qa, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'flashcards' ? 'active' : ''}" id="panel-flashcards">
        ${flashcards.length ? renderFlashcards(flashcards, topicKey) : renderEmpty()}
      </div>

      <div class="content-panel ${state.currentTab === 'mnemonics' ? 'active' : ''}" id="panel-mnemonics">
        ${mnemonics.length ? renderMnemonics(mnemonics) : renderEmpty()}
      </div>
    </div>
  `;

  content.innerHTML = html;
}
FUNC

# Now we need to replace the function in the file
# This is a simplified approach - using sed to replace the function

# Find the line numbers
START_LINE=$(grep -n "^function renderTopicView() {" index.html | head -1 | cut -d: -f1)
if [ -z "$START_LINE" ]; then
    echo "❌ Could not find renderTopicView function"
    exit 1
fi

# Find the next function definition after renderTopicView
END_LINE=$(tail -n +$((START_LINE + 1)) index.html | grep -n "^function " | head -1 | cut -d: -f1)
if [ -z "$END_LINE" ]; then
    # If no next function, use the end of file
    END_LINE=$(wc -l < index.html)
else
    END_LINE=$((START_LINE + END_LINE - 1))
fi

echo "Replacing lines $START_LINE to $END_LINE"

# Create a new file with the replacement
head -n $((START_LINE - 1)) index.html > /tmp/index_new.html
cat /tmp/new_render_topic.txt >> /tmp/index_new.html
tail -n +$((END_LINE + 1)) index.html >> /tmp/index_new.html

# Replace the original file
mv /tmp/index_new.html index.html

echo "✅ Updated renderTopicView with subtopic support"

# Add CSS for subtopics if not present
if ! grep -q "subtopic-grid" index.html; then
    echo "Adding CSS for subtopics..."
    # Find the style tag and add CSS before it closes
    sed -i '/<\/style>/i \
/* Subtopics CSS */\
.subtopic-grid {\
  display: grid;\
  grid-template-columns: 1fr;\
  gap: 12px;\
  padding: 16px 0;\
}\
.subtopic-card {\
  background: var(--card-bg);\
  border-radius: 16px;\
  padding: 16px;\
  display: flex;\
  align-items: center;\
  gap: 16px;\
  cursor: pointer;\
  border: 1px solid var(--border-color);\
  transition: all 0.3s;\
}\
.subtopic-card:hover {\
  border-color: var(--gold);\
  transform: translateY(-2px);\
}\
.subtopic-card:active {\
  transform: scale(0.98);\
}\
.subtopic-icon {\
  font-size: 32px;\
  width: 48px;\
  height: 48px;\
  display: flex;\
  align-items: center;\
  justify-content: center;\
  background: var(--bg-hover);\
  border-radius: 12px;\
  flex-shrink: 0;\
}\
.subtopic-info {\
  flex: 1;\
}\
.subtopic-name {\
  font-size: 16px;\
  font-weight: 600;\
  color: var(--text-primary);\
}\
.subtopic-desc {\
  font-size: 13px;\
  color: var(--text-dim);\
  margin-top: 4px;\
}\
.subtopic-stats {\
  display: flex;\
  gap: 12px;\
  margin-top: 6px;\
  font-size: 12px;\
  color: var(--text-dim);\
}\
.subtopic-stats span {\
  background: var(--bg-hover);\
  padding: 2px 10px;\
  border-radius: 10px;\
}\
.subtopic-arrow {\
  font-size: 20px;\
  color: var(--text-dim);\
}' index.html
    echo "✅ Added CSS for subtopics"
fi

echo ""
echo "✅ Update complete!"
echo "📝 Now run: git add index.html && git commit -m 'Add subtopic support' && git push"

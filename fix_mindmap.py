import re

with open('templates/brief.html', 'r') as f:
    content = f.read()

# 1. Remove D3 script tag
content = content.replace(
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>',
    ''
)

# 2. Replace mindmap container — remove SVG
content = content.replace(
    '<div id="mindmap-container">\n            <svg id="mindmap-svg"></svg>\n          </div>',
    '<div id="mindmap-container"></div>'
)

# 3. Add CSS for HTML mindmap (append before closing </style>)
mm_css = """
    #mindmap-container{margin-top:16px;width:100%;background:#F8F6F2;border:1px solid var(--border);padding:24px 20px;overflow-x:auto;min-height:200px;}
    .mm-wrap{display:flex;align-items:flex-start;gap:0;}
    .mm-date{background:#0C1B33;color:#fff;font-size:11px;font-weight:700;padding:8px 14px;border-radius:4px;white-space:nowrap;align-self:center;}
    .mm-connector{width:32px;height:1.5px;background:#DADADA;align-self:center;flex-shrink:0;}
    .mm-branches{display:flex;flex-direction:column;gap:10px;}
    .mm-branch{display:flex;align-items:center;gap:0;}
    .mm-theme{background:#1B6EF5;color:#fff;font-size:9.5px;font-weight:700;padding:6px 12px;border-radius:4px;white-space:nowrap;flex-shrink:0;}
    .mm-theme.mm-signals{background:#C8A96E;color:#0C1B33;}
    .mm-sub-connector{width:16px;height:1.5px;background:#DADADA;flex-shrink:0;}
    .mm-entities{display:flex;flex-direction:column;gap:5px;}
    .mm-entity{background:#E8F0FE;color:#1B6EF5;font-size:9px;font-weight:500;padding:4px 10px;border-radius:3px;white-space:nowrap;border:1px solid #C5D5F5;}
    .mm-entity.mm-signal{background:#FFF8E1;color:#C8A96E;border-color:#FFE082;}
"""
content = content.replace('  </style>', mm_css + '  </style>', 1)

# 4. Replace the entire renderMindMap block
# Find it by locating the comment and replacing to the next comment
marker_start = '  // ── MIND MAP'
marker_end = '\n\n  // ── QUIZ'

idx_start = content.find(marker_start)
idx_end = content.find(marker_end)

if idx_start == -1:
    print('ERROR: could not find mind map start marker')
elif idx_end == -1:
    print('ERROR: could not find mind map end marker')
else:
    new_mm = '''  // ── MIND MAP HTML ──
  let mindMapRendered = false;

  function renderMindMap() {
    if (mindMapRendered) return;
    const container = document.getElementById('mindmap-container');
    if (!container) return;
    const devs = (todayBrief.report && todayBrief.report.key_developments || []).slice(0, 6);
    const signals = (todayBrief.report && todayBrief.report.signals_to_watch || []).slice(0, 3);
    if (!devs.length) {
      container.innerHTML = '<p style="color:#aaa;font-size:13px;">No developments to map.</p>';
      return;
    }
    const companies = ['OpenAI','Anthropic','Google','Meta','Microsoft','Apple','Amazon',
      'NVIDIA','Qualcomm','Intel','AMD','SpaceX','Tesla','Databricks','Sequoia','a16z',
      'Stripe','Salesforce','Hugging Face','Mistral','xAI','DeepMind'];

    function getEntities(text) {
      var found = companies.filter(function(c){ return text.indexOf(c) !== -1; });
      return found.slice(0, 3);
    }

    var html = '<div class="mm-wrap">';
    html += '<div class="mm-date">' + todayDate + '</div>';
    html += '<div class="mm-connector"></div>';
    html += '<div class="mm-branches">';

    devs.forEach(function(d) {
      var entities = getEntities(d.content || '');
      html += '<div class="mm-branch">';
      html += '<div class="mm-theme">' + (d.theme || 'Development') + '</div>';
      if (entities.length) {
        html += '<div class="mm-sub-connector"></div>';
        html += '<div class="mm-entities">';
        entities.forEach(function(e) {
          html += '<div class="mm-entity">' + e + '</div>';
        });
        html += '</div>';
      }
      html += '</div>';
    });

    if (signals.length) {
      html += '<div class="mm-branch">';
      html += '<div class="mm-theme mm-signals">Signals to Watch</div>';
      html += '<div class="mm-sub-connector"></div>';
      html += '<div class="mm-entities">';
      signals.forEach(function(s) {
        var label = s.length > 55 ? s.substring(0, 55) + '...' : s;
        html += '<div class="mm-entity mm-signal" title="' + s + '">' + label + '</div>';
      });
      html += '</div></div>';
    }

    html += '</div></div>';
    container.innerHTML = html;
    mindMapRendered = true;
  }'''

    content = content[:idx_start] + new_mm + content[idx_end:]
    print('Mind map block replaced successfully')

with open('templates/brief.html', 'w') as f:
    f.write(content)

count = content.count('mm-wrap')
print('mm-wrap count:', count)
print('Done' if count > 0 else 'FAILED')

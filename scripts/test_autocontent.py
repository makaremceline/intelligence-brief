import os
from dotenv import load_dotenv
load_dotenv()
from scripts.generate_autocontent import generate_podcast, build_brief_text

test_brief = {
    'date': '2026-06-15',
    'report': {
        'big_picture': 'AI agents are transforming enterprise software.',
        'key_developments': [{'theme': 'Test', 'content': 'This is a test brief.'}],
        'signals_to_watch': ['Watch agent infrastructure deals'],
        'polymarket_intelligence': 'Markets signal high confidence.',
        'funding_intelligence': 'VC money flowing into AI.',
        'regulatory_intelligence': 'FTC watching big tech.'
    }
}

brief_text = build_brief_text(test_brief)
print('Brief text built successfully')
result = generate_podcast(brief_text, '2026-06-15-test')
print(f'Result: {result}')
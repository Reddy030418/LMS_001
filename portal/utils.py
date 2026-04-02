from django.utils import timezone
from decimal import Decimal
import os

FINE_PER_DAY = Decimal('2.00')

def calculate_fine(due_date, returned_date=None):
    if returned_date is None:
        returned_date = timezone.localdate()
    delay = (returned_date - due_date).days
    if delay > 0:
        return FINE_PER_DAY * delay
    return Decimal('0.00')

def generate_book_metadata(title, author):
    import json
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-api-key':
        return {}
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"Provide a brief description (3 sentences max) and a 1-3 word subject classification for the book '{title}' by {author}. Respond strictly with a JSON object formatted exactly like this: {{\"description\": \"...\", \"subject\": \"...\"}}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful librarian metadata auto-tagger. You respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            timeout=10
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating AI metadata: {e}")
        return {}

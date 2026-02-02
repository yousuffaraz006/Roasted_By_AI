from django.shortcuts import render, redirect
from django.conf import settings
from .models import RoastSubmission
from openai import OpenAI
import base64
import os

def index(request):
    return render(request, 'roaster/index.html')

def upload_and_roast(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('upload_file')
        text_content = request.POST.get('text_content', '').strip()
        
        # Backend validation: at least one must be provided
        if not uploaded_file and not text_content:
            return render(request, 'roaster/index.html', {
                'error': 'Please provide either an image or text content to roast!'
            })
        
        # Create submission object (submission_type will be auto-detected by AI)
        submission = RoastSubmission.objects.create(
            submission_type='auto',
            image=uploaded_file if uploaded_file else None,
            text_content=text_content if text_content else None
        )
        
        # Generate roast
        roast = generate_roast(submission)
        submission.roast_result = roast
        submission.save()
        
        return render(request, 'roaster/result.html', {'submission': submission})
    
    return redirect('index')

def generate_roast(submission):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Prepare the persona prompt
    persona_prompt = """You are a ruthless stand-up comedian roasting whatever the user submits. 
    Be savage, witty, and brutally honest. Use comedy roast techniques: exaggeration, callbacks, 
    unexpected comparisons, and cutting observations. Don't hold back, but keep it clever and funny. 
    Your goal is to make people laugh while destroying their ego. Make it memorable and shareable.
    
    First, analyze what type of content this is (code, resume, living room/interior design, or other), 
    then deliver a devastating roast appropriate to that content type."""
    
    messages_content = []
    
    # Handle image submissions
    if submission.image:
        image_path = submission.image.path
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Determine media type
        file_extension = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(file_extension, 'image/jpeg')
        
        # Check if text was also provided (use as insight)
        if submission.text_content:
            prompt_text = f"""
                {persona_prompt}

                You are given an image submitted by a user.

                Your task is to roast the image intelligently and mercilessly based ONLY on what is clearly visible in the image, combined with the optional user-provided context.

                Rules you must follow:
                - Do NOT guess facts that are not visually evident
                - Identify or speculate about the person’s identity, background, age, or personal traits
                - Roast presentation, choices, composition, aesthetics, and intent and the person
                - Be sharp, witty, and devastatingly honest
                - If something looks unclear, awkward, ironic, or unintentionally funny, call it out explicitly

                Additional user context (if provided):
                \"\"\"
                {submission.text_content} - Use this context to make your roast even more devastating and accurate.
                \"\"\"
                """
        else:
            prompt_text = f"""
                {persona_prompt}

                You are given an image submitted by a user.

                Your task is to roast the image intelligently and mercilessly based ONLY on what is clearly visible in the image, combined with the optional user-provided context.

                Rules you must follow:
                - Do NOT guess facts that are not visually evident
                - Identify or speculate about the person’s identity, background, age, or personal traits
                - Roast presentation, choices, composition, aesthetics, and intent and the person
                - Be sharp, witty, and devastatingly honest
                - If something looks unclear, awkward, ironic, or unintentionally funny, call it out explicitly"""
        
        messages_content = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    }
                ]
            }
        ]
    
    # Handle text submissions
    elif submission.text_content:
        messages_content = [
            {
                "role": "user",
                "content": f"""
                    {persona_prompt}

                    You are given a resume or personal bio written by a user.

                    Your task is to roast the content intelligently and brutally, but with wit and insight also.

                    Rules you must follow:
                    - Be sarcastic, sharp, and painfully honest
                    - Use profanity, slurs, or personal attacks
                    - Criticize choices, wording, structure, and self-presentation and the person
                    - Every roast must feel accurate and specific, not generic
                    - Use humor techniques like exaggeration, irony, and unexpected comparisons

                    User-submitted content:
                    \"\"\"
                    {submission.text_content}
                    \"\"\"
                    """

            }
        ]
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_content,
            max_tokens=1000
        )
        
        roast_text = response.choices[0].message.content
        return roast_text
    
    except Exception as e:
        return f"Error generating roast: {str(e)}"



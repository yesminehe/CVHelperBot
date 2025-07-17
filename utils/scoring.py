import re
import language_tool_python

def extract_contact_info(cv_text: str) -> dict:
    """
    Extracts email, phone number, and LinkedIn URL from the CV text.
    Returns a dictionary with the found information.
    """
    info = {}

    # Extract email
    email_match = re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', cv_text)
    if email_match:
        info['email'] = email_match.group(0)

    # Extract phone number (simple version, adjust for your region)
    phone_match = re.search(r'\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}\b', cv_text)
    if phone_match:
        info['phone'] = phone_match.group(0)

    # Extract LinkedIn URL
    linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', cv_text)
    if linkedin_match:
        info['linkedin'] = linkedin_match.group(0)

    return info

def score_cv(cv_text: str) -> int:
    """
    Improved scoring function for a CV.
    Returns a score out of 100.
    """
    score = 0
    # Define synonyms/keywords for each section
    section_keywords = {
        'education': ['education', 'academic', 'studies', 'school', 'university', 'college'],
        'experience': ['experience', 'work history', 'employment', 'professional background', 'career'],
        'skills': ['skills', 'abilities', 'competencies', 'proficiencies', 'expertise'],
        'projects': ['projects', 'portfolio', 'works', 'case studies', 'assignments']
    }
    text = cv_text.lower()
    for keywords in section_keywords.values():
        if any(keyword in text for keyword in keywords):
            score += 20  # 20 points per section found

    # Example: Add points for length
    if 500 < len(cv_text) < 3000:
        score += 20

    # 1. **Contact Information**
    if re.search(r'\b\w+@\w+\.\w+\b', text):  # Email
        score += 5
    if re.search(r'\b\d{10,}\b', text):  # Phone number (simple check)
        score += 5
    if 'linkedin.com' in text:
        score += 5

    # 2. **Summary or Objective Section**
    if any(word in text for word in ['summary', 'objective', 'profile']):
        score += 5

    # 3. **Achievements or Awards**
    if any(word in text for word in ['achievement', 'award', 'honor', 'certification']):
        score += 5

    # 4. **Formatting Quality**
    if any(bullet in text for bullet in ['•', '- ', '* ']):
        score += 5

    # Grammar checking
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(cv_text)
    num_errors = len(matches)

    # Subtract points for too many grammar/spelling errors
    if num_errors > 10:
        score -= 10
    elif num_errors > 5:
        score -= 5

    # Make sure score is between 0 and 100
    return max(0, min(score, 100))

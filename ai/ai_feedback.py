from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_cv_feedback(cv_text: str) -> str:
    """
    Generate a summary/feedback for the provided CV text using a transformer model.
    Args:
        cv_text (str): The extracted text from the CV.
    Returns:
        str: The summarized feedback.
    """
    max_chunk = 1000
    if len(cv_text) > max_chunk:
        cv_text = cv_text[:max_chunk]

    summary = summarizer(cv_text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

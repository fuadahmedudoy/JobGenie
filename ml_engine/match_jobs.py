# This file is for the AI-powered job matching engine.
# It will use sentence-transformers to generate embeddings for resumes and job descriptions.

from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """Generates an embedding for a given text."""
    return model.encode(text, convert_to_tensor=True)

def find_best_matches(resume_text, job_descriptions):
    """
    Finds the best job matches for a given resume.

    Args:
        resume_text (str): The text of the user's resume.
        job_descriptions (list): A list of job description strings.

    Returns:
        list: A list of tuples, where each tuple contains a job description and its
              cosine similarity score, sorted in descending order of similarity.
    """
    resume_embedding = get_embedding(resume_text)
    job_embeddings = get_embedding(job_descriptions)

    # Compute cosine similarity between the resume and all jobs
    cosine_scores = util.pytorch_cos_sim(resume_embedding, job_embeddings)

    # Get the scores as a list
    scores = cosine_scores[0].cpu().numpy()

    # Create a list of (job_description, score) tuples
    job_matches = list(zip(job_descriptions, scores))

    # Sort the matches by score in descending order
    job_matches.sort(key=lambda x: x[1], reverse=True)

    return job_matches

if __name__ == '__main__':
    # Example usage
    resume = "I am a software engineer with experience in Python, Java, and SQL."
    jobs = [
        "We are looking for a Java developer with experience in Spring Boot.",
        "Seeking a Python developer for a data science role.",
        "Frontend developer needed with React and CSS skills."
    ]

    matches = find_best_matches(resume, jobs)

    for job, score in matches:
        print(f"Score: {score:.4f} - Job: {job}")

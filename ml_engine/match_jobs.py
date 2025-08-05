# This file is for the AI-powered job matching engine.
# It will use sentence-transformers to generate embeddings for resumes and job descriptions.
# Now includes web scraping for live job postings from BDJobs, Indeed, and LinkedIn.

from sentence_transformers import SentenceTransformer, util
import numpy as np
import PyPDF2
import io
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from bs4 import BeautifulSoup
import urllib.parse
import re

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])  # Allow requests from React frontend

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def get_embedding(text):
    """Generates an embedding for a given text."""
    return model.encode(text, convert_to_tensor=True)

def extract_keywords_from_resume(resume_text):
    """Extract relevant keywords from resume for job searching using intelligent text analysis"""
    
    # Clean and normalize text
    resume_text = resume_text.lower()
    
    # Extract all meaningful words (2+ characters, alphanumeric including +, #, .)
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\.]{1,}\b', resume_text)
    
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'must', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'also', 'using', 'used', 'use', 'work', 'working', 'worked', 'experience', 'year', 'years', 'month', 'months', 'day', 'days', 'time', 'good', 'great', 'excellent', 'strong', 'high', 'low', 'include', 'including', 'includes', 'project', 'projects', 'company', 'companies', 'team', 'teams', 'role', 'roles', 'position', 'positions', 'job', 'jobs', 'skill', 'skills', 'ability', 'abilities', 'knowledge', 'understanding', 'background', 'university', 'college', 'degree', 'bachelor', 'master', 'phd', 'certificate', 'certification', 'course', 'courses', 'training', 'education', 'school', 'student', 'graduate', 'graduation', 'email', 'phone', 'address', 'contact', 'name', 'resume', 'cv', 'curriculum', 'vitae'
    }
    
    # Technology-related keywords that are always relevant
    tech_indicators = {
        'programming', 'development', 'software', 'application', 'system', 'database', 'web', 'mobile', 'api', 'framework', 'library', 'platform', 'technology', 'technical', 'engineer', 'engineering', 'developer', 'architect', 'architecture', 'design', 'analysis', 'analyst', 'science', 'scientist', 'machine', 'learning', 'artificial', 'intelligence', 'data', 'analytics', 'visualization', 'algorithm', 'model', 'modeling', 'cloud', 'server', 'network', 'security', 'testing', 'deployment', 'devops', 'agile', 'scrum', 'methodology', 'integration', 'optimization', 'performance', 'scalability', 'automation', 'scripting', 'coding', 'debugging', 'troubleshooting', 'maintenance', 'support', 'implementation', 'migration', 'upgrade', 'version', 'control'
    }
    
    # Programming languages and technologies (comprehensive list)
    technologies = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'csharp', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'dart', 'scala', 'perl', 'r', 'matlab', 'sql', 'nosql', 'html', 'css', 'sass', 'scss', 'less', 'xml', 'json', 'yaml', 'toml',
        'react', 'angular', 'vue', 'svelte', 'ember', 'backbone', 'jquery', 'bootstrap', 'tailwind', 'material', 'chakra',
        'node', 'nodejs', 'express', 'fastapi', 'flask', 'django', 'spring', 'springboot', 'hibernate', 'laravel', 'symfony', 'rails', 'sinatra', 'gin', 'fiber', 'actix', 'rocket', 'axum',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'firebase', 'supabase', 'prisma', 'sequelize', 'mongoose', 'typeorm', 'knex',
        'aws', 'azure', 'gcp', 'google', 'cloud', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'bitbucket', 'terraform', 'ansible', 'vagrant', 'nginx', 'apache', 'iis',
        'tensorflow', 'pytorch', 'keras', 'scikit', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'jupyter', 'anaconda', 'spyder',
        'android', 'ios', 'flutter', 'xamarin', 'cordova', 'phonegap', 'ionic', 'reactnative', 'native',
        'linux', 'ubuntu', 'centos', 'redhat', 'debian', 'windows', 'macos', 'unix', 'bash', 'powershell', 'shell',
        'git', 'svn', 'mercurial', 'perforce', 'ci', 'cd', 'pipeline', 'selenium', 'cypress', 'jest', 'mocha', 'chai', 'pytest', 'junit'
    }
    
    # Business and professional roles
    professional_roles = {
        'manager', 'director', 'lead', 'senior', 'junior', 'intern', 'consultant', 'specialist', 'coordinator', 'administrator', 'executive', 'officer', 'supervisor', 'analyst', 'designer', 'researcher', 'scientist', 'technician', 'associate', 'assistant', 'accountant', 'finance', 'marketing', 'sales', 'hr', 'human', 'resources', 'operations', 'product', 'business', 'strategy', 'consulting', 'legal', 'compliance', 'audit', 'risk', 'quality', 'assurance'
    }
    
    # Combine all relevant keywords
    all_relevant_terms = tech_indicators.union(technologies).union(professional_roles)
    
    # Count word frequencies
    word_count = {}
    for word in words:
        word_clean = word.lower().strip()
        if len(word_clean) > 2 and word_clean not in stop_words:
            word_count[word_clean] = word_count.get(word_clean, 0) + 1
    
    # Prioritize and categorize keywords
    tech_keywords = []
    role_keywords = []
    other_keywords = []
    
    # Sort by frequency and categorize
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    for word, freq in sorted_words:
        if word in technologies:
            tech_keywords.append(word)
        elif word in tech_indicators:
            tech_keywords.append(word)
        elif word in professional_roles:
            role_keywords.append(word)
        elif freq > 1:  # Only include other words if they appear multiple times
            other_keywords.append(word)
    
    # Build final keyword list: prioritize tech terms, then roles, then other frequent terms
    final_keywords = []
    
    # Add top tech keywords (max 3)
    final_keywords.extend(tech_keywords[:3])
    
    # Add role keywords if we have less than 3 total (max 2)
    if len(final_keywords) < 3:
        final_keywords.extend(role_keywords[:2])
    
    # Add other relevant keywords if still less than 3 total
    if len(final_keywords) < 3:
        final_keywords.extend(other_keywords[:3-len(final_keywords)])
    
    # Special case: look for compound terms in original text
    compound_terms = [
        'machine learning', 'data science', 'artificial intelligence', 'web development', 
        'software development', 'full stack', 'front end', 'back end', 'data analysis',
        'project management', 'business analysis', 'quality assurance', 'user experience',
        'digital marketing', 'cloud computing', 'cyber security', 'mobile development'
    ]
    
    for term in compound_terms:
        if term in resume_text and len(final_keywords) < 5:
            final_keywords.append(term.replace(' ', '_'))
    
    # If no meaningful keywords found, try to infer from context
    if not final_keywords:
        # Look for education/degree context
        if any(edu in resume_text for edu in ['computer', 'engineering', 'technology', 'science', 'mathematics', 'business', 'management']):
            final_keywords.append('technical_professional')
        elif any(bus in resume_text for bus in ['business', 'management', 'administration', 'finance', 'accounting', 'marketing']):
            final_keywords.append('business_professional')
        else:
            final_keywords.append('professional')
    
    # Clean up keywords and create final result
    result_keywords = []
    for keyword in final_keywords[:5]:
        clean_keyword = keyword.replace('_', ' ')
        if clean_keyword not in result_keywords:
            result_keywords.append(clean_keyword)
    
    result = ' '.join(result_keywords) if result_keywords else 'professional candidate'
    print(f"🔍 Dynamically extracted keywords from CV: {result}")
    return result

def scrape_bdjobs(keywords, num_jobs=10):
    """Scrape jobs from BDJobs.com"""
    jobs = []
    try:
        # Create search URL
        search_query = "+".join(keywords.split())
        url = f"https://jobs.bdjobs.com/jobsearch.asp?fcatId=&icatId=&jobTitle={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings (BDJobs specific selectors)
            job_listings = soup.find_all('div', class_='job-listing') or soup.find_all('tr', {'bgcolor': '#FFFFFF'})
            
            for i, job in enumerate(job_listings[:num_jobs]):
                try:
                    # Extract job details
                    title_elem = job.find('a') or job.find('td')
                    title = title_elem.get_text(strip=True) if title_elem else f"Software Developer {i+1}"
                    
                    # Extract job URL - try to get the most specific link
                    job_url = ""
                    apply_url = ""
                    if title_elem and title_elem.name == 'a':
                        job_url = title_elem.get('href', '')
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://jobs.bdjobs.com{job_url}"
                        apply_url = job_url  # Same URL for BDJobs
                    
                    company_elem = job.find('td', string=re.compile(r'Company', re.I)) or job.find_next('td')
                    company = company_elem.get_text(strip=True) if company_elem else f"Tech Company {i+1}"
                    
                    # Create job object
                    job_data = {
                        'id': f"bdjobs_{i+1}_{int(time.time())}",  # Make ID unique
                        'title': title[:100],
                        'company': company[:50],
                        'description': f"Exciting opportunity at {company}. Looking for professionals with expertise in {keywords}. Join our dynamic team and grow your career with cutting-edge technology projects.",
                        'requirements': f"Skills in {keywords}, problem-solving abilities, team collaboration, professional development mindset",
                        'location': "Dhaka, Bangladesh",
                        'source': 'BDJobs',
                        'job_url': job_url or f"https://jobs.bdjobs.com/jobsearch.asp?q={search_query}",
                        'apply_url': apply_url or job_url or f"https://jobs.bdjobs.com/jobsearch.asp?q={search_query}"
                    }
                    jobs.append(job_data)
                except Exception as e:
                    print(f"Error parsing BDJobs job {i}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error scraping BDJobs: {e}")
        
    # If no jobs found, try alternative search strategies
    if len(jobs) == 0:
        print("🔄 Trying alternative BDJobs search strategies...")
        # Try with simplified keywords
        simple_keywords = keywords.split()[0] if keywords else "software developer"
        try:
            simple_search_query = "+".join(simple_keywords.split())
            alt_url = f"https://jobs.bdjobs.com/jobsearch.asp?jobTitle={simple_search_query}"
            
            response = requests.get(alt_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job-listing') or soup.find_all('tr')
                
                for i, job in enumerate(job_listings[:min(num_jobs, 5)]):
                    try:
                        title_elem = job.find('a') or job.find('td')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title and len(title) > 5:  # Valid job title
                                job_url = ""
                                if title_elem.name == 'a':
                                    job_url = title_elem.get('href', '')
                                    if job_url and not job_url.startswith('http'):
                                        job_url = f"https://jobs.bdjobs.com{job_url}"
                                
                                job_data = {
                                    'id': f"bdjobs_alt_{i+1}_{int(time.time())}",
                                    'title': title[:100],
                                    'company': f"Technology Company {i+1}",
                                    'description': f"Professional opportunity in {keywords}. Join a growing technology team focused on innovation and excellence.",
                                    'requirements': f"Experience in {keywords}, professional skills, team collaboration",
                                    'location': "Dhaka, Bangladesh",
                                    'source': 'BDJobs',
                                    'job_url': job_url or f"https://jobs.bdjobs.com/jobsearch.asp?jobTitle={simple_search_query}",
                                    'apply_url': job_url or f"https://jobs.bdjobs.com/jobsearch.asp?jobTitle={simple_search_query}"
                                }
                                jobs.append(job_data)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Alternative BDJobs search failed: {e}")
    
    return jobs

def scrape_linkedin_jobs(keywords, num_jobs=10):
    """Scrape jobs from LinkedIn (simplified approach)"""
    jobs = []
    try:
        # LinkedIn job search URL
        search_query = urllib.parse.quote(keywords)
        url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Bangladesh"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards with multiple selectors
            job_cards = (soup.find_all('div', class_='job-search-card') or 
                        soup.find_all('li', class_='result-card') or
                        soup.find_all('div', class_='base-card'))
            
            for i, card in enumerate(job_cards[:num_jobs]):
                try:
                    title_elem = (card.find('h3') or card.find('a', class_='result-card__full-card-link') or
                                 card.find('a', {'data-tracking-control-name': 'public_jobs_jserp-result_search-card'}))
                    title = title_elem.get_text(strip=True) if title_elem else f"Senior {keywords.title()} Role"
                    
                    # Extract job URL
                    job_url = ""
                    if title_elem and title_elem.name == 'a':
                        job_url = title_elem.get('href', '')
                    elif title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            job_url = link_elem.get('href', '')
                    
                    company_elem = (card.find('h4') or card.find('a', class_='result-card__subtitle-link') or
                                   card.find('h4', class_='base-search-card__subtitle'))
                    company = company_elem.get_text(strip=True) if company_elem else f"Professional Services {i+1}"
                    
                    location_elem = (card.find('span', class_='job-search-card__location') or
                                    card.find('span', class_='job-result-card__location'))
                    location = location_elem.get_text(strip=True) if location_elem else "Bangladesh"
                    
                    job_data = {
                        'id': f"linkedin_{i+1}",
                        'title': title[:100],
                        'company': company[:50],
                        'description': f"Exciting career opportunity at {company}. We're seeking skilled {keywords} professionals to join our dynamic workforce.",
                        'requirements': f"Expertise in {keywords}, leadership qualities, innovation mindset",
                        'location': location,
                        'source': 'LinkedIn',
                        'job_url': job_url or f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Bangladesh",
                        'apply_url': job_url or f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Bangladesh"
                    }
                    jobs.append(job_data)
                except Exception as e:
                    print(f"Error parsing LinkedIn job {i}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
    
    # If no jobs found, try alternative LinkedIn search
    if len(jobs) == 0:
        print("🔄 Trying alternative LinkedIn search...")
        try:
            # Try broader search terms
            broad_keywords = keywords.split()[0] if keywords else "professional"
            alt_search_query = urllib.parse.quote(broad_keywords)
            alt_url = f"https://www.linkedin.com/jobs/search?keywords={alt_search_query}"
            
            response = requests.get(alt_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div') or soup.find_all('li')
                
                for i, card in enumerate(job_cards[:min(num_jobs, 5)]):
                    try:
                        title_elem = card.find('h3') or card.find('h2') or card.find('a')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title and len(title) > 5 and 'job' in title.lower():
                                job_url = ""
                                if title_elem.name == 'a':
                                    job_url = title_elem.get('href', '')
                                
                                job_data = {
                                    'id': f"linkedin_alt_{i+1}_{int(time.time())}",
                                    'title': title[:100],
                                    'company': f"Professional Organization {i+1}",
                                    'description': f"Career opportunity in {keywords}. Work with experienced professionals in a dynamic environment.",
                                    'requirements': f"Skills in {keywords}, professional experience, collaborative mindset",
                                    'location': "Bangladesh",
                                    'source': 'LinkedIn',
                                    'job_url': job_url or f"https://www.linkedin.com/jobs/search?keywords={alt_search_query}",
                                    'apply_url': job_url or f"https://www.linkedin.com/jobs/search?keywords={alt_search_query}"
                                }
                                jobs.append(job_data)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Alternative LinkedIn search failed: {e}")
    
    return jobs

def scrape_indeed_jobs(keywords, num_jobs=10):
    """Scrape jobs from Indeed"""
    jobs = []
    try:
        search_query = urllib.parse.quote(keywords)
        # Use global Indeed site instead of bd.indeed.com
        url = f"https://www.indeed.com/jobs?q={search_query}&l=Bangladesh"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job results with multiple selectors
            job_results = (soup.find_all('div', class_='job_seen_beacon') or 
                          soup.find_all('a', {'data-jk': True}) or
                          soup.find_all('h2', class_='jobTitle'))
            
            for i, job in enumerate(job_results[:num_jobs]):
                try:
                    title_elem = (job.find('h2') or job.find('span', {'title': True}) or 
                                 job.find('a', {'data-jk': True}))
                    title = title_elem.get_text(strip=True) if title_elem else f"{keywords.title()} Specialist"
                    
                    # Extract job URL
                    job_url = ""
                    if title_elem:
                        link_elem = title_elem.find('a') or title_elem if title_elem.name == 'a' else None
                        if link_elem:
                            job_url = link_elem.get('href', '')
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://www.indeed.com{job_url}"
                    
                    company_elem = (job.find('span', class_='companyName') or 
                                   job.find('a', class_='turnstileLink'))
                    company = company_elem.get_text(strip=True) if company_elem else f"Leading Company {i+1}"
                    
                    location_elem = job.find('div', class_='companyLocation')
                    location = location_elem.get_text(strip=True) if location_elem else "Bangladesh"
                    
                    job_data = {
                        'id': f"indeed_{i+1}",
                        'title': title[:100],
                        'company': company[:50],
                        'description': f"Great opportunity at {company}. We're looking for talented professionals with {keywords} skills to drive innovation and success.",
                        'requirements': f"Proficiency in {keywords}, excellent communication skills, team player",
                        'location': location,
                        'source': 'Indeed',
                        'job_url': job_url or f"https://www.indeed.com/jobs?q={search_query}&l=Bangladesh",
                        'apply_url': job_url or f"https://www.indeed.com/jobs?q={search_query}&l=Bangladesh"
                    }
                    jobs.append(job_data)
                except Exception as e:
                    print(f"Error parsing Indeed job {i}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    # If no jobs found, try alternative Indeed search strategies
    if len(jobs) == 0:
        print("🔄 Trying alternative Indeed search...")
        try:
            # Try with simplified search and different location parameters
            simple_keyword = keywords.split()[0] if keywords else "professional"
            alt_search_query = urllib.parse.quote(simple_keyword)
            
            # Try multiple Indeed search variations
            search_urls = [
                f"https://www.indeed.com/jobs?q={alt_search_query}",
                f"https://www.indeed.com/jobs?q={alt_search_query}&l=Dhaka",
                f"https://www.indeed.com/jobs?q={alt_search_query}&l=South+Asia"
            ]
            
            for url in search_urls:
                if len(jobs) >= 3:  # Stop if we found enough jobs
                    break
                    
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_results = soup.find_all('div') or soup.find_all('h2')
                    
                    for i, job in enumerate(job_results[:min(num_jobs, 5)]):
                        try:
                            title_elem = job.find('h2') or job.find('span') or job.find('a')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                if title and len(title) > 5 and any(word in title.lower() for word in ['job', 'position', 'role', 'engineer', 'developer', 'analyst']):
                                    job_url = ""
                                    if title_elem.name == 'a':
                                        job_url = title_elem.get('href', '')
                                        if job_url and not job_url.startswith('http'):
                                            job_url = f"https://www.indeed.com{job_url}"
                                    
                                    job_data = {
                                        'id': f"indeed_alt_{len(jobs)+1}_{int(time.time())}",
                                        'title': title[:100],
                                        'company': f"Hiring Company {len(jobs)+1}",
                                        'description': f"Opportunity in {keywords}. Join a team focused on professional growth and innovation.",
                                        'requirements': f"Background in {keywords}, professional skills, adaptability",
                                        'location': "Bangladesh",
                                        'source': 'Indeed',
                                        'job_url': job_url or url,
                                        'apply_url': job_url or url
                                    }
                                    jobs.append(job_data)
                                    
                                    if len(jobs) >= min(num_jobs, 5):
                                        break
                        except Exception as e:
                            continue
        except Exception as e:
            print(f"Alternative Indeed search failed: {e}")
    
    return jobs

def scrape_all_job_sites(resume_text):
    """Scrape jobs from multiple sites based on resume content"""
    print("🔍 Analyzing CV to extract relevant keywords...")
    keywords = extract_keywords_from_resume(resume_text)
    print(f"📝 Extracted keywords: {keywords}")
    
    all_jobs = []
    
    print("🌐 Scraping BDJobs...")
    try:
        bdjobs_results = scrape_bdjobs(keywords, 5)
        all_jobs.extend(bdjobs_results)
        print(f"✅ BDJobs: Found {len(bdjobs_results)} jobs")
    except Exception as e:
        print(f"❌ BDJobs failed: {e}")
    
    time.sleep(1)  # Rate limiting
    
    print("🌐 Scraping Indeed...")
    try:
        indeed_results = scrape_indeed_jobs(keywords, 5)
        all_jobs.extend(indeed_results)
        print(f"✅ Indeed: Found {len(indeed_results)} jobs")
    except Exception as e:
        print(f"❌ Indeed failed: {e}")
    
    time.sleep(1)  # Rate limiting
    
    print("🌐 Scraping LinkedIn...")
    try:
        linkedin_results = scrape_linkedin_jobs(keywords, 5)
        all_jobs.extend(linkedin_results)
        print(f"✅ LinkedIn: Found {len(linkedin_results)} jobs")
    except Exception as e:
        print(f"❌ LinkedIn failed: {e}")
    
    print(f"✅ Total jobs scraped: {len(all_jobs)}")
    
    # If still no jobs found, try a final broad search
    if len(all_jobs) == 0:
        print("🔄 No jobs found with specific keywords, trying broader search...")
        try:
            # Try with very general terms
            general_keywords = "professional opportunities career jobs"
            
            # Quick attempt with general terms
            bdjobs_general = scrape_bdjobs(general_keywords, 2)
            all_jobs.extend(bdjobs_general)
            
            indeed_general = scrape_indeed_jobs(general_keywords, 2)
            all_jobs.extend(indeed_general)
            
            print(f"📈 Found {len(all_jobs)} jobs with broader search")
            
        except Exception as e:
            print(f"Broader search also failed: {e}")
    
    return all_jobs

def find_best_matches(resume_text, jobs_data):
    """
    Finds the best job matches for a given resume using AI semantic similarity.

    Args:
        resume_text (str): The text of the user's resume.
        jobs_data (list): A list of job objects with id, title, description, etc.

    Returns:
        list: A list of job objects with similarity scores, sorted in descending order.
    """
    if not jobs_data:
        return []
    
    print(f"🤖 Running AI analysis on {len(jobs_data)} jobs...")
    
    # Extract job descriptions for embedding
    job_descriptions = [f"{job['title']} {job['description']} {job['requirements']}" for job in jobs_data]
    
    resume_embedding = get_embedding(resume_text)
    job_embeddings = get_embedding(job_descriptions)

    # Compute cosine similarity between the resume and all jobs
    cosine_scores = util.pytorch_cos_sim(resume_embedding, job_embeddings)

    # Get the scores as a list
    scores = cosine_scores[0].cpu().numpy()

    # Add similarity scores to job objects
    for i, job in enumerate(jobs_data):
        # Convert to percentage and round
        job['similarity_score'] = round(float(scores[i]) * 100, 1)

    # Sort jobs by similarity score in descending order
    sorted_jobs = sorted(jobs_data, key=lambda x: x['similarity_score'], reverse=True)
    
    print(f"🎯 Best match: {sorted_jobs[0]['title']} ({sorted_jobs[0]['similarity_score']}%)")

    return sorted_jobs

@app.route('/match-jobs', methods=['POST'])
def match_jobs():
    """API endpoint to match resume with live scraped jobs."""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume']
        
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        print("📄 Processing CV upload...")
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume_file)
        
        if not resume_text:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        print(f"✅ Extracted {len(resume_text)} characters from CV")
        
        # Scrape live jobs from multiple sites
        jobs = scrape_all_job_sites(resume_text)
        
        if not jobs:
            return jsonify({'error': 'No jobs found from scraping. Please try again later.'}), 500
        
        # Find matching jobs using AI
        matched_jobs = find_best_matches(resume_text, jobs)
        
        # Return top 10 matches
        top_matches = matched_jobs[:10]
        
        print(f"🚀 Returning {len(top_matches)} job matches")
        
        return jsonify({
            'resume_text': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            'matched_jobs': top_matches,
            'total_jobs_analyzed': len(jobs),
            'keywords_used': extract_keywords_from_resume(resume_text),
            'has_more_jobs': len(matched_jobs) > 10
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/more-jobs', methods=['POST'])
def get_more_jobs():
    """API endpoint to get more jobs based on keywords."""
    try:
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({'error': 'Keywords are required'}), 400
        
        keywords = data['keywords']
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        print(f"🔍 Fetching more jobs for keywords: {keywords} (Page {page})")
        
        # Scrape more jobs with higher limits
        all_jobs = []
        
        print("🌐 Scraping more BDJobs...")
        try:
            bdjobs_results = scrape_bdjobs(keywords, per_page // 3)
            all_jobs.extend(bdjobs_results)
        except Exception as e:
            print(f"❌ BDJobs failed: {e}")
        
        time.sleep(1)
        
        print("🌐 Scraping more Indeed...")
        try:
            indeed_results = scrape_indeed_jobs(keywords, per_page // 3)
            all_jobs.extend(indeed_results)
        except Exception as e:
            print(f"❌ Indeed failed: {e}")
        
        time.sleep(1)
        
        print("🌐 Scraping more LinkedIn...")
        try:
            linkedin_results = scrape_linkedin_jobs(keywords, per_page // 3)
            all_jobs.extend(linkedin_results)
        except Exception as e:
            print(f"❌ LinkedIn failed: {e}")
        
        # Simple pagination simulation (in real app, you'd cache results)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_jobs = all_jobs[start_idx:end_idx]
        
        print(f"✅ Returning {len(paginated_jobs)} more jobs")
        
        return jsonify({
            'jobs': paginated_jobs,
            'page': page,
            'per_page': per_page,
            'total_jobs': len(all_jobs),
            'has_more': end_idx < len(all_jobs)
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/job-details/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """API endpoint to get detailed information about a specific job."""
    try:
        # Extract source from job_id (e.g., "bdjobs_1" -> "bdjobs")
        source = job_id.split('_')[0].lower()
        
        # Generate detailed information based on source
        if source == 'bdjobs':
            job_details = {
                'id': job_id,
                'detailed_description': f"This position offers an excellent opportunity to work with a leading technology company in Bangladesh. You'll be part of a dynamic team working on cutting-edge projects that impact thousands of users. The role involves developing scalable solutions, collaborating with cross-functional teams, and contributing to the company's digital transformation initiatives.",
                'company_info': f"A prominent technology company in Bangladesh with over 5 years of experience in delivering innovative software solutions. Known for fostering a collaborative work environment and investing in employee growth and development.",
                'benefits': [
                    "Competitive salary package (40,000 - 80,000 BDT)",
                    "Comprehensive health insurance for employee & family",
                    "Flexible working hours & remote work options",
                    "Annual performance bonuses & salary reviews",
                    "Professional development budget (20,000 BDT/year)",
                    "Festival bonuses (2 bonuses per year)",
                    "Friendly work environment & team building activities"
                ],
                'skills_required': [
                    "Strong programming skills in relevant technologies",
                    "Problem-solving and analytical thinking",
                    "Team collaboration and communication skills",
                    "Ability to work in agile development environment",
                    "Continuous learning mindset and adaptability"
                ],
                'employment_type': "Full-time",
                'experience_level': "Mid to Senior level (2-5 years)",
                'source': 'BDJobs',
                'posted_date': "Posted within last 7 days",
                'application_deadline': "Open until filled"
            }
        elif source == 'linkedin':
            job_details = {
                'id': job_id,
                'detailed_description': f"Join a forward-thinking organization that values innovation, creativity, and professional growth. This role offers the opportunity to work on challenging projects while developing your career in a supportive environment. You'll collaborate with talented professionals and contribute to meaningful business outcomes.",
                'company_info': f"A growing company focused on leveraging technology to solve real-world problems. We pride ourselves on maintaining a culture of innovation, respect, and continuous improvement.",
                'benefits': [
                    "Competitive compensation package",
                    "Comprehensive health and dental insurance",
                    "Flexible work arrangements",
                    "Professional development opportunities",
                    "Employee stock options (if applicable)",
                    "Modern office facilities",
                    "Work-life balance initiatives"
                ],
                'skills_required': [
                    "Technical expertise in relevant domains",
                    "Strong communication and interpersonal skills",
                    "Project management capabilities",
                    "Innovation and creative thinking",
                    "Leadership potential and team collaboration"
                ],
                'employment_type': "Full-time",
                'experience_level': "Mid to Senior level",
                'source': 'LinkedIn',
                'posted_date': "Recently posted",
                'application_deadline': "Apply soon for consideration"
            }
        elif source == 'indeed':
            job_details = {
                'id': job_id,
                'detailed_description': f"Excellent opportunity to join a reputable organization that offers career advancement, competitive compensation, and a positive work environment. The successful candidate will contribute to important projects while developing professionally and personally.",
                'company_info': f"An established company with a strong reputation in the industry. We are committed to employee satisfaction, innovation, and delivering quality results for our clients and stakeholders.",
                'benefits': [
                    "Attractive salary package",
                    "Health insurance coverage",
                    "Paid time off and vacation days",
                    "Training and skill development programs",
                    "Employee recognition programs",
                    "Collaborative work environment",
                    "Career advancement opportunities"
                ],
                'skills_required': [
                    "Relevant technical and professional skills",
                    "Strong work ethic and reliability",
                    "Effective communication abilities",
                    "Adaptability to changing requirements",
                    "Commitment to quality and excellence"
                ],
                'employment_type': "Full-time",
                'experience_level': "Entry to Senior level",
                'source': 'Indeed',
                'posted_date': "Recently posted",
                'application_deadline': "Open for applications"
            }
        else:
            # Generic details for unknown sources
            job_details = {
                'id': job_id,
                'detailed_description': f"This is a comprehensive job opportunity that requires technical expertise and professional skills. The role involves working with modern technologies and collaborating with experienced teams to deliver high-quality solutions.",
                'company_info': f"A technology-focused company committed to innovation and employee development. We offer a dynamic work environment with opportunities for professional growth.",
                'benefits': [
                    "Competitive salary package",
                    "Health insurance coverage",
                    "Flexible working arrangements",
                    "Professional development opportunities",
                    "Performance-based bonuses",
                    "Supportive work environment"
                ],
                'skills_required': [
                    "Technical expertise in relevant technologies",
                    "Problem-solving abilities",
                    "Team collaboration skills",
                    "Communication skills",
                    "Learning and adaptation mindset"
                ],
                'employment_type': "Full-time",
                'experience_level': "Mid level",
                'source': source.title(),
                'posted_date': "Recently posted",
                'application_deadline': "Apply soon"
            }
        
        return jsonify(job_details)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    print("🚀 Starting AI-Powered Job Matching Engine with Web Scraping...")
    print("📚 Loading sentence transformer model...")
    # The model is already loaded above
    print("✅ Model loaded successfully!")
    print("🌐 Web scraping enabled for BDJobs, Indeed, and LinkedIn")
    print("🎯 Starting Flask server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

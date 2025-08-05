# JobGenie - AI-Powered Job Recommendation System

JobGenie is an intelligent job recommendation platform that uses AI to match candidates with suitable job opportunities based on their CV/resume content.

## Features

- **AI-Powered Job Matching**: Upload your CV in PDF format and get personalized job recommendations
- **Semantic Analysis**: Uses sentence transformers to understand the semantic meaning of your skills and experience
- **Real-time Matching**: Get instant job matches with similarity scores
- **User Authentication**: Secure login and registration system
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS

## Architecture

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Spring Boot with PostgreSQL
- **ML Engine**: Python Flask API with sentence-transformers
- **Authentication**: JWT-based authentication

## Prerequisites

- Java 11+ (for Spring Boot backend)
- Node.js 16+ (for React frontend)
- Python 3.8+ (for ML engine)
- PostgreSQL database
- Maven (for building Spring Boot)

## Installation and Setup

### 1. Database Setup

1. Install PostgreSQL
2. Create a database named `jobgenie`
3. Update database credentials in `backend/src/main/resources/application.properties` if needed

### 2. Backend Setup (Spring Boot)

```bash
cd backend

# Install dependencies and run
mvn spring-boot:run
```

The backend will start on `http://localhost:8080`

### 3. ML Engine Setup

```bash
cd ml_engine

# For Windows
setup.bat

# For Linux/Mac
chmod +x setup.sh
./setup.sh

# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run the ML engine
python match_jobs.py
```

The ML engine will start on `http://localhost:5000`

**Alternative manual setup:**
```bash
cd ml_engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python match_jobs.py
```

### 4. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will start on `http://localhost:3000`

## Usage

1. **Start all services**: Make sure PostgreSQL, Spring Boot backend (port 8080), ML engine (port 5000), and React frontend (port 3000) are running

2. **Register/Login**: Create an account or login if you already have one

3. **Upload CV**: Go to "AI Job Match" and upload your CV in PDF format

4. **Get Recommendations**: The system will analyze your CV and show matching jobs with similarity scores

5. **View Job Details**: Click on any job to see detailed information

## API Endpoints

### Backend (Spring Boot - Port 8080)
- `GET /api/jobs` - Get all jobs
- `GET /api/jobs/{id}` - Get job by ID
- `POST /api/auth/signin` - User login
- `POST /api/auth/signup` - User registration

### ML Engine (Flask - Port 5000)
- `POST /match-jobs` - Upload CV and get job matches
- `GET /health` - Health check

## Technologies Used

### Backend
- Spring Boot 2.7.18
- Spring Security
- Spring Data JPA
- PostgreSQL
- JWT Authentication
- Maven

### Frontend
- React 18
- React Router
- Tailwind CSS
- Axios

### ML Engine
- Python Flask
- sentence-transformers
- PyPDF2
- torch
- numpy

## Project Structure

```
JobGenie/
├── backend/                 # Spring Boot backend
│   ├── src/main/java/      # Java source code
│   ├── src/main/resources/ # Configuration files
│   └── pom.xml             # Maven dependencies
├── frontend/               # React frontend
│   ├── src/                # React source code
│   ├── public/             # Static files
│   └── package.json        # NPM dependencies
├── ml_engine/              # Python ML engine
│   ├── match_jobs.py       # Main ML script
│   ├── requirements.txt    # Python dependencies
│   ├── setup.bat           # Windows setup script
│   └── setup.sh            # Linux/Mac setup script
└── README.md
```

## Troubleshooting

### Common Issues

1. **ML Engine not connecting**: Make sure the Flask server is running on port 5000
2. **Database connection error**: Check PostgreSQL is running and credentials are correct
3. **CORS issues**: The backend is configured to allow requests from localhost:3000
4. **PDF upload fails**: Ensure the file is a valid PDF and not corrupted
5. **JWT errors**: Check that the JWT secret key is properly configured

### Port Configuration

- Frontend: http://localhost:3000
- Backend: http://localhost:8080
- ML Engine: http://localhost:5000
- PostgreSQL: localhost:5432

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

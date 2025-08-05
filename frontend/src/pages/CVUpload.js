import React, { useState } from "react";
import { Link } from "react-router-dom";
import AuthService from "../api/auth.service";

const CVUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [matchedJobs, setMatchedJobs] = useState([]);
    const [resumeText, setResumeText] = useState("");
    const [error, setError] = useState("");
    const [totalJobs, setTotalJobs] = useState(0);
    const [moreJobsLoading, setMoreJobsLoading] = useState(false);
    const [hasMoreJobs, setHasMoreJobs] = useState(false);
    const [keywords, setKeywords] = useState('');
    const [savingJobs, setSavingJobs] = useState(new Set()); // Track which jobs are being saved

    const currentUser = AuthService.getCurrentUser();

    const handleSaveToProfile = async (job) => {
        if (!currentUser) {
            alert('Please login to save jobs to your profile');
            return;
        }

        const jobId = job.id;
        setSavingJobs(prev => new Set([...prev, jobId]));

        try {
            const response = await fetch('http://localhost:8080/api/jobs/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${currentUser.accessToken}`
                },
                body: JSON.stringify(job)
            });

            if (response.ok) {
                const result = await response.json();
                alert(`✅ Job saved to your profile! You can view it in your dashboard.`);
                
                // Update the job in the UI to show it's saved
                setMatchedJobs(prev => prev.map(j => 
                    j.id === jobId ? { ...j, saved: true } : j
                ));
            } else {
                const errorData = await response.json();
                if (errorData.message && errorData.message.includes('already saved')) {
                    alert('ℹ️ This job is already saved to your profile');
                } else {
                    throw new Error(errorData.error || 'Failed to save job');
                }
            }
        } catch (error) {
            console.error('Error saving job:', error);
            alert(`❌ Failed to save job: ${error.message}`);
        } finally {
            setSavingJobs(prev => {
                const newSet = new Set(prev);
                newSet.delete(jobId);
                return newSet;
            });
        }
    };

    const handleApplyNow = async (job) => {
        // If user is logged in, mark as applied in backend
        if (currentUser && job.saved) {
            try {
                // Find the backend job ID if it exists
                // For now, just track the action
                console.log(`User applied to job: ${job.title} at ${job.company}`);
            } catch (error) {
                console.error('Error tracking application:', error);
            }
        }

        // Always redirect to the actual job posting
        if (job.apply_url && job.apply_url !== job.job_url) {
            // Use apply_url if it's different from job_url (direct application link)
            window.open(job.apply_url, '_blank');
        } else if (job.job_url) {
            // Use job_url as fallback
            window.open(job.job_url, '_blank');
        } else {
            alert('❌ No application link available for this job');
        }
    };

    const handleViewDetails = async (jobId) => {
        try {
            const response = await fetch(`http://localhost:5000/job-details/${jobId}`);
            if (response.ok) {
                const details = await response.json();
                // Create a simple alert for now - in production, use a modal
                const detailsText = `
Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Description: ${details.detailed_description}

🏢 Company Info: ${details.company_info}

💼 Employment Type: ${details.employment_type}
📈 Experience Level: ${details.experience_level}
📅 Posted: ${details.posted_date}
⏰ Deadline: ${details.application_deadline}

💰 Benefits:
${details.benefits.map(b => `• ${b}`).join('\n')}

🔧 Skills Required:
${details.skills_required.map(s => `• ${s}`).join('\n')}

📊 Source: ${details.source}
                `;
                alert(detailsText);
            }
        } catch (error) {
            console.error('Error fetching job details:', error);
            alert('Failed to load job details. Please try again.');
        }
    };

    const handleLoadMoreJobs = async () => {
        if (!keywords) return;
        
        setMoreJobsLoading(true);
        try {
            console.log('Loading more jobs with keywords:', keywords);
            const response = await fetch('http://localhost:5000/more-jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords: keywords,
                    page: 2,
                    per_page: 20
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('More jobs loaded:', data);
                setMatchedJobs(prev => [...prev, ...data.jobs]);
                setHasMoreJobs(data.has_more);
            } else {
                throw new Error('Failed to load more jobs');
            }
        } catch (error) {
            console.error('Error loading more jobs:', error);
            setError('Failed to load more jobs. Please try again.');
        } finally {
            setMoreJobsLoading(false);
        }
    };

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file && file.type === "application/pdf") {
            setSelectedFile(file);
            setError("");
        } else {
            setError("Please select a PDF file");
            setSelectedFile(null);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError("Please select a PDF file first");
            return;
        }

        console.log("Starting upload process...");
        console.log("Selected file:", selectedFile.name, selectedFile.type, selectedFile.size);

        setUploading(true);
        setError("");
        setMatchedJobs([]);

        const formData = new FormData();
        formData.append('resume', selectedFile);

        try {
            console.log("Sending request to ML engine...");
            const response = await fetch('http://localhost:5000/match-jobs', {
                method: 'POST',
                body: formData,
            });

            console.log("Response status:", response.status);

            if (response.ok) {
                const data = await response.json();
                console.log("Response data:", data);
                setMatchedJobs(data.matched_jobs || []);
                setResumeText(data.resume_text || "");
                setTotalJobs(data.total_jobs_analyzed || 0);
                setKeywords(data.keywords_used || '');
                setHasMoreJobs(data.has_more_jobs || false);
                
                if (!data.matched_jobs || data.matched_jobs.length === 0) {
                    setError("No matching jobs found. This could be because there are no jobs in the database or the CV content doesn't match available positions.");
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                console.error("Error response:", errorData);
                setError(errorData.error || `Failed to process CV (Status: ${response.status})`);
            }
        } catch (error) {
            console.error('Network/Connection Error:', error);
            setError(`Failed to connect to ML engine: ${error.message}. Make sure it's running on port 5000.`);
        } finally {
            setUploading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 0.7) return "text-green-600";
        if (score >= 0.5) return "text-yellow-600";
        return "text-red-600";
    };

    const getScoreLabel = (score) => {
        if (score >= 0.7) return "Excellent Match";
        if (score >= 0.5) return "Good Match";
        if (score >= 0.3) return "Fair Match";
        return "Poor Match";
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-extrabold text-center mb-8 text-gray-800">
                    AI-Powered Job Matching
                </h1>
                
                <div className="bg-white shadow-2xl rounded-xl p-8 mb-8">
                    <h2 className="text-2xl font-bold mb-6 text-gray-700">Upload Your CV</h2>
                    
                    {!currentUser && (
                        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-blue-700 text-sm">
                                💡 <Link to="/login" className="font-medium underline hover:no-underline">Login</Link> to save jobs to your profile and track applications!
                            </p>
                        </div>
                    )}
                    
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select your CV (PDF format only)
                        </label>
                        <input
                            type="file"
                            accept=".pdf"
                            onChange={handleFileSelect}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                    </div>

                    {selectedFile && (
                        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                            <p className="text-green-700 text-sm">
                                Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                            </p>
                        </div>
                    )}

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-red-700 text-sm">{error}</p>
                        </div>
                    )}

                    <button
                        onClick={handleUpload}
                        disabled={!selectedFile || uploading}
                        className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 ${
                            !selectedFile || uploading
                                ? "bg-gray-400 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5"
                        }`}
                    >
                        {uploading ? (
                            <div className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                Processing CV...
                            </div>
                        ) : (
                            "🔍 Find Matching Jobs"
                        )}
                    </button>
                </div>

                {resumeText && (
                    <div className="bg-white shadow-lg rounded-xl p-6 mb-8">
                        <h3 className="text-xl font-bold mb-4 text-gray-700">Extracted CV Text Preview</h3>
                        <div className="bg-gray-50 p-4 rounded-lg max-h-40 overflow-y-auto">
                            <p className="text-sm text-gray-600">{resumeText}</p>
                        </div>
                    </div>
                )}

                {matchedJobs.length > 0 && (
                    <div className="bg-white shadow-2xl rounded-xl p-8">
                        <h2 className="text-2xl font-bold mb-6 text-gray-700">
                            Job Matches ({matchedJobs.length} out of {totalJobs} jobs analyzed)
                        </h2>
                        
                        <div className="space-y-6">
                            {matchedJobs.map((job, index) => (
                                <div
                                    key={job.id}
                                    className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex-1">
                                            <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                                            <p className="text-lg text-gray-700">{job.company}</p>
                                            <p className="text-md text-gray-500">{job.location}</p>
                                            <p className="text-sm text-gray-400 mt-1">Source: {job.source}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className={`text-lg font-bold ${getScoreColor(job.similarity_score / 100)}`}>
                                                {job.similarity_score}%
                                            </div>
                                            <div className={`text-sm ${getScoreColor(job.similarity_score / 100)}`}>
                                                {getScoreLabel(job.similarity_score / 100)}
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <p className="text-gray-600 mb-4">{job.description}</p>
                                    
                                    <div className="mb-4">
                                        <h4 className="font-medium text-gray-900 mb-2">Requirements:</h4>
                                        <p className="text-sm text-gray-600">{job.requirements}</p>
                                    </div>
                                    
                                    <div className="flex flex-wrap gap-2">
                                        {currentUser && (
                                            <button
                                                onClick={() => handleSaveToProfile(job)}
                                                disabled={savingJobs.has(job.id) || job.saved}
                                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                                                    job.saved 
                                                        ? 'bg-green-100 text-green-800 cursor-default'
                                                        : savingJobs.has(job.id)
                                                            ? 'bg-gray-400 text-white cursor-not-allowed'
                                                            : 'bg-purple-600 text-white hover:bg-purple-700'
                                                }`}
                                            >
                                                {savingJobs.has(job.id) ? (
                                                    <span className="flex items-center">
                                                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                                        Saving...
                                                    </span>
                                                ) : job.saved ? (
                                                    "✅ Saved"
                                                ) : (
                                                    "💾 Save to Profile"
                                                )}
                                            </button>
                                        )}
                                        
                                        {job.job_url && (
                                            <a
                                                href={job.job_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                                            >
                                                🔗 View Original Post
                                            </a>
                                        )}
                                        
                                        <button
                                            onClick={() => handleViewDetails(job.id)}
                                            className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
                                        >
                                            📄 View Details
                                        </button>
                                        
                                        <button
                                            onClick={() => handleApplyNow(job)}
                                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center"
                                        >
                                            <span className="mr-1">🚀</span>
                                            Apply Now
                                        </button>
                                    </div>
                                </div>
                            ))}
                            
                            {hasMoreJobs && (
                                <div className="text-center py-6">
                                    <button
                                        onClick={handleLoadMoreJobs}
                                        disabled={moreJobsLoading}
                                        className={`px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 ${
                                            moreJobsLoading
                                                ? "bg-gray-400 cursor-not-allowed"
                                                : "bg-purple-600 hover:bg-purple-700 hover:shadow-lg transform hover:-translate-y-0.5"
                                        }`}
                                    >
                                        {moreJobsLoading ? (
                                            <div className="flex items-center justify-center">
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                                Loading More Jobs...
                                            </div>
                                        ) : (
                                            "🔍 See More Jobs"
                                        )}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {matchedJobs.length === 0 && !uploading && !error && (
                    <div className="text-center p-8 bg-white shadow-lg rounded-lg">
                        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Ready to Find Your Perfect Job?</h2>
                        <p className="text-gray-500">Upload your CV in PDF format and let our AI find the best job matches for you!</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CVUpload;

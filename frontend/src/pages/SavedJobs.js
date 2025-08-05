import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import AuthService from "../api/auth.service";

const SavedJobs = () => {
    const [savedJobs, setSavedJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [deletingJobs, setDeletingJobs] = useState(new Set());

    const currentUser = AuthService.getCurrentUser();

    useEffect(() => {
        if (!currentUser) {
            setError("Please login to view saved jobs");
            setLoading(false);
            return;
        }
        fetchSavedJobs();
    }, [currentUser]);

    const fetchSavedJobs = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/jobs/saved', {
                headers: {
                    'Authorization': `Bearer ${currentUser.accessToken}`
                }
            });

            if (response.ok) {
                const jobs = await response.json();
                setSavedJobs(jobs);
            } else {
                throw new Error('Failed to fetch saved jobs');
            }
        } catch (error) {
            console.error('Error fetching saved jobs:', error);
            setError('Failed to load saved jobs');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteJob = async (jobId) => {
        if (!window.confirm('Are you sure you want to remove this job from your saved list?')) {
            return;
        }

        setDeletingJobs(prev => new Set([...prev, jobId]));

        try {
            const response = await fetch(`http://localhost:8080/api/jobs/${jobId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${currentUser.accessToken}`
                }
            });

            if (response.ok) {
                setSavedJobs(prev => prev.filter(job => job.id !== jobId));
                alert('✅ Job removed from saved list');
            } else {
                throw new Error('Failed to delete job');
            }
        } catch (error) {
            console.error('Error deleting job:', error);
            alert('❌ Failed to remove job');
        } finally {
            setDeletingJobs(prev => {
                const newSet = new Set(prev);
                newSet.delete(jobId);
                return newSet;
            });
        }
    };

    const handleApplyNow = async (job) => {
        try {
            // Mark as applied in backend
            await fetch(`http://localhost:8080/api/jobs/${job.id}/apply`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.accessToken}`
                }
            });

            // Update local state
            setSavedJobs(prev => prev.map(j => 
                j.id === job.id ? { ...j, applied: true, appliedDate: new Date().toISOString() } : j
            ));
        } catch (error) {
            console.error('Error marking as applied:', error);
        }

        // Redirect to job posting
        if (job.applyUrl && job.applyUrl !== job.jobUrl) {
            window.open(job.applyUrl, '_blank');
        } else if (job.jobUrl) {
            window.open(job.jobUrl, '_blank');
        } else {
            alert('❌ No application link available for this job');
        }
    };

    const getScoreColor = (score) => {
        if (score >= 70) return "text-green-600";
        if (score >= 50) return "text-yellow-600";
        return "text-red-600";
    };

    const getScoreLabel = (score) => {
        if (score >= 70) return "Excellent Match";
        if (score >= 50) return "Good Match";
        if (score >= 30) return "Fair Match";
        return "Poor Match";
    };

    if (!currentUser) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-2xl mx-auto text-center">
                    <h1 className="text-3xl font-bold text-gray-800 mb-4">Saved Jobs</h1>
                    <div className="bg-white shadow-lg rounded-lg p-8">
                        <p className="text-gray-600 mb-4">Please login to view your saved jobs</p>
                        <Link
                            to="/login"
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                        >
                            Login
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-4xl mx-auto">
                    <h1 className="text-3xl font-bold text-gray-800 mb-8">My Saved Jobs</h1>
                    <div className="bg-white shadow-lg rounded-lg p-8 text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                        <p className="text-gray-600">Loading your saved jobs...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">My Saved Jobs</h1>
                    <Link
                        to="/cv-upload"
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                    >
                        🔍 Find More Jobs
                    </Link>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {savedJobs.length === 0 ? (
                    <div className="bg-white shadow-lg rounded-lg p-8 text-center">
                        <h2 className="text-xl font-semibold text-gray-700 mb-4">No Saved Jobs Yet</h2>
                        <p className="text-gray-500 mb-6">
                            Start by uploading your CV to find and save job matches!
                        </p>
                        <Link
                            to="/cv-upload"
                            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                        >
                            Upload CV & Find Jobs
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {savedJobs.map((job) => (
                            <div
                                key={job.id}
                                className="bg-white shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                                        <p className="text-lg text-gray-700">{job.company}</p>
                                        <p className="text-md text-gray-500">{job.location}</p>
                                        <div className="flex items-center mt-2 space-x-4">
                                            <span className="text-sm text-gray-400">Source: {job.source}</span>
                                            <span className="text-sm text-gray-400">
                                                Saved: {new Date(job.savedDate).toLocaleDateString()}
                                            </span>
                                            {job.applied && (
                                                <span className="text-sm text-green-600 font-medium">
                                                    ✅ Applied on {new Date(job.appliedDate).toLocaleDateString()}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        {job.similarityScore && (
                                            <>
                                                <div className={`text-lg font-bold ${getScoreColor(job.similarityScore)}`}>
                                                    {job.similarityScore.toFixed(1)}%
                                                </div>
                                                <div className={`text-sm ${getScoreColor(job.similarityScore)}`}>
                                                    {getScoreLabel(job.similarityScore)}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                </div>
                                
                                <p className="text-gray-600 mb-4">{job.description}</p>
                                
                                {job.requirements && (
                                    <div className="mb-4">
                                        <h4 className="font-medium text-gray-900 mb-2">Requirements:</h4>
                                        <p className="text-sm text-gray-600">{job.requirements}</p>
                                    </div>
                                )}
                                
                                <div className="flex flex-wrap gap-2">
                                    {job.jobUrl && (
                                        <a
                                            href={job.jobUrl}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                                        >
                                            🔗 View Original Post
                                        </a>
                                    )}
                                    
                                    {!job.applied ? (
                                        <button
                                            onClick={() => handleApplyNow(job)}
                                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                                        >
                                            🚀 Apply Now
                                        </button>
                                    ) : (
                                        <span className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
                                            ✅ Applied
                                        </span>
                                    )}
                                    
                                    <button
                                        onClick={() => handleDeleteJob(job.id)}
                                        disabled={deletingJobs.has(job.id)}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                                            deletingJobs.has(job.id)
                                                ? 'bg-gray-400 text-white cursor-not-allowed'
                                                : 'bg-red-600 text-white hover:bg-red-700'
                                        }`}
                                    >
                                        {deletingJobs.has(job.id) ? (
                                            <span className="flex items-center">
                                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                                Removing...
                                            </span>
                                        ) : (
                                            "🗑️ Remove"
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SavedJobs;

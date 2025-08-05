import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import jobService from "../api/job.service";

const JobDetails = () => {
    const { id } = useParams();
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        jobService.getJobById(id).then(
            (response) => {
                setJob(response.data);
                setLoading(false);
            },
            (error) => {
                console.log(error);
                setLoading(false);
            }
        );
    }, [id]);

    if (loading) {
        return <p className="text-center text-gray-500 mt-10">Loading job details...</p>;
    }

    if (!job) {
        return (
            <div className="text-center p-8 bg-white shadow-lg rounded-lg mt-10">
                <h2 className="text-2xl font-semibold text-gray-700">Job Not Found</h2>
                <p className="text-gray-500 mt-2">The job you are looking for does not exist.</p>
                <Link to="/" className="mt-4 inline-block bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-blue-600 transition-colors">
                    Back to Listings
                </Link>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="bg-white shadow-2xl rounded-xl p-8">
                <h1 className="text-4xl font-extrabold text-gray-900">{job.title}</h1>
                <p className="text-2xl text-gray-700 mt-2">{job.company}</p>
                <p className="text-xl text-gray-500 mt-1 mb-6">{job.location}</p>
                
                <div className="prose max-w-none text-gray-800">
                    <p>{job.description}</p>
                </div>

                <div className="mt-8">
                    <h3 className="text-2xl font-bold text-gray-800">Skills</h3>
                    <div className="flex flex-wrap gap-2 mt-4">
                        {job.skills && job.skills.map((skill, index) => (
                            <span key={index} className="bg-gray-200 text-gray-800 px-3 py-1 rounded-full text-sm font-semibold">
                                {skill}
                            </span>
                        ))}
                    </div>
                </div>

                <div className="mt-8">
                    <Link to="/" className="text-blue-500 hover:underline">
                        &larr; Back to all jobs
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default JobDetails;

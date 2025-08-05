import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import jobService from "../api/job.service";

const Home = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        jobService.getAllJobs().then(
            (response) => {
                setJobs(response.data);
                setLoading(false);
            },
            (error) => {
                console.log(error);
                setLoading(false);
            }
        );
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-4xl font-extrabold text-center mb-10 text-gray-800">Job Listings</h1>

            {loading && <p className="text-center text-gray-500">Loading jobs...</p>}

            {!loading && jobs.length === 0 && (
                <div className="text-center p-8 bg-white shadow-lg rounded-lg">
                    <h2 className="text-2xl font-semibold text-gray-700">No Jobs Found</h2>
                    <p className="text-gray-500 mt-2">There are currently no open positions. Please check back later!</p>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {jobs.map((job) => (
                    <Link to={`/jobs/${job.id}`} key={job.id} className="block">
                        <div className="bg-white shadow-lg rounded-xl p-6 hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 ease-in-out">
                            <h2 className="text-2xl font-bold text-gray-900">{job.title}</h2>
                            <p className="text-lg text-gray-700 mt-2">{job.company}</p>
                            <p className="text-md text-gray-500 mt-1">{job.location}</p>
                            <p className="mt-4 text-gray-600 truncate">{job.description}</p>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default Home;

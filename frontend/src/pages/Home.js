import React, { useState, useEffect } from "react";
import jobService from "../api/job.service";

const Home = () => {
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        jobService.getAllJobs().then(
            (response) => {
                setJobs(response.data);
            },
            (error) => {
                console.log(error);
            }
        );
    }, []);

    return (
        <div className="container mx-auto">
            <h1 className="text-3xl font-bold text-center my-8">Job Listings</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {jobs.map((job) => (
                    <div key={job.id} className="bg-white shadow-md rounded-lg p-6">
                        <h2 className="text-xl font-bold">{job.title}</h2>
                        <p className="text-gray-700">{job.company}</p>
                        <p className="text-gray-500">{job.location}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Home;

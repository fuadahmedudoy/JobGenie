import axios from 'axios';
import authHeader from './auth-header';

const API_URL = 'http://localhost:8080/api/jobs/';

const getAllJobs = () => {
  return axios.get(API_URL);
};

const getJobById = (id) => {
    return axios.get(API_URL + id);
};

const saveJob = (jobData) => {
    return axios.post(API_URL + 'save', jobData, { headers: authHeader() });
};

const getSavedJobs = () => {
    return axios.get(API_URL + 'saved', { headers: authHeader() });
};

const deleteJob = (jobId) => {
    return axios.delete(API_URL + 'saved/' + jobId, { headers: authHeader() });
};

const markAsApplied = (jobId) => {
    return axios.put(API_URL + 'saved/' + jobId + '/apply', {}, { headers: authHeader() });
};

const jobService = {
    getAllJobs,
    getJobById,
    saveJob,
    getSavedJobs,
    deleteJob,
    markAsApplied,
};

export default jobService;

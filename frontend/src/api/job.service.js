import axios from 'axios';
import authHeader from './auth-header';

const API_URL = 'http://localhost:8080/api/jobs/';

const getAllJobs = () => {
  return axios.get(API_URL, { headers: authHeader() });
};


const jobService = {
    getAllJobs,
};

export default jobService;

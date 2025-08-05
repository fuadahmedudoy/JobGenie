package com.jobrecommender.controller;

import com.jobrecommender.model.Job;
import com.jobrecommender.model.User;
import com.jobrecommender.repository.JobRepository;
import com.jobrecommender.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Map;

@RestController
@RequestMapping("/api/jobs")
@CrossOrigin(origins = "http://localhost:3000")
public class JobController {

    @Autowired
    private JobRepository jobRepository;
    
    @Autowired
    private UserRepository userRepository;

    @GetMapping
    public List<Job> getAllJobs() {
        return jobRepository.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Job> getJobById(@PathVariable Long id) {
        Optional<Job> job = jobRepository.findById(id);
        if (job.isPresent()) {
            return ResponseEntity.ok(job.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    @PostMapping("/save")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<?> saveJob(@RequestBody Map<String, Object> jobData) {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String username = auth.getName();
            
            Optional<User> userOpt = userRepository.findByUsername(username);
            if (!userOpt.isPresent()) {
                return ResponseEntity.badRequest().body("User not found");
            }
            
            User user = userOpt.get();
            
            // Check if job already exists by external ID
            String externalId = (String) jobData.get("id");
            Optional<Job> existingJob = jobRepository.findByExternalIdAndSavedByUser(externalId, user);
            
            if (existingJob.isPresent()) {
                return ResponseEntity.ok().body(Map.of("message", "Job already saved", "jobId", existingJob.get().getId()));
            }
            
            // Create new job entry
            Job job = new Job();
            job.setExternalId(externalId);
            job.setTitle((String) jobData.get("title"));
            job.setDescription((String) jobData.get("description"));
            job.setCompany((String) jobData.get("company"));
            job.setLocation((String) jobData.get("location"));
            job.setSource((String) jobData.get("source"));
            job.setJobUrl((String) jobData.get("job_url"));
            job.setApplyUrl((String) jobData.get("apply_url"));
            job.setRequirements((String) jobData.get("requirements"));
            
            // Handle similarity score
            Object similarityObj = jobData.get("similarity_score");
            if (similarityObj != null) {
                if (similarityObj instanceof Number) {
                    job.setSimilarityScore(((Number) similarityObj).doubleValue());
                } else if (similarityObj instanceof String) {
                    try {
                        job.setSimilarityScore(Double.parseDouble((String) similarityObj));
                    } catch (NumberFormatException e) {
                        job.setSimilarityScore(0.0);
                    }
                }
            }
            
            job.setSavedByUser(user);
            job.setSavedDate(LocalDateTime.now());
            job.setTimestamp(LocalDateTime.now());
            
            Job savedJob = jobRepository.save(job);
            
            return ResponseEntity.ok().body(Map.of(
                "message", "Job saved successfully", 
                "jobId", savedJob.getId(),
                "externalId", savedJob.getExternalId()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Failed to save job: " + e.getMessage()));
        }
    }
    
    @GetMapping("/saved")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<List<Job>> getSavedJobs() {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String username = auth.getName();
            
            Optional<User> userOpt = userRepository.findByUsername(username);
            if (!userOpt.isPresent()) {
                return ResponseEntity.badRequest().build();
            }
            
            List<Job> savedJobs = jobRepository.findBySavedByUserOrderBySavedDateDesc(userOpt.get());
            return ResponseEntity.ok(savedJobs);
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    @PutMapping("/saved/{id}/apply")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<?> markAsApplied(@PathVariable Long id) {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String username = auth.getName();
            
            Optional<User> userOpt = userRepository.findByUsername(username);
            Optional<Job> jobOpt = jobRepository.findById(id);
            
            if (!userOpt.isPresent() || !jobOpt.isPresent()) {
                return ResponseEntity.badRequest().body(Map.of("error", "User or job not found"));
            }
            
            Job job = jobOpt.get();
            job.setApplied(true);
            job.setAppliedDate(LocalDateTime.now());
            
            jobRepository.save(job);
            
            return ResponseEntity.ok().body(Map.of(
                "message", "Job marked as applied",
                "applyUrl", job.getApplyUrl()
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Failed to mark as applied: " + e.getMessage()));
        }
    }
    
    @DeleteMapping("/saved/{id}")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<?> deleteSavedJob(@PathVariable Long id) {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String username = auth.getName();
            
            Optional<User> userOpt = userRepository.findByUsername(username);
            Optional<Job> jobOpt = jobRepository.findById(id);
            
            if (!userOpt.isPresent() || !jobOpt.isPresent()) {
                return ResponseEntity.badRequest().body(Map.of("error", "User or job not found"));
            }
            
            Job job = jobOpt.get();
            
            // Check if user owns this saved job
            if (!job.getSavedByUser().getId().equals(userOpt.get().getId())) {
                return ResponseEntity.badRequest().body(Map.of("error", "Unauthorized"));
            }
            
            jobRepository.delete(job);
            
            return ResponseEntity.ok().body(Map.of("message", "Job removed from saved list"));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Failed to delete job: " + e.getMessage()));
        }
    }
}

package com.jobrecommender.repository;

import com.jobrecommender.model.Job;
import com.jobrecommender.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface JobRepository extends JpaRepository<Job, Long> {
    
    // Find saved jobs by user
    List<Job> findBySavedByUserOrderBySavedDateDesc(User user);
    
    // Find job by external ID and user (to prevent duplicates)
    Optional<Job> findByExternalIdAndSavedByUser(String externalId, User user);
    
    // Find jobs by source
    List<Job> findBySource(String source);
    
    // Find applied jobs by user
    List<Job> findBySavedByUserAndAppliedTrueOrderByAppliedDateDesc(User user);
}

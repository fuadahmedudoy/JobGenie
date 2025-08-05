package com.jobrecommender.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Getter;
import lombok.Setter;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "jobs")
@Getter
@Setter
public class Job {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    private String company;
    private String location;
    private LocalDateTime timestamp;
    
    // New fields for scraped jobs
    private String externalId; // e.g., "bdjobs_1", "linkedin_2"
    private String source; // e.g., "BDJobs", "LinkedIn", "Indeed"
    private String jobUrl; // Direct link to the job posting
    private String applyUrl; // Direct application link
    private String requirements;
    private Double similarityScore;
    private String keywords; // Keywords used to find this job
    
    // User interaction fields
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private User savedByUser; // User who saved this job
    
    private Boolean applied = false; // Whether user applied to this job
    private LocalDateTime appliedDate;
    private LocalDateTime savedDate;
}
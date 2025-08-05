package com.jobrecommender.config;

import com.jobrecommender.model.ERole;
import com.jobrecommender.model.Job;
import com.jobrecommender.model.Role;
import com.jobrecommender.repository.JobRepository;
import com.jobrecommender.repository.RoleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private JobRepository jobRepository;

    @Override
    public void run(String... args) throws Exception {
        // Initialize roles if they don't exist
        if (roleRepository.findByName(ERole.ROLE_USER).isEmpty()) {
            Role userRole = new Role(ERole.ROLE_USER);
            roleRepository.save(userRole);
            System.out.println("Created ROLE_USER");
        }

        if (roleRepository.findByName(ERole.ROLE_ADMIN).isEmpty()) {
            Role adminRole = new Role(ERole.ROLE_ADMIN);
            roleRepository.save(adminRole);
            System.out.println("Created ROLE_ADMIN");
        }

        // Initialize sample jobs if none exist
        if (jobRepository.count() == 0) {
            Job job1 = new Job();
            job1.setTitle("Java Developer");
            job1.setCompany("Tech Corp");
            job1.setLocation("New York, NY");
            job1.setDescription("We are looking for an experienced Java developer to join our team. You will be responsible for developing and maintaining our enterprise applications using Spring Boot, Hibernate, and other modern Java technologies.");
            job1.setTimestamp(LocalDateTime.now());
            jobRepository.save(job1);

            Job job2 = new Job();
            job2.setTitle("Frontend React Developer");
            job2.setCompany("StartupXYZ");
            job2.setLocation("San Francisco, CA");
            job2.setDescription("Join our dynamic team as a Frontend Developer. You'll work with React, TypeScript, and modern CSS frameworks to create beautiful and responsive user interfaces for our web applications.");
            job2.setTimestamp(LocalDateTime.now());
            jobRepository.save(job2);

            Job job3 = new Job();
            job3.setTitle("Full Stack Engineer");
            job3.setCompany("Innovation Labs");
            job3.setLocation("Austin, TX");
            job3.setDescription("We're seeking a talented Full Stack Engineer to work on both frontend and backend systems. Experience with Node.js, React, PostgreSQL, and cloud platforms is preferred.");
            job3.setTimestamp(LocalDateTime.now());
            jobRepository.save(job3);

            System.out.println("Created sample jobs");
        }
    }
}

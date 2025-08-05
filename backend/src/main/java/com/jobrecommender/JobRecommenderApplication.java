package com.jobrecommender;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class JobRecommenderApplication {

	public static void main(String[] args) {
		SpringApplication.run(JobRecommenderApplication.class, args);
	}

}

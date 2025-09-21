import { JobSearchResponse, JobMatch, JobFilters } from '@/types/job';

export interface JobSearchRequest {
  salary_min: number;
  salary_max: number;
  seniority: string;
  job_type: string[];
  job_titles: string[];
  skills: string[];
  education_level: string;
}

export class JobService {
  private static readonly BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  static async findJobs(searchData: JobSearchRequest): Promise<JobSearchResponse> {
    // Store search criteria in localStorage for use in individual job pages
    if (typeof window !== 'undefined') {
      localStorage.setItem('lastSearchCriteria', JSON.stringify(searchData));
    }

    const response = await fetch(`${this.BASE_URL}/api/users/find_jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Job search failed: ${response.statusText}`);
    }

    return await response.json();
  }

  static async getJobs(filters?: JobFilters, page: number = 1, limit: number = 10): Promise<JobSearchResponse> {
    // Try to use stored search criteria first, fallback to defaults if none exist
    console.log('📋 getJobs called with filters:', filters);
    const storedCriteria = this.getStoredSearchCriteria();
    console.log('📋 getJobs found stored criteria:', storedCriteria);
    
    if (storedCriteria) {
      // Use stored criteria without overwriting localStorage
      const response = await fetch(`${this.BASE_URL}/api/users/find_jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storedCriteria),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Job search failed: ${response.statusText}`);
      }

      return await response.json();
    }
    
    // Fallback to default search if no stored criteria (but don't store these defaults)
    const searchData: JobSearchRequest = {
      salary_min: filters?.salaryMin || 0,
      salary_max: filters?.salaryMax || 1000000,
      seniority: 'Junior', // Default values
      job_type: filters?.jobType || [],
      job_titles: filters?.jobTitles || [],
      skills: filters?.skills || [],
      education_level: 'high school'
    };

    // Call API directly without storing defaults in localStorage
    const response = await fetch(`${this.BASE_URL}/api/users/find_jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Job search failed: ${response.statusText}`);
    }

    return await response.json();
  }

  static getStoredSearchCriteria(): JobSearchRequest | null {
    if (typeof window === 'undefined') return null;
    
    try {
      const stored = localStorage.getItem('lastSearchCriteria');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  static async getJobById(id: number): Promise<JobMatch | null> {
    try {
      // Try to get stored search criteria to calculate proper scores
      const searchCriteria = this.getStoredSearchCriteria();
      
      if (searchCriteria) {
        // If we have search criteria, use the search endpoint to get the job with proper scoring
        const searchResponse = await this.findJobs(searchCriteria);
        const jobWithScores = searchResponse.jobs.find(job => job.id === id);
        if (jobWithScores) {
          return jobWithScores;
        }
      }
      
      // Fallback to the direct endpoint (will have 0 scores)
      const response = await fetch(`${this.BASE_URL}/api/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 404) {
        return null; // Job not found
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch job: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching job by ID:', error);
      throw error;
    }
  }
}

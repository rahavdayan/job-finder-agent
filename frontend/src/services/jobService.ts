export interface JobSearchRequest {
  salaryMin: number;
  salaryMax: number;
  seniority: string;
  jobType: string[];
  jobTitles: string[];
  skills: string[];
  educationLevel: string;
}

export interface JobSearchResponse {
  message: string;
  jobs: any[]; // Will be defined later when we know the job structure
}

export class JobService {
  private static readonly BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  static async findJobs(searchData: JobSearchRequest): Promise<JobSearchResponse> {
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
}

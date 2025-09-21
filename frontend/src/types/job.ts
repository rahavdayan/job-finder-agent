export interface JobMatch {
  // Job data from JOB_PAGES_PARSED
  id: number;
  job_title: string | null;
  employer: string | null;
  location: string | null;
  date_posted: string | null;
  primary_salary_min: number | null;
  primary_salary_max: number | null;
  primary_salary_rate: string | null;
  secondary_salary_min: number | null;
  secondary_salary_max: number | null;
  secondary_salary_rate: string | null;
  job_type: string | null;
  skills: string | null;
  description: string | null;
  seniority: string | null;
  education_level: string | null;
  normalized_salary_min: number | null;
  normalized_salary_max: number | null;
  
  // URL from JOB_PAGES_RAW
  url: string;
  
  // Calculated score
  score: number;
  
  // Score breakdown for transparency
  job_type_score: number;
  title_score: number;
  skills_score: number;
  salary_score: number;
}

export interface JobSearchResponse {
  jobs: JobMatch[];
  total_count: number;
}

export interface JobFilters {
  salaryMin?: number;
  salaryMax?: number;
  salaryPeriod?: 'hourly' | 'weekly' | 'monthly' | 'yearly';
  jobType?: string[];
  jobTitles?: string[];
  skills?: string[];
}

export interface PaginationInfo {
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  totalItems: number;
}

export type SalaryPeriod = 'hourly' | 'weekly' | 'monthly' | 'yearly';

export const SALARY_PERIODS: { value: SalaryPeriod; label: string }[] = [
  { value: 'hourly', label: 'Per Hour' },
  { value: 'weekly', label: 'Per Week' },
  { value: 'monthly', label: 'Per Month' },
  { value: 'yearly', label: 'Per Year' },
];

export const JOB_TYPES = [
  'Full-time',
  'Part-time',
  'Contract',
  'Freelance',
  'Remote',
  'Hybrid',
  'On-site',
];

// Helper function to format salary display
export const formatSalary = (
  min: number | null,
  max: number | null,
  rate: string | null
): string => {
  if (!min && !max) return 'Salary not specified';
  
  const formatAmount = (amount: number) => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`;
    } else {
      return `$${amount.toLocaleString()}`;
    }
  };

  const rateText = rate ? ` ${rate}` : '';
  
  if (min && max) {
    return `${formatAmount(min)} - ${formatAmount(max)}${rateText}`;
  } else if (min) {
    return `${formatAmount(min)}+${rateText}`;
  } else if (max) {
    return `Up to ${formatAmount(max)}${rateText}`;
  }
  
  return 'Salary not specified';
};

// Helper function to format skills array
export const formatSkills = (skillsString: string | null): string[] => {
  if (!skillsString) return [];
  return skillsString.split(',').map(skill => skill.trim()).filter(skill => skill.length > 0);
};

// Helper function to truncate description
export const truncateDescription = (description: string | null, maxLength: number = 150): string => {
  if (!description) return 'No description available';
  if (description.length <= maxLength) return description;
  return description.substring(0, maxLength).trim() + '...';
};

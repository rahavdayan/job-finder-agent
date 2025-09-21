'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { JobCard } from '@/components/JobCard';
import { JobFiltersComponent } from '@/components/JobFilters';
import { Pagination } from '@/components/Pagination';
import { JobService } from '@/services/jobService';
import { JobMatch, JobFilters, PaginationInfo } from '@/types/job';

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<JobFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Load jobs on component mount
  useEffect(() => {
    loadJobs();
  }, []);

  // Apply filters when filters change
  useEffect(() => {
    applyFilters();
  }, [jobs, filters]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await JobService.getJobs();
      setJobs(response.jobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...jobs];

    // Apply salary filter
    if (filters.salaryMin || filters.salaryMax) {
      filtered = filtered.filter(job => {
        const jobSalary = job.normalized_salary_min || job.primary_salary_min;
        if (!jobSalary) return true; // Include jobs without salary info
        
        if (filters.salaryMin && jobSalary < filters.salaryMin) return false;
        if (filters.salaryMax && jobSalary > filters.salaryMax) return false;
        
        return true;
      });
    }

    // Apply job type filter
    if (filters.jobType && filters.jobType.length > 0) {
      filtered = filtered.filter(job => {
        if (!job.job_type) return false;
        return filters.jobType!.some(type => 
          job.job_type!.toLowerCase().includes(type.toLowerCase())
        );
      });
    }

    // Apply job titles filter
    if (filters.jobTitles && filters.jobTitles.length > 0) {
      filtered = filtered.filter(job => {
        if (!job.job_title) return false;
        return filters.jobTitles!.some(title =>
          job.job_title!.toLowerCase().includes(title.toLowerCase())
        );
      });
    }

    // Apply skills filter
    if (filters.skills && filters.skills.length > 0) {
      filtered = filtered.filter(job => {
        if (!job.skills) return false;
        const jobSkills = job.skills.toLowerCase();
        return filters.skills!.some(skill =>
          jobSkills.includes(skill.toLowerCase())
        );
      });
    }

    setFilteredJobs(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleFiltersChange = (newFilters: JobFilters) => {
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    applyFilters();
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const handleJobClick = (job: JobMatch) => {
    router.push(`/jobs/${job.id}`);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Calculate pagination
  const totalItems = filteredJobs.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentJobs = filteredJobs.slice(startIndex, endIndex);

  const pagination: PaginationInfo = {
    currentPage,
    totalPages,
    itemsPerPage,
    totalItems,
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Jobs</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadJobs}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Job Search Results
          </h1>
          <p className="text-gray-600">
            Found {totalItems} job{totalItems !== 1 ? 's' : ''} matching your criteria
          </p>
        </div>

        {/* Filters */}
        <JobFiltersComponent
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onApplyFilters={handleApplyFilters}
          onClearFilters={handleClearFilters}
        />

        {/* Results */}
        {filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or search criteria
            </p>
            <button
              onClick={handleClearFilters}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <>
            {/* Job Cards */}
            <div className="space-y-4 mb-8">
              {currentJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onClick={handleJobClick}
                />
              ))}
            </div>

            {/* Pagination */}
            <Pagination
              pagination={pagination}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>
    </div>
  );
}

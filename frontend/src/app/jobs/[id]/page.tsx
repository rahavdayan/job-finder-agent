'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { JobService } from '@/services/jobService';
import { JobMatch, formatSalary, formatSkills } from '@/types/job';

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const [job, setJob] = useState<JobMatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.id) {
      loadJob(parseInt(params.id as string));
    }
  }, [params.id]);

  const loadJob = async (jobId: number) => {
    try {
      setLoading(true);
      setError(null);
      const jobData = await JobService.getJobById(jobId);
      if (jobData) {
        setJob(jobData);
      } else {
        setError('Job not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load job details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Date not specified';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const handleBackClick = () => {
    router.back();
  };

  const handleApplyClick = () => {
    if (job?.url) {
      window.open(job.url, '_blank', 'noopener,noreferrer');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Job Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The requested job could not be found.'}</p>
          <button
            onClick={handleBackClick}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const skills = formatSkills(job.skills);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={handleBackClick}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Jobs
        </button>

        {/* Job Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {job.job_title || 'Job Title Not Specified'}
              </h1>
              <p className="text-xl text-gray-600 font-medium mb-4">
                {job.employer || 'Company Not Specified'}
              </p>
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {job.location || 'Location not specified'}
                </div>
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a1 1 0 011-1h6a1 1 0 011 1v4h3a1 1 0 011 1v9a1 1 0 01-1 1H5a1 1 0 01-1-1V8a1 1 0 011-1h3z" />
                  </svg>
                  Posted: {formatDate(job.date_posted)}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-lg font-semibold mb-4">
                Match Score: {(job.score * 100).toFixed(0)}%
              </div>
              <button
                onClick={handleApplyClick}
                className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 font-medium"
              >
                Apply Now
              </button>
            </div>
          </div>

          {/* Salary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Salary</h3>
            <p className="text-2xl font-bold text-green-600">
              {formatSalary(
                job.normalized_salary_min || job.primary_salary_min,
                job.normalized_salary_max || job.primary_salary_max,
                job.primary_salary_rate
              )}
            </p>
          </div>

          {/* Job Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {job.job_type && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Job Type</h3>
                <span className="bg-gray-100 text-gray-700 px-3 py-2 rounded-md">
                  {job.job_type}
                </span>
              </div>
            )}
            
            {job.seniority && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Seniority Level</h3>
                <span className="bg-blue-100 text-blue-700 px-3 py-2 rounded-md">
                  {job.seniority}
                </span>
              </div>
            )}
            
            {job.education_level && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Education Level</h3>
                <span className="bg-purple-100 text-purple-700 px-3 py-2 rounded-md">
                  {job.education_level}
                </span>
              </div>
            )}
          </div>

          {/* Skills */}
          {skills.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-blue-50 text-blue-700 px-3 py-2 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Score Breakdown */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Match Score Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {(job.job_type_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Job Type</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {(job.title_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Title Match</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {(job.skills_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Skills Match</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {(job.salary_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Salary Score</div>
              </div>
            </div>
          </div>
        </div>

        {/* Job Description */}
        {job.description && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Job Description</h2>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {job.description}
              </div>
            </div>
          </div>
        )}

        {/* Additional Salary Information */}
        {(job.secondary_salary_min || job.secondary_salary_max) && (
          <div className="bg-white rounded-lg shadow-md p-8 mt-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Additional Salary Information</h2>
            <p className="text-lg text-gray-700">
              Secondary Range: {formatSalary(
                job.secondary_salary_min,
                job.secondary_salary_max,
                job.secondary_salary_rate
              )}
            </p>
          </div>
        )}

        {/* Apply Button (Bottom) */}
        <div className="text-center mt-8">
          <button
            onClick={handleApplyClick}
            className="bg-green-600 text-white px-8 py-4 rounded-lg hover:bg-green-700 font-medium text-lg"
          >
            Apply for This Position
          </button>
          <p className="text-sm text-gray-600 mt-2">
            You will be redirected to the original job posting
          </p>
        </div>
      </div>
    </div>
  );
}

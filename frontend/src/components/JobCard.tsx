import React from 'react';
import { JobMatch, formatSalary, formatSkills, truncateDescription } from '@/types/job';

interface JobCardProps {
  job: JobMatch;
  onClick: (job: JobMatch) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onClick }) => {
  const handleClick = () => {
    onClick(job);
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Date not specified';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const skills = formatSkills(job.skills);
  const displaySkills = skills.slice(0, 5); // Show max 5 skills
  const remainingSkills = skills.length - displaySkills.length;

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 cursor-pointer border border-gray-200 hover:border-blue-300"
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-1">
            {job.job_title || 'Job Title Not Specified'}
          </h3>
          <p className="text-gray-600 font-medium">
            {job.employer || 'Company Not Specified'}
          </p>
        </div>
        <div className="text-right">
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
            Score: {(job.score * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Location and Date */}
      <div className="flex justify-between items-center mb-3 text-sm text-gray-600">
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
          {formatDate(job.date_posted)}
        </div>
      </div>

      {/* Salary */}
      <div className="mb-3">
        <span className="text-lg font-semibold text-green-600">
          {formatSalary(
            job.normalized_salary_min || job.primary_salary_min,
            job.normalized_salary_max || job.primary_salary_max,
            job.primary_salary_rate
          )}
        </span>
      </div>

      {/* Job Type */}
      {job.job_type && (
        <div className="mb-3">
          <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
            {job.job_type}
          </span>
        </div>
      )}

      {/* Skills */}
      {displaySkills.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {displaySkills.map((skill, index) => (
              <span
                key={index}
                className="bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs"
              >
                {skill}
              </span>
            ))}
            {remainingSkills > 0 && (
              <span className="bg-gray-50 text-gray-600 px-2 py-1 rounded-full text-xs">
                +{remainingSkills} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Description Preview */}
      <div className="text-gray-700 text-sm leading-relaxed">
        {truncateDescription(job.description)}
      </div>

      {/* Footer with additional info */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex justify-between items-center text-xs text-gray-500">
        <div className="flex space-x-4">
          {job.seniority && (
            <span>Level: {job.seniority}</span>
          )}
          {job.education_level && (
            <span>Education: {job.education_level}</span>
          )}
        </div>
        <div className="text-blue-600 hover:text-blue-800">
          View Details →
        </div>
      </div>
    </div>
  );
};

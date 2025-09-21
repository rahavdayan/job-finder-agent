import React, { useState } from 'react';
import { JobFilters, SALARY_PERIODS, JOB_TYPES, SalaryPeriod } from '@/types/job';

interface JobFiltersProps {
  filters: JobFilters;
  onFiltersChange: (filters: JobFilters) => void;
  onApplyFilters: () => void;
  onClearFilters: () => void;
}

export const JobFiltersComponent: React.FC<JobFiltersProps> = ({
  filters,
  onFiltersChange,
  onApplyFilters,
  onClearFilters,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState<JobFilters>(filters);

  const handleInputChange = (field: keyof JobFilters, value: any) => {
    const updatedFilters = { ...localFilters, [field]: value };
    setLocalFilters(updatedFilters);
    onFiltersChange(updatedFilters);
  };

  const handleJobTypeToggle = (jobType: string) => {
    const currentTypes = localFilters.jobType || [];
    const updatedTypes = currentTypes.includes(jobType)
      ? currentTypes.filter(type => type !== jobType)
      : [...currentTypes, jobType];
    
    handleInputChange('jobType', updatedTypes);
  };

  const handleSkillsChange = (skillsString: string) => {
    const skills = skillsString
      .split(',')
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0);
    handleInputChange('skills', skills);
  };

  const handleJobTitlesChange = (titlesString: string) => {
    const titles = titlesString
      .split(',')
      .map(title => title.trim())
      .filter(title => title.length > 0);
    handleInputChange('jobTitles', titles);
  };

  const handleApply = () => {
    onApplyFilters();
    setIsExpanded(false);
  };

  const handleClear = () => {
    const clearedFilters: JobFilters = {};
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
    onClearFilters();
  };

  const hasActiveFilters = Object.keys(localFilters).some(key => {
    const value = localFilters[key as keyof JobFilters];
    return value !== undefined && value !== null && 
           (Array.isArray(value) ? value.length > 0 : true);
  });

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 mb-6">
      {/* Filter Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
            {hasActiveFilters && (
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                Active
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleClear}
              className="text-gray-500 hover:text-gray-700 text-sm"
              disabled={!hasActiveFilters}
            >
              Clear All
            </button>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-blue-600 hover:text-blue-800 flex items-center"
            >
              {isExpanded ? 'Hide Filters' : 'Show Filters'}
              <svg
                className={`w-4 h-4 ml-1 transform transition-transform ${
                  isExpanded ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="p-4 space-y-6">
          {/* Salary Range */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Salary
              </label>
              <input
                type="number"
                value={localFilters.salaryMin || ''}
                onChange={(e) => handleInputChange('salaryMin', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="e.g., 50000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Salary
              </label>
              <input
                type="number"
                value={localFilters.salaryMax || ''}
                onChange={(e) => handleInputChange('salaryMax', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="e.g., 100000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Salary Period
              </label>
              <select
                value={localFilters.salaryPeriod || 'yearly'}
                onChange={(e) => handleInputChange('salaryPeriod', e.target.value as SalaryPeriod)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {SALARY_PERIODS.map(period => (
                  <option key={period.value} value={period.value}>
                    {period.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Job Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Types
            </label>
            <div className="flex flex-wrap gap-2">
              {JOB_TYPES.map(jobType => (
                <button
                  key={jobType}
                  onClick={() => handleJobTypeToggle(jobType)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    (localFilters.jobType || []).includes(jobType)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {jobType}
                </button>
              ))}
            </div>
          </div>

          {/* Job Titles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Titles
            </label>
            <input
              type="text"
              value={(localFilters.jobTitles || []).join(', ')}
              onChange={(e) => handleJobTitlesChange(e.target.value)}
              placeholder="e.g., Software Engineer, Developer, Frontend"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Separate multiple titles with commas
            </p>
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Skills
            </label>
            <input
              type="text"
              value={(localFilters.skills || []).join(', ')}
              onChange={(e) => handleSkillsChange(e.target.value)}
              placeholder="e.g., React, Python, JavaScript, AWS"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Separate multiple skills with commas
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleClear}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
              disabled={!hasActiveFilters}
            >
              Clear
            </button>
            <button
              onClick={handleApply}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { JobService, JobSearchRequest } from '../../services/jobService';

interface FormData {
  salaryMin: string;
  salaryMax: string;
  salaryPeriod: 'hourly' | 'weekly' | 'monthly' | 'yearly';
  seniority: string;
  jobType: string[];
  jobTitles: string[];
  skills: string[];
  educationLevel: string;
}

interface TagInputProps {
  label: string;
  tags: string[];
  onAddTag: (tag: string) => void;
  onRemoveTag: (index: number) => void;
  placeholder: string;
}

const TagInput: React.FC<TagInputProps> = ({ label, tags, onAddTag, onRemoveTag, placeholder }) => {
  const [inputValue, setInputValue] = useState('');

  const handleAdd = () => {
    if (inputValue.trim() && !tags.includes(inputValue.trim())) {
      onAddTag(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="button"
          onClick={handleAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Add
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag, index) => (
          <span
            key={index}
            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
          >
            {tag}
            <button
              type="button"
              onClick={() => onRemoveTag(index)}
              className="ml-2 text-blue-600 hover:text-blue-800"
            >
              ×
            </button>
          </span>
        ))}
      </div>
    </div>
  );
};

export default function ManualEntryPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState<FormData>({
    salaryMin: '',
    salaryMax: '',
    salaryPeriod: 'yearly',
    seniority: '',
    jobType: [],
    jobTitles: [],
    skills: [],
    educationLevel: '',
  });

  // Pre-fill data from localStorage if available (from resume upload)
  useEffect(() => {
    const resumeData = localStorage.getItem('resumeData');
    if (resumeData) {
      try {
        const parsed = JSON.parse(resumeData);
        setFormData(prev => ({
          ...prev,
          seniority: parsed.seniority || '',
          jobTitles: parsed.job_titles || [],
          skills: parsed.skills || [],
          educationLevel: parsed.education_level || '',
        }));
        // Keep the data for resume bypass functionality
        // localStorage.removeItem('resumeData');
      } catch (error) {
        console.error('Error parsing resume data:', error);
      }
    }
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.salaryMin) {
      newErrors.salaryMin = 'Minimum salary is required';
    } else {
      const minValue = parseFloat(formData.salaryMin);
      if (minValue < 0) {
        newErrors.salaryMin = 'Salary must be positive';
      } else {
        // Add period-specific validation
        if (formData.salaryPeriod === 'hourly' && minValue < 1) {
          newErrors.salaryMin = 'Hourly rate should be at least $1';
        } else if (formData.salaryPeriod === 'weekly' && minValue < 40) {
          newErrors.salaryMin = 'Weekly salary should be at least $40';
        } else if (formData.salaryPeriod === 'monthly' && minValue < 160) {
          newErrors.salaryMin = 'Monthly salary should be at least $160';
        } else if (formData.salaryPeriod === 'yearly' && minValue < 2000) {
          newErrors.salaryMin = 'Yearly salary should be at least $2,000';
        }
      }
    }

    if (!formData.salaryMax) {
      newErrors.salaryMax = 'Maximum salary is required';
    } else if (parseFloat(formData.salaryMax) < 0) {
      newErrors.salaryMax = 'Salary must be positive';
    }

    if (formData.salaryMin && formData.salaryMax && parseFloat(formData.salaryMax) < parseFloat(formData.salaryMin)) {
      newErrors.salaryMax = 'Maximum salary must be greater than or equal to minimum salary';
    }

    if (!formData.seniority) {
      newErrors.seniority = 'Seniority level is required';
    }

    if (formData.jobType.length === 0) {
      newErrors.jobType = 'At least one job type is required';
    }

    if (formData.jobTitles.length === 0) {
      newErrors.jobTitles = 'At least one job title is required';
    }

    if (formData.skills.length === 0) {
      newErrors.skills = 'At least one skill is required';
    }

    if (!formData.educationLevel) {
      newErrors.educationLevel = 'Education level is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const searchRequest: JobSearchRequest = {
        salaryMin: parseFloat(formData.salaryMin),
        salaryMax: parseFloat(formData.salaryMax),
        salaryPeriod: formData.salaryPeriod,
        seniority: formData.seniority,
        jobType: formData.jobType,
        jobTitles: formData.jobTitles,
        skills: formData.skills,
        educationLevel: formData.educationLevel,
      };

      await JobService.findJobs(searchRequest);
      router.push('/jobs');
    } catch (error) {
      setErrors({ submit: error instanceof Error ? error.message : 'Failed to find jobs. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleJobTypeChange = (jobType: string) => {
    setFormData(prev => ({
      ...prev,
      jobType: prev.jobType.includes(jobType)
        ? prev.jobType.filter(type => type !== jobType)
        : [...prev.jobType, jobType]
    }));
  };

  const addJobTitle = (title: string) => {
    setFormData(prev => ({
      ...prev,
      jobTitles: [...prev.jobTitles, title]
    }));
  };

  const removeJobTitle = (index: number) => {
    setFormData(prev => ({
      ...prev,
      jobTitles: prev.jobTitles.filter((_, i) => i !== index)
    }));
  };

  const addSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: [...prev.skills, skill]
    }));
  };

  const removeSkill = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index)
    }));
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Complete Your Profile
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Review and complete your job search preferences to get personalized recommendations.
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Salary Range */}
            <div className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Salary
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.salaryMin}
                    onChange={(e) => setFormData(prev => ({ ...prev, salaryMin: e.target.value }))}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.salaryMin ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="50000"
                  />
                  {errors.salaryMin && <p className="mt-1 text-sm text-red-600">{errors.salaryMin}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Salary
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.salaryMax}
                    onChange={(e) => setFormData(prev => ({ ...prev, salaryMax: e.target.value }))}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.salaryMax ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="100000"
                  />
                  {errors.salaryMax && <p className="mt-1 text-sm text-red-600">{errors.salaryMax}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Salary Period
                  </label>
                  <select
                    value={formData.salaryPeriod}
                    onChange={(e) => setFormData(prev => ({ ...prev, salaryPeriod: e.target.value as FormData['salaryPeriod'] }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="hourly">Per Hour</option>
                    <option value="weekly">Per Week</option>
                    <option value="monthly">Per Month</option>
                    <option value="yearly">Per Year</option>
                  </select>
                </div>
              </div>
              <p className="text-sm text-gray-500 italic">
                Enter salary in {formData.salaryPeriod === 'hourly' ? 'dollars per hour' : 
                  formData.salaryPeriod === 'weekly' ? 'dollars per week' : 
                  formData.salaryPeriod === 'monthly' ? 'dollars per month' : 
                  'dollars per year'}
              </p>
            </div>

            {/* Seniority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Seniority Level
              </label>
              <select
                value={formData.seniority}
                onChange={(e) => setFormData(prev => ({ ...prev, seniority: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.seniority ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select seniority level</option>
                <option value="Junior">Junior</option>
                <option value="Mid-level">Mid-level</option>
                <option value="Senior">Senior</option>
                <option value="Lead">Lead</option>
                <option value="Manager">Manager</option>
              </select>
              {errors.seniority && <p className="mt-1 text-sm text-red-600">{errors.seniority}</p>}
            </div>

            {/* Job Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Type (Select all that apply)
              </label>
              <div className="space-y-2">
                {['Full-time', 'Part-time', 'Contract'].map((type) => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.jobType.includes(type)}
                      onChange={() => handleJobTypeChange(type)}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">{type}</span>
                  </label>
                ))}
              </div>
              {errors.jobType && <p className="mt-1 text-sm text-red-600">{errors.jobType}</p>}
            </div>

            {/* Job Titles */}
            <div>
              <TagInput
                label="Job Titles"
                tags={formData.jobTitles}
                onAddTag={addJobTitle}
                onRemoveTag={removeJobTitle}
                placeholder="e.g., Software Engineer, Product Manager"
              />
              {errors.jobTitles && <p className="mt-1 text-sm text-red-600">{errors.jobTitles}</p>}
            </div>

            {/* Skills */}
            <div>
              <TagInput
                label="Skills"
                tags={formData.skills}
                onAddTag={addSkill}
                onRemoveTag={removeSkill}
                placeholder="e.g., JavaScript, Leadership, Python"
              />
              {errors.skills && <p className="mt-1 text-sm text-red-600">{errors.skills}</p>}
            </div>

            {/* Education Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Education Level
              </label>
              <select
                value={formData.educationLevel}
                onChange={(e) => setFormData(prev => ({ ...prev, educationLevel: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.educationLevel ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select education level</option>
                <option value="high school">High School</option>
                <option value="BSc">Bachelor's Degree (BSc)</option>
                <option value="MSc">Master's Degree (MSc)</option>
                <option value="PhD">Doctorate (PhD)</option>
              </select>
              {errors.educationLevel && <p className="mt-1 text-sm text-red-600">{errors.educationLevel}</p>}
            </div>

            {/* Submit Error */}
            {errors.submit && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 font-medium">{errors.submit}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isSubmitting}
                className={`px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 ${
                  isSubmitting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                }`}
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Finding Jobs...
                  </div>
                ) : (
                  'Find My Jobs'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}

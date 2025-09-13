import React from 'react';
import Link from 'next/link';

const steps = [
  {
    title: 'Upload Resume',
    description: 'Share your professional experience',
    icon: '📄'
  },
  {
    title: 'Fill Information',
    description: 'Tell us your preferences',
    icon: '✏️'
  },
  {
    title: 'Get Matches',
    description: 'Receive AI-powered job recommendations',
    icon: '🎯'
  }
];

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-primary-800 mb-6">
            Find Your Dream Job with AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform analyzes your experience and preferences to find the perfect job matches. 
            Say goodbye to endless searching and hello to targeted opportunities.
          </p>
        </div>

        {/* Journey Steps */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <div 
              key={step.title}
              className="bg-white rounded-lg p-8 shadow-soft transform hover:scale-105 transition-transform duration-200"
            >
              <div className="text-4xl mb-4">{step.icon}</div>
              <h3 className="text-xl font-semibold text-primary-700 mb-2">
                {step.title}
              </h3>
              <p className="text-gray-600">{step.description}</p>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 text-primary-300 text-2xl">
                  →
                </div>
              )}
            </div>
          ))}
        </div>

        {/* CTA Button */}
        <div className="text-center">
          <Link 
            href="/upload"
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white text-lg font-semibold px-8 py-4 rounded-lg shadow-soft transform hover:scale-105 transition-all duration-200"
          >
            Start Your Journey
          </Link>
        </div>
      </div>
    </main>
  );
}

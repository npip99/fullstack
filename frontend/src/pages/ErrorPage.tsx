import React, { useEffect, useState } from 'react';

import { Route } from '../types';
import { redirect } from '../utils';

const ErrorPage: React.FC = () => {
  const [errorMessage, setErrorMessage] = useState<string>('Unknown Error');

  useEffect(() => {
    // Get error_message from query parameters
    const params = new URLSearchParams(window.location.search);
    const error = params.get('error_message');
    if (error) {
      setErrorMessage(error);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Main Content */}
      <main className="grow flex items-center justify-center px-6">
        <div className="bg-gray-800 rounded-2xl shadow-xl p-8 w-full max-w-md">
          {/* Error Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
          </div>

          {/* Error Header */}
          <h1 className="text-3xl font-semibold text-center mb-4 text-white">
            Error
          </h1>

          {/* Error Message */}
          <p className="text-center text-lg mb-8 text-gray-300">
            {errorMessage}
          </p>

          {/* Continue Button */}
          <button
            onClick={() => redirect('/' + Route.Home)}
            className="w-full bg-blue-600 text-white rounded-lg py-3 px-4 text-lg font-medium hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Continue
          </button>
        </div>
      </main>
    </div>
  );
};

export default ErrorPage;

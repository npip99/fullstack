import React from 'react';

import { redirect } from '../utils';

const LoginPage: React.FC = () => {
  const handleGoogleSignIn = () => {
    redirect('/api/auth/google/login');
  };

  return (
    <div className={`min-h-screen bg-gray-900 flex flex-col`}>
      {/* Main Content */}
      <main className="grow flex items-center justify-center px-6">
        <div className="bg-gray-800 rounded-2xl shadow-xl p-8 w-full max-w-sm">
          {/* Card Logo */}
          <div className="flex justify-center mb-6">
            <img
              src="assets/images/logo.svg"
              alt="Logo"
              className="w-14 h-14"
            />
          </div>

          {/* Sign in Header */}
          <h1 className="text-3xl font-semibold text-center mb-8 text-white">
            Sign in
          </h1>

          {/* Sign-In Button */}
          <button
            onClick={handleGoogleSignIn}
            className="flex items-center justify-center w-full bg-white text-gray-700 rounded-lg py-3 px-4 text-lg font-medium hover:bg-gray-100 transition-colors border border-gray-300 shadow-xs cursor-pointer"
          >
            <img
              src="https://developers.google.com/identity/images/g-logo.png"
              alt="Google Logo"
              className="h-5 w-5 mr-4"
            />
            <span>Sign in with Google</span>
          </button>
        </div>
      </main>
    </div>
  );
};

export default LoginPage;

import { X } from 'lucide-react';
import React, { useState } from 'react';
import { useSelector } from 'react-redux';

import { useFocusTrap } from '../hooks/useFocusTrap';
import { RootState } from '../store/store';

const HomePage: React.FC = () => {
  const account = useSelector(
    (state: RootState) => state.loggedInState?.account
  );

  const [showModal, setShowModal] = useState(false);
  const modalRef = useFocusTrap(showModal, () => setShowModal(false));

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 text-gray-100">Home Page</h1>

      <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6">
        <div className="flex flex-col items-start gap-4">
          <h2 className="text-xl font-semibold text-gray-100">
            Welcome to the Home Page!
          </h2>
          {account !== undefined && (
            <p className="text-gray-100">
              You are currently logged in as {account.name}
            </p>
          )}
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors cursor-pointer"
          >
            Example Modal
          </button>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div
            ref={modalRef}
            className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">
                Example Modal
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className="text-gray-300 mb-6">
              This is an example modal. You can put any content here.
            </p>
            <div className="flex justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;

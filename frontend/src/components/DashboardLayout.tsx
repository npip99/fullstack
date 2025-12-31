import { Code, LogOut, Search } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';

import { actions, RootState, useAppDispatch } from '../store/store';
import { Route } from '../types';
import { redirect } from '../utils';
import SidebarLink from './SidebarLink';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = (props) => {
  const dispatch = useAppDispatch();
  const account = useSelector(
    (state: RootState) => state.loggedInState?.account
  );

  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside or pressing Escape
  useEffect(() => {
    if (!showUserDropdown) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowUserDropdown(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowUserDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [showUserDropdown]);

  return (
    <div className="h-screen flex overflow-hidden bg-gray-900">
      <aside className="shrink-0 h-full w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-4 flex justify-center">
          <img
            src="assets/images/logo-full.svg"
            alt="Full Logo"
            className="h-12"
          />
        </div>
        <SidebarLink
          icon={<Code className="text-gray-400" />}
          text="Home"
          route={Route.Home}
        />
        <SidebarLink
          icon={<Search className="text-gray-400" />}
          text="Login"
          route={Route.Login}
        />
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="shrink-0 bg-gray-800 border-b border-gray-700">
          <div className="flex items-center justify-between px-6 h-[60px]">
            <div className="relative">{/* Left side of top header */}</div>
            <div className="flex items-center space-x-4">
              {/* Right side of top header */}
              <div className="relative" ref={dropdownRef}>
                {account !== undefined && (
                  <>
                    <button
                      onClick={() => setShowUserDropdown(!showUserDropdown)}
                      className="w-8 h-8 rounded-full bg-gray-700 border border-gray-600 flex items-center justify-center text-gray-300 hover:bg-gray-600 transition-colors cursor-pointer"
                    >
                      {account.name.charAt(0).toUpperCase() || ''}
                    </button>

                    {showUserDropdown && (
                      <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-gray-800 border border-gray-600">
                        <div>
                          <button
                            onClick={() => {
                              dispatch(actions.logout());
                              redirect('/' + Route.Login);
                            }}
                            className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 w-full rounded-md cursor-pointer"
                          >
                            <LogOut className="mr-2 h-4 w-4" />
                            Log Out
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-hidden">{props.children}</main>
      </div>
    </div>
  );
};

export default DashboardLayout;

import { LucideIcon } from 'lucide-react';
import React from 'react';
import { useSelector } from 'react-redux';

import { RootState } from '../store/store';
import { Route } from '../types';

interface SidebarLinkProps {
  icon: React.ReactElement<LucideIcon>;
  text: string;
  route: Route;
  externalUrl?: string;
}

const SidebarLink: React.FC<SidebarLinkProps> = ({
  icon,
  text,
  route,
  externalUrl,
}) => {
  const currentRoute = useSelector((state: RootState) => {
    return state.route;
  });

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (externalUrl) {
      window.open(externalUrl, '_blank');
      e.preventDefault();
    } else {
      e.preventDefault();
      window.history.pushState({}, '', `/${route}`);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  return (
    <a
      href={`/${route}`}
      onClick={handleClick}
      className={`flex items-center space-x-2 px-4 py-2 text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors ${
        route === currentRoute ? 'bg-gray-700 text-[#4594ff]' : ''
      }`}
    >
      {icon}
      <span>{text}</span>
    </a>
  );
};

export default SidebarLink;

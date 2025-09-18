import React from 'react';
import { Plane, MapPin, Utensils, DollarSign } from 'lucide-react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        {/* Main spinner */}
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
        
        {/* Agent icons rotating around */}
        <div className="absolute inset-0 animate-pulse">
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-2">
            <Plane className="h-4 w-4 text-blue-500" />
          </div>
          <div className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-2">
            <MapPin className="h-4 w-4 text-green-500" />
          </div>
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-2">
            <Utensils className="h-4 w-4 text-orange-500" />
          </div>
          <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-2">
            <DollarSign className="h-4 w-4 text-purple-500" />
          </div>
        </div>
      </div>
      
      <div className="mt-8 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Creating Your Perfect Itinerary
        </h3>
        <p className="text-gray-600 mb-4">
          Our AI agents are working together to plan your trip...
        </p>
        
        <div className="space-y-2 text-sm text-gray-500">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span>Explorer Agent finding attractions...</span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Budget Agent optimizing costs...</span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
            <span>Food Agent selecting restaurants...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;

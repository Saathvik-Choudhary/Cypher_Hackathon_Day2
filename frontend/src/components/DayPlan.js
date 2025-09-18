import React from 'react';
import { 
  Clock, 
  MapPin, 
  DollarSign, 
  Star, 
  Utensils,
  Sunrise,
  Sun,
  Moon
} from 'lucide-react';

const DayPlan = ({ dayPlan, dayNumber }) => {
  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
    return `${mins}m`;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getTimeIcon = (timeOfDay) => {
    switch (timeOfDay) {
      case 'morning':
        return <Sunrise className="h-4 w-4 text-yellow-500" />;
      case 'afternoon':
        return <Sun className="h-4 w-4 text-orange-500" />;
      case 'evening':
        return <Moon className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const ActivityCard = ({ activity, timeOfDay }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-gray-900">{activity.name}</h4>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          {getTimeIcon(timeOfDay)}
          <span>{formatTime(activity.estimated_duration)}</span>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{activity.description}</p>
      
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1 text-gray-500">
            <MapPin className="h-3 w-3" />
            <span>{activity.location}</span>
          </div>
          
          {activity.entry_fee && (
            <div className="flex items-center space-x-1 text-green-600">
              <DollarSign className="h-3 w-3" />
              <span>{formatCurrency(activity.entry_fee)}</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <Star className="h-3 w-3 text-yellow-500" />
            <span className="text-xs">{activity.popularity_score}/10</span>
          </div>
          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
            {activity.category}
          </span>
        </div>
      </div>
    </div>
  );

  const RestaurantCard = ({ restaurant, mealType }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-gray-900">{restaurant.name}</h4>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          <Utensils className="h-4 w-4" />
          <span className="capitalize">{mealType}</span>
        </div>
      </div>
      
      <div className="flex items-center space-x-2 mb-2">
        <span className="text-sm text-gray-600">{restaurant.cuisine_type}</span>
        <span className="text-sm font-medium text-green-600">
          {formatCurrency(restaurant.estimated_cost_per_person)}/person
        </span>
        <div className="flex items-center space-x-1">
          <Star className="h-3 w-3 text-yellow-500" />
          <span className="text-sm">{restaurant.rating}/5</span>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{restaurant.location}</p>
      
      {restaurant.specialties && restaurant.specialties.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-700 mb-1">Specialties:</p>
          <div className="flex flex-wrap gap-1">
            {restaurant.specialties.slice(0, 3).map((specialty, index) => (
              <span key={index} className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded">
                {specialty}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {restaurant.must_try_dishes && restaurant.must_try_dishes.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-700 mb-1">Must Try:</p>
          <p className="text-xs text-gray-600">
            {restaurant.must_try_dishes.slice(0, 2).join(', ')}
          </p>
        </div>
      )}
    </div>
  );

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          Day {dayNumber}
        </h3>
        <div className="text-sm text-gray-600">
          {dayPlan.date && new Date(dayPlan.date).toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'short',
            day: 'numeric'
          })}
        </div>
      </div>

      <div className="space-y-6">
        {/* Morning Activities */}
        {dayPlan.morning_activities && dayPlan.morning_activities.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Sunrise className="h-5 w-5 mr-2 text-yellow-500" />
              Morning Activities
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dayPlan.morning_activities.map((activity, index) => (
                <ActivityCard key={index} activity={activity} timeOfDay="morning" />
              ))}
            </div>
          </div>
        )}

        {/* Lunch */}
        {dayPlan.lunch && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Sun className="h-5 w-5 mr-2 text-orange-500" />
              Lunch
            </h4>
            <RestaurantCard restaurant={dayPlan.lunch} mealType="lunch" />
          </div>
        )}

        {/* Afternoon Activities */}
        {dayPlan.afternoon_activities && dayPlan.afternoon_activities.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Sun className="h-5 w-5 mr-2 text-orange-500" />
              Afternoon Activities
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dayPlan.afternoon_activities.map((activity, index) => (
                <ActivityCard key={index} activity={activity} timeOfDay="afternoon" />
              ))}
            </div>
          </div>
        )}

        {/* Dinner */}
        {dayPlan.dinner && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Moon className="h-5 w-5 mr-2 text-blue-500" />
              Dinner
            </h4>
            <RestaurantCard restaurant={dayPlan.dinner} mealType="dinner" />
          </div>
        )}

        {/* Evening Activities */}
        {dayPlan.evening_activities && dayPlan.evening_activities.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              <Moon className="h-5 w-5 mr-2 text-blue-500" />
              Evening Activities
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dayPlan.evening_activities.map((activity, index) => (
                <ActivityCard key={index} activity={activity} timeOfDay="evening" />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Day Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Day {dayNumber} Estimated Cost:</span>
          <span className="font-medium text-green-600">
            {formatCurrency(dayPlan.total_estimated_cost)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DayPlan;

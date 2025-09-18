import React from 'react';
import { 
  Calendar, 
  MapPin, 
  Clock, 
  DollarSign, 
  Users, 
  Star, 
  Utensils, 
  Camera,
  ArrowLeft,
  Download,
  Phone
} from 'lucide-react';
import DayPlan from './DayPlan';
import BudgetBreakdown from './BudgetBreakdown';

const ItineraryDisplay = ({ itinerary, onReset }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <button
          onClick={onReset}
          className="btn-secondary mb-4"
        >
          <ArrowLeft className="inline h-4 w-4 mr-2" />
          Plan Another Trip
        </button>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Your {itinerary.destination} Itinerary
        </h1>
        <p className="text-lg text-gray-600">
          {formatDate(itinerary.day_plans[0]?.date)} - {formatDate(itinerary.day_plans[1]?.date)}
        </p>
      </div>

      {/* Budget Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BudgetBreakdown budgetBreakdown={itinerary.budget_breakdown} />
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <DollarSign className="h-5 w-5 mr-2 text-green-600" />
            Budget Summary
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Budget:</span>
              <span className="font-medium">{formatCurrency(itinerary.total_budget)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Estimated Cost:</span>
              <span className="font-medium">{formatCurrency(itinerary.total_estimated_cost)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Remaining:</span>
              <span className="font-medium text-green-600">
                {formatCurrency(itinerary.total_budget - itinerary.total_estimated_cost)}
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between">
                <span className="text-gray-600">Budget Used:</span>
                <span className="font-medium">
                  {itinerary.budget_utilization_percentage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(itinerary.budget_utilization_percentage, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Day Plans */}
      <div className="space-y-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center">
          2-Day Itinerary
        </h2>
        
        {itinerary.day_plans.map((dayPlan, index) => (
          <DayPlan key={index} dayPlan={dayPlan} dayNumber={index + 1} />
        ))}
      </div>

      {/* Recommendations */}
      {itinerary.recommendations && itinerary.recommendations.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Star className="h-5 w-5 mr-2 text-yellow-500" />
            AI Recommendations
          </h3>
          <ul className="space-y-2">
            {itinerary.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Emergency Contacts */}
      <div className="card bg-red-50 border-red-200">
        <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
          <Phone className="h-5 w-5 mr-2" />
          Emergency Contacts
        </h3>
        <ul className="space-y-2">
          {itinerary.emergency_contacts.map((contact, index) => (
            <li key={index} className="text-red-800">
              {contact}
            </li>
          ))}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="text-center space-x-4">
        <button className="btn-primary">
          <Download className="inline h-4 w-4 mr-2" />
          Download Itinerary
        </button>
        <button className="btn-secondary">
          Share Itinerary
        </button>
      </div>
    </div>
  );
};

export default ItineraryDisplay;

import React from 'react';
import { 
  Home, 
  Car, 
  Utensils, 
  Camera, 
  Plus,
  DollarSign
} from 'lucide-react';

const BudgetBreakdown = ({ budgetBreakdown }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getPercentage = (amount, total) => {
    return total > 0 ? (amount / total) * 100 : 0;
  };

  const budgetItems = [
    {
      name: 'Accommodation',
      amount: budgetBreakdown.accommodation,
      icon: Home,
      color: 'bg-blue-500',
      description: 'Hotels, hostels, or other lodging'
    },
    {
      name: 'Transportation',
      amount: budgetBreakdown.transportation,
      icon: Car,
      color: 'bg-green-500',
      description: 'Flights, local transport, taxis'
    },
    {
      name: 'Food & Dining',
      amount: budgetBreakdown.food,
      icon: Utensils,
      color: 'bg-orange-500',
      description: 'Restaurants, cafes, street food'
    },
    {
      name: 'Activities',
      amount: budgetBreakdown.activities,
      icon: Camera,
      color: 'bg-purple-500',
      description: 'Attractions, tours, entertainment'
    },
    {
      name: 'Miscellaneous',
      amount: budgetBreakdown.miscellaneous,
      icon: Plus,
      color: 'bg-gray-500',
      description: 'Shopping, tips, unexpected expenses'
    }
  ];

  const totalAllocated = budgetItems.reduce((sum, item) => sum + item.amount, 0);
  const remaining = budgetBreakdown.total_budget - totalAllocated;

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
        <DollarSign className="h-5 w-5 mr-2 text-green-600" />
        Budget Breakdown
      </h3>

      <div className="space-y-4">
        {budgetItems.map((item, index) => {
          const Icon = item.icon;
          const percentage = getPercentage(item.amount, budgetBreakdown.total_budget);
          
          return (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${item.color}`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{item.name}</h4>
                    <p className="text-xs text-gray-500">{item.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">
                    {formatCurrency(item.amount)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {percentage.toFixed(1)}%
                  </div>
                </div>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${item.color}`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Total and Remaining */}
      <div className="mt-6 pt-4 border-t border-gray-200 space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-medium text-gray-900">Total Allocated:</span>
          <span className="font-medium text-gray-900">
            {formatCurrency(totalAllocated)}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="font-medium text-gray-900">Remaining Budget:</span>
          <span className={`font-medium ${remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(remaining)}
          </span>
        </div>
        
        {remaining < 0 && (
          <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
            ⚠️ You're over budget by {formatCurrency(Math.abs(remaining))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BudgetBreakdown;

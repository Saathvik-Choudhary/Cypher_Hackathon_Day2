import React, { useState, useEffect } from 'react';
import { Calendar, Users, DollarSign, MapPin, Heart, Star } from 'lucide-react';
import { getPopularDestinations, getTravelPreferences, getBudgetCategories } from '../services/api';

const TravelForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    destination: '',
    budget: '',
    budget_category: 'moderate',
    travel_preferences: [],
    start_date: '',
    group_size: 1,
    special_requirements: ''
  });

  const [destinations, setDestinations] = useState([]);
  const [preferences, setPreferences] = useState([]);
  const [budgetCategories, setBudgetCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [destinationsRes, preferencesRes, budgetRes] = await Promise.all([
          getPopularDestinations(),
          getTravelPreferences(),
          getBudgetCategories()
        ]);
        
        setDestinations(destinationsRes.destinations || []);
        setPreferences(preferencesRes.preferences || []);
        setBudgetCategories(budgetRes.categories || []);
      } catch (error) {
        console.error('Error fetching form data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreferenceChange = (preference) => {
    setFormData(prev => ({
      ...prev,
      travel_preferences: prev.travel_preferences.includes(preference)
        ? prev.travel_preferences.filter(p => p !== preference)
        : [...prev.travel_preferences, preference]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.destination || !formData.budget || !formData.start_date) {
      alert('Please fill in all required fields');
      return;
    }

    if (formData.travel_preferences.length === 0) {
      alert('Please select at least one travel preference');
      return;
    }

    // Convert budget to number
    const submitData = {
      ...formData,
      budget: parseFloat(formData.budget),
      group_size: parseInt(formData.group_size)
    };

    onSubmit(submitData);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Destination */}
        <div className="card">
          <label className="label">
            <MapPin className="inline h-4 w-4 mr-1" />
            Destination *
          </label>
          <select
            name="destination"
            value={formData.destination}
            onChange={handleInputChange}
            className="input-field"
            required
          >
            <option value="">Select a destination</option>
            {destinations.map((dest, index) => (
              <option key={index} value={dest.name}>
                {dest.name} - {dest.category}
              </option>
            ))}
          </select>
        </div>

        {/* Budget */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <label className="label">
              <DollarSign className="inline h-4 w-4 mr-1" />
              Total Budget (USD) *
            </label>
            <input
              type="number"
              name="budget"
              value={formData.budget}
              onChange={handleInputChange}
              className="input-field"
              placeholder="500"
              min="100"
              step="50"
              required
            />
          </div>

          <div className="card">
            <label className="label">
              <Star className="inline h-4 w-4 mr-1" />
              Budget Category *
            </label>
            <select
              name="budget_category"
              value={formData.budget_category}
              onChange={handleInputChange}
              className="input-field"
              required
            >
              {budgetCategories.map((category, index) => (
                <option key={index} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Travel Preferences */}
        <div className="card">
          <label className="label">
            <Heart className="inline h-4 w-4 mr-1" />
            Travel Preferences * (Select at least one)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {preferences.map((pref, index) => (
              <label key={index} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.travel_preferences.includes(pref.value)}
                  onChange={() => handlePreferenceChange(pref.value)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">{pref.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Date and Group Size */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <label className="label">
              <Calendar className="inline h-4 w-4 mr-1" />
              Start Date *
            </label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleInputChange}
              className="input-field"
              min={new Date().toISOString().split('T')[0]}
              required
            />
          </div>

          <div className="card">
            <label className="label">
              <Users className="inline h-4 w-4 mr-1" />
              Group Size
            </label>
            <input
              type="number"
              name="group_size"
              value={formData.group_size}
              onChange={handleInputChange}
              className="input-field"
              min="1"
              max="10"
            />
          </div>
        </div>

        {/* Special Requirements */}
        <div className="card">
          <label className="label">
            Special Requirements (Optional)
          </label>
          <textarea
            name="special_requirements"
            value={formData.special_requirements}
            onChange={handleInputChange}
            className="input-field"
            rows="3"
            placeholder="Any special requirements, dietary restrictions, accessibility needs, etc."
          />
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            className="btn-primary px-8 py-3 text-lg"
          >
            Create My Itinerary
          </button>
        </div>
      </form>
    </div>
  );
};

export default TravelForm;

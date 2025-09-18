import React from 'react';
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets, Thermometer } from 'lucide-react';

const WeatherForecast = ({ weatherForecast }) => {
  if (!weatherForecast || weatherForecast.length === 0) {
    return null;
  }

  const getWeatherIcon = (description) => {
    const desc = description.toLowerCase();
    if (desc.includes('sun') || desc.includes('clear')) {
      return <Sun className="h-6 w-6 text-yellow-500" />;
    } else if (desc.includes('cloud')) {
      return <Cloud className="h-6 w-6 text-gray-500" />;
    } else if (desc.includes('rain')) {
      return <CloudRain className="h-6 w-6 text-blue-500" />;
    } else if (desc.includes('snow')) {
      return <CloudSnow className="h-6 w-6 text-blue-200" />;
    } else {
      return <Cloud className="h-6 w-6 text-gray-400" />;
    }
  };

  const formatTemperature = (temp) => {
    return `${Math.round(temp)}°C`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Thermometer className="h-5 w-5 mr-2 text-blue-600" />
        Weather Forecast
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {weatherForecast.map((forecast, index) => (
          <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getWeatherIcon(forecast.description)}
                <span className="font-medium text-gray-900">
                  {formatDate(forecast.date)}
                </span>
              </div>
              <span className="text-2xl font-bold text-blue-600">
                {formatTemperature(forecast.temperature)}
              </span>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-gray-600 capitalize">
                {forecast.description}
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <Droplets className="h-3 w-3" />
                  <span>{forecast.humidity}%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Wind className="h-3 w-3" />
                  <span>{forecast.wind_speed} m/s</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          💡 <strong>Weather Tip:</strong> Check the forecast before heading out and pack accordingly. 
          Consider indoor alternatives if weather conditions are unfavorable.
        </p>
      </div>
    </div>
  );
};

export default WeatherForecast;

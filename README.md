# AI Weekend Travel Buddy

An intelligent travel planning application powered by multi-agent AI collaboration that generates personalized 2-day itineraries for any destination and budget.

## 🌟 Features

- **Multi-Agent AI System**: Three specialized AI agents work together to create comprehensive travel plans
  - **Explorer Agent**: Finds top attractions and activities with detailed information
  - **Budget Agent**: Optimizes budget allocation across travel, accommodation, food, and activities
  - **Food Agent**: Recommends restaurants, cafes, and local culinary experiences
- **Modern React Frontend**: Beautiful, responsive UI built with React and Tailwind CSS
- **FastAPI Backend**: High-performance Python API with automatic documentation
- **Single Container Deployment**: Easy deployment with Docker
- **Real-time Itinerary Generation**: AI agents collaborate to create optimized 2-day plans

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   AI Agents     │
│                 │◄──►│   Backend       │◄──►│                 │
│ - Travel Form   │    │                 │    │ - Explorer      │
│ - Itinerary     │    │ - Orchestrator  │    │ - Budget        │
│ - Budget View   │    │ - API Endpoints │    │ - Food          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Cyber_Hack_Day2
```

### 2. Environment Configuration

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Build and Run with Docker

```bash
# Build and start the application
docker-compose up --build

# The application will be available at http://localhost:8000
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🛠️ Development Setup

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
python main.py
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📱 Usage

1. **Enter Trip Details**: Fill in destination, budget, travel preferences, and dates
2. **AI Processing**: Watch as three AI agents collaborate to create your itinerary
3. **Review Itinerary**: Explore your personalized 2-day plan with:
   - Detailed day-by-day activities
   - Restaurant recommendations
   - Budget breakdown
   - Travel tips and recommendations

## 🔧 API Endpoints

### Core Endpoints

- `POST /api/create-itinerary` - Create a new travel itinerary
- `GET /api/health` - Health check endpoint
- `GET /api/destinations/popular` - Get popular destinations
- `GET /api/preferences` - Get available travel preferences
- `GET /api/budget-categories` - Get budget categories

### Example API Usage

```bash
curl -X POST "http://localhost:8000/api/create-itinerary" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris, France",
    "budget": 500,
    "budget_category": "moderate",
    "travel_preferences": ["culture", "food"],
    "start_date": "2024-06-15",
    "group_size": 2
  }'
```

## 🏗️ Project Structure

```
├── agents/                 # AI Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── explorer_agent.py  # Attraction discovery agent
│   ├── budget_agent.py    # Budget optimization agent
│   └── food_agent.py      # Restaurant recommendation agent
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   └── App.js         # Main React app
│   └── package.json       # Frontend dependencies
├── main.py                # FastAPI application
├── orchestrator.py        # Agent coordination logic
├── models.py              # Pydantic data models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Docker Compose setup
```

## 🤖 AI Agents

### Explorer Agent
- Discovers top attractions and activities
- Provides detailed information (hours, fees, duration)
- Ranks attractions by popularity and uniqueness
- Optimizes selection based on preferences and budget

### Budget Agent
- Distributes budget across categories (accommodation, food, activities, transport)
- Estimates costs for planned activities
- Provides budget optimization recommendations
- Ensures realistic spending within budget constraints

### Food Agent
- Recommends restaurants, cafes, and street food
- Suggests local must-try dishes
- Provides meal planning for each day
- Offers culinary tips and local insights

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build production image
docker build -t travel-buddy .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  travel-buddy
```

### Docker Compose

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔒 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI agents | Yes |
| `GOOGLE_PLACES_API_KEY` | Google Places API key (optional) | No |
| `API_HOST` | API server host | No (default: 0.0.0.0) |
| `API_PORT` | API server port | No (default: 8000) |
| `DEBUG` | Enable debug mode | No (default: false) |

## 🧪 Testing

```bash
# Test API endpoints
curl http://localhost:8000/api/health

# Test itinerary creation
curl -X POST http://localhost:8000/api/create-itinerary \
  -H "Content-Type: application/json" \
  -d '{"destination": "Tokyo, Japan", "budget": 600, "budget_category": "moderate", "travel_preferences": ["culture", "food"], "start_date": "2024-06-15", "group_size": 1}'
```

## 📊 Performance

- **Response Time**: Typically 10-30 seconds for itinerary generation
- **Concurrent Users**: Supports multiple simultaneous requests
- **Memory Usage**: ~200MB per container instance
- **API Rate Limits**: Respects OpenAI API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the health check at `/api/health`
- Check Docker logs: `docker-compose logs`

## 🎯 Future Enhancements

- [ ] Real-time weather integration
- [ ] Hotel booking integration
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Social sharing features
- [ ] Offline mode support

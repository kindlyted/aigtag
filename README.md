# Mystic Divination Service

A modern web application that combines traditional Chinese divination with AI technology.

## Project Structure

```
mystic-divination-service/
├── backend/                 # Flask backend
│   ├── prompt/             # AI prompt templates
│   ├── app.py              # Main Flask application
│   ├── services.py         # Business logic services
│   ├── utils.py            # Utility functions
│   ├── constants.py        # Constants and configurations
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vue.js frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── index.html         # Entry HTML
│   ├── package.json       # Frontend dependencies
│   └── vite.config.js     # Vite configuration
└── package.json           # Root package.json for project management
```

## Prerequisites

- Node.js >= 16
- Python >= 3.8
- npm or yarn

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mystic-divination-service
```

2. Install dependencies:
```bash
# Install both frontend and backend dependencies
npm install
```

## Development

Run both frontend and backend in development mode:
```bash
npm run dev
```

Or run them separately:
```bash
# Run frontend only
npm run frontend:dev

# Run backend only
npm run backend:dev
```

## Production Build

1. Build the frontend:
```bash
npm run build
```

2. Deploy:
- Frontend files will be in `frontend/dist/`
- Configure your web server to serve these files
- Set up the Python backend with your preferred WSGI server (e.g., Gunicorn)

## Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
FLASK_APP=app.py
```

## API Documentation

Backend API documentation is available at `/apidocs` when running the Flask application.

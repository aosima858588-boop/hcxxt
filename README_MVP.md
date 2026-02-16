# Data Import & Query MVP

A minimal FastAPI-based CSV import and search MVP with Docker support and Render deployment guide.

## Features

- 📤 **CSV Upload**: Upload CSV files and automatically parse them into a searchable database
- 🔍 **Search**: Search across dataset records with pagination support
- 📊 **Dataset Management**: View all datasets with row counts and delete unwanted datasets
- 🎨 **Simple UI**: Clean single-page interface for all operations
- 🐳 **Docker Ready**: Containerized for easy deployment
- ☁️ **Render Deploy**: One-click deployment to Render

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/aosima858588-boop/hcxxt.git
   cd hcxxt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Open in browser**
   ```
   http://localhost:8000
   ```

### Using Docker

1. **Build the image**
   ```bash
   docker build -t data-query-mvp .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 data-query-mvp
   ```

3. **Access the application**
   ```
   http://localhost:8000
   ```

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

### Deployment Steps

1. **Push your code to GitHub**

2. **Sign up/Login to Render** at https://render.com

3. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `aosima858588-boop/hcxxt`
   - Select the branch: `add/data-query-mvp`

4. **Configure the service**
   - **Name**: `data-query-mvp` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `add/data-query-mvp`
   - **Plan**: Free (or your preferred plan)

5. **Environment Variables** (Optional)
   - `DATABASE_URL`: PostgreSQL URL if you want persistent storage
     - On Free plan, use Render's PostgreSQL database
     - Click "New +" → "PostgreSQL" to create one
     - Copy the Internal Database URL to `DATABASE_URL`

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your app will be available at: `https://your-app-name.onrender.com`

### Using Render PostgreSQL (Recommended for Production)

1. Create a PostgreSQL database:
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `data-query-db`
   - Plan: Free or paid

2. Get the Internal Database URL from your PostgreSQL dashboard

3. Add to your Web Service:
   - Environment → Add environment variable
   - Key: `DATABASE_URL`
   - Value: `postgresql://...` (from PostgreSQL dashboard)

## API Endpoints

### POST /api/upload_csv
Upload and parse a CSV file.

**Request:**
- Form data:
  - `name`: Dataset name (string)
  - `file`: CSV file

**Response:**
```json
{
  "dataset_id": 1,
  "row_count": 100,
  "columns": ["name", "age", "city"]
}
```

### GET /api/datasets
List all datasets.

**Response:**
```json
[
  {
    "id": 1,
    "name": "employees",
    "columns": ["name", "age", "city"],
    "row_count": 100,
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### GET /api/search
Search dataset records.

**Query Parameters:**
- `dataset_id`: Dataset ID (required)
- `q`: Search query (optional, searches in all fields)
- `limit`: Results per page (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "dataset_id": 1,
  "dataset_name": "employees",
  "total": 100,
  "limit": 100,
  "offset": 0,
  "records": [
    {
      "id": 1,
      "data": {"name": "John", "age": "30", "city": "NYC"}
    }
  ]
}
```

### DELETE /api/datasets/{dataset_id}
Delete a dataset and all its records.

**Response:**
```json
{
  "message": "Dataset 1 deleted successfully"
}
```

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLModel + SQLAlchemy (SQLite by default, PostgreSQL for production)
- **Data Processing**: Pandas
- **Frontend**: Vanilla JavaScript + HTML/CSS
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection URL
  - Default: `sqlite:///./data.db`
  - PostgreSQL example: `postgresql://user:password@host:port/database`
- `PORT`: Server port (default: 8000)

## Database Schema

### Dataset Table
- `id`: Primary key
- `name`: Dataset name
- `columns`: JSON array of column names
- `row_count`: Number of rows
- `created_at`: Timestamp

### Record Table
- `id`: Primary key
- `dataset_id`: Foreign key to Dataset
- `data`: JSON object containing row data

## Development

### Project Structure
```
hcxxt/
├── app/
│   ├── __init__.py
│   ├── database.py       # Database setup and session management
│   ├── models.py         # SQLModel models
│   ├── main.py          # FastAPI application and routes
│   └── static/
│       └── index.html   # Frontend UI
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI
├── Dockerfile           # Docker configuration
├── .dockerignore
├── .gitignore
├── requirements.txt     # Python dependencies
└── README.md
```

### Running Tests

The application includes a basic CI workflow that:
- Installs dependencies
- Checks if the app can start
- Builds the Docker image

Run locally:
```bash
# Test app startup
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test Docker build
docker build -t data-query-mvp .
```

## License

MIT License - See LICENSE file for details

## Contributing

Issues and pull requests are welcome!

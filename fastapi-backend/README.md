# FastAPI Backend for Vue Application

This project serves as a backend for a Vue application, providing an API to interact with the Paris Metro Assistant functionalities.

## Project Structure

```
fastapi-backend
├── app
│   ├── main.py               # Entry point of the FastAPI application
│   ├── api
│   │   └── routes.py         # API routes for the application
│   ├── core
│   │   └── config.py         # Configuration settings for the application
│   ├── services
│   │   └── metro_service.py   # Service layer for metro-related functionalities
│   └── functions
│       └── functionsV1.py    # Existing functions for metro operations
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd fastapi-backend
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Run the FastAPI application:**
   ```
   uvicorn app.main:app --reload
   ```

## Usage

Once the application is running, you can access the API at `http://127.0.0.1:8000`. The interactive API documentation can be found at `http://127.0.0.1:8000/docs`.

## API Endpoints

- **Calculate Trip:** `/api/calculate_trip`
- **Display All Station IDs:** `/api/station_ids`
- **Display Stations for a Metro Line:** `/api/metro_line/{line_number}`

## Contributing

Feel free to submit issues or pull requests for any improvements or bug fixes.
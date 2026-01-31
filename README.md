# Chemical Equipment Parameter Visualizer

A hybrid Web + Desktop application for data visualization and analytics of chemical equipment parameters. Upload CSV files containing equipment data and view interactive charts, summary statistics, and generate PDF reports.

![Application Screenshot](docs/screenshot.png)

## 🚀 Features

- **CSV Upload** - Upload equipment data via both Web and Desktop interfaces
- **Data Summary API** - Total counts, averages, and equipment type distribution
- **Interactive Visualizations** - Charts using Chart.js (Web) and Matplotlib (Desktop)
- **History Management** - Store and access last 5 uploaded datasets
- **PDF Report Generation** - Download comprehensive equipment reports
- **Basic Authentication** - User registration and login system
- **Cross-Platform** - Works on Windows, macOS, and Linux

## 📁 Project Structure

```
MLP/
├── backend/                    # Django REST API Backend
│   ├── api/                    # Main API application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API endpoints
│   │   ├── serializers.py     # Data serialization
│   │   ├── urls.py            # URL routing
│   │   └── utils.py           # Utility functions (PDF, CSV parsing)
│   ├── backend/               # Django project settings
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
├── frontend-web/              # React.js Web Frontend
│   ├── public/                # Static files
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── api.js             # API client
│   │   ├── App.js             # Main application
│   │   └── index.css          # Styles
│   └── package.json           # Node dependencies
├── frontend-desktop/          # PyQt5 Desktop Frontend
│   ├── main.py                # Main application
│   └── requirements.txt       # Python dependencies
├── sample_equipment_data.csv  # Sample data for testing
└── README.md                  # This file
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend | Django + Django REST Framework | REST API |
| Frontend (Web) | React.js + Chart.js | Web interface |
| Frontend (Desktop) | PyQt5 + Matplotlib | Desktop application |
| Data Processing | Pandas | CSV parsing & analytics |
| Database | SQLite | Data storage |
| PDF Generation | ReportLab | PDF reports |

## 📋 Prerequisites

- **Python 3.9+** (for Backend and Desktop app)
- **Node.js 16+** (for Web frontend)
- **pip** (Python package manager)
- **npm** or **yarn** (Node package manager)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The backend API will be available at: `http://localhost:8000/api/`

### 3. Web Frontend Setup

Open a new terminal:

```bash
# Navigate to web frontend directory
cd frontend-web

# Install dependencies
npm install

# Start the development server
npm start
```

The web application will be available at: `http://localhost:3000`

### 4. Desktop Frontend Setup

Open a new terminal:

```bash
# Navigate to desktop frontend directory
cd frontend-desktop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the desktop application
python main.py
```

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is provided for testing. The expected CSV format:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A1,Reactor,150.5,25.3,180.0
Pump-P101,Pump,200.0,15.8,45.0
...
```

### Required Columns:
- **Equipment Name** - Name/ID of the equipment
- **Type** - Equipment type (e.g., Reactor, Pump, Compressor)
- **Flowrate** - Flow rate value (numeric)
- **Pressure** - Pressure value (numeric)
- **Temperature** - Temperature value (numeric)

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | API health check |
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | User login |
| `/api/auth/logout/` | POST | User logout |
| `/api/auth/user/` | GET | Get current user |
| `/api/datasets/` | GET | List datasets (last 5) |
| `/api/datasets/<id>/` | GET, DELETE | Get or delete dataset |
| `/api/datasets/<id>/summary/` | GET | Get dataset summary |
| `/api/datasets/<id>/records/` | GET | Get equipment records |
| `/api/datasets/<id>/report/` | GET | Download PDF report |
| `/api/upload/` | POST | Upload CSV file |

## 📱 Usage

### Web Application

1. Open `http://localhost:3000` in your browser
2. (Optional) Register/Login for personalized experience
3. Upload a CSV file using the upload section
4. View summary statistics, charts, and data table
5. Download PDF reports for analysis

### Desktop Application

1. Launch the application with `python main.py`
2. (Optional) Login using the authentication panel
3. Click "Select CSV File" to upload data
4. Navigate between Charts and Data Table tabs
5. Download PDF reports using the button

## 🔐 Authentication

The application supports basic authentication:

- **Register**: Create a new account with username, email, and password
- **Login**: Access your account and view personalized data
- **Logout**: Securely end your session

Note: Authentication is optional. The application works without login.

## 📄 PDF Reports

Generated PDF reports include:
- Dataset name and generation timestamp
- Total records count
- Summary statistics (averages for Flowrate, Pressure, Temperature)
- Equipment type distribution table
- Complete equipment data table (up to 50 records)

## 🐛 Troubleshooting

### Backend Issues

**Error: "Cannot connect to the backend API"**
- Ensure Django server is running: `python manage.py runserver`
- Check if port 8000 is available

**Error: "Missing required columns"**
- Verify CSV has columns: Equipment Name, Type, Flowrate, Pressure, Temperature

### Web Frontend Issues

**Error: "npm start fails"**
- Delete `node_modules` and run `npm install` again
- Ensure Node.js version is 16+

### Desktop Frontend Issues

**Error: "PyQt5 not found"**
- Ensure you're in the virtual environment
- Run `pip install PyQt5`

**Error: "matplotlib backend error"**
- Run `pip install PyQt5 matplotlib` again

## 🚀 Deployment

### Backend Deployment (Production)

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a production server (Gunicorn, uWSGI)
4. Set up a proper database (PostgreSQL recommended)

### Web Frontend Deployment

```bash
cd frontend-web
npm run build
```

Deploy the `build/` folder to a static hosting service (Netlify, Vercel, etc.)

## 📹 Demo Video

For a 2-3 minute demonstration of the application, see: [Demo Video Link]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is created for educational purposes as part of an intern screening task.

## 👤 Author

[Your Name]

## 🙏 Acknowledgments

- Django REST Framework for the excellent API toolkit
- React.js and Chart.js for web visualization
- PyQt5 and Matplotlib for desktop visualization
- ReportLab for PDF generation

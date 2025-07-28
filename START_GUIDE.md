# 🚀 Quick Start Guide - AOI Website

## How to Run Your Website

### Option 1: Automated Startup (Recommended)

**Windows Users:**
1. Double-click `start_backend.bat` 
2. Wait for "Uvicorn running on http://0.0.0.0:8000" message
3. Double-click `start_frontend.bat` in a new window
4. Wait for "Local: http://localhost:5173/" message
5. Open browser to http://localhost:5173/

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```cmd
cd E:\site\backend-flask
python main.py
```

**Terminal 2 - Frontend:**
```cmd
cd E:\site\aoi-web-front
npm run dev
```

## 🌐 Access Your Website

| Service | URL | Description |
|---------|-----|-------------|
| **Main Website** | http://localhost:5173/ | Your AOI web application |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Backend status |

## ✅ Success Indicators

**Backend is Ready When You See:**
```
✅ Port 8000 is available
🌐 Starting server at http://0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Frontend is Ready When You See:**
```
VITE v7.0.6  ready in XXXms
➜  Local:   http://localhost:5173/
```

## 🔧 Troubleshooting

### Port Already in Use
- Backend will automatically find ports 8000-8010
- Frontend uses port 5173 by default

### Backend Won't Start
```cmd
# Check Python version (need 3.8+)
python --version

# Install missing dependencies
cd backend-flask
pip install -r requirements.txt

# On Windows, you may need:
pip install pywin32
```

### Frontend Won't Start
```cmd
# Check Node.js version (need 16+)
node --version

# Install dependencies
cd aoi-web-front
npm install

# Clear cache if needed
npm run build
```

### Can't Access Website
1. Make sure both servers are running
2. Check firewall settings
3. Try http://127.0.0.1:5173/ instead
4. Check browser console for errors

## 🛑 How to Stop

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal
- **Or**: Close the command prompt windows

## 📱 What You Should See

Your AOI website should load with:
- Login screen
- Dashboard with industrial vision controls
- Camera management interface
- Algorithm debugging tools
- System configuration options

---

**Need Help?** Run `python verify_project.py` to check your setup!
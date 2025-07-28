# Frontend API Migration Guide

## Issue Fixed
The backend now uses **dynamic port discovery** (8000, 8001, 8002, etc.) but the frontend was hardcoded to port 8000, causing connection failures.

## ✅ What's Been Fixed

### 1. **Enhanced URL Configuration** (`src/url.js`)
- ✅ Added dynamic port discovery
- ✅ Health check-based backend detection  
- ✅ Automatic fallback to port 8000
- ✅ Backward compatibility maintained

### 2. **New API Utility** (`src/utils/api.js`)
- ✅ Automatic port discovery for all API calls
- ✅ Enhanced error handling
- ✅ Same interface as existing request methods

### 3. **Updated Vite Proxy** (`vite.config.js`)
- ✅ Dynamic backend port discovery during development
- ✅ Automatic proxy configuration

### 4. **Example Migration** (`src/store/media/actions.js`)
- ✅ Migrated to use new API utility
- ✅ Enhanced error handling
- ✅ Better logging

## 🔄 How to Migrate Remaining API Calls

**There are 217 API calls across 35 files that need migration.**

### Before (Old Pattern):
```javascript
import { get, post } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

const { response, responseData } = await get(`http://${ipAddress}:${port}/endpoint`);
```

### After (New Pattern):
```javascript
import api from "../../utils/api.js";

const { response, responseData } = await api.get('/endpoint');
```

## 📋 Files That Need Migration

**High Priority (Core functionality):**
- `src/store/auth/actions.js` - Authentication
- `src/store/algorithms/actions.js` - Algorithm management  
- `src/store/camera_settings/actions.js` - Camera configuration
- `src/store/process/actions.js` - Process management

**Medium Priority:**
- All other store action files
- Component files with direct API calls

## 🚀 Migration Steps

1. **Import the new API utility:**
   ```javascript
   import api from "../../utils/api.js";
   ```

2. **Replace URL construction:**
   ```javascript
   // OLD
   `http://${ipAddress}:${port}/endpoint`
   
   // NEW  
   '/endpoint'
   ```

3. **Update method calls:**
   ```javascript
   // OLD
   await get(url)
   
   // NEW
   await api.get('/endpoint')
   ```

4. **Add error handling:**
   ```javascript
   try {
       const { response, responseData } = await api.get('/endpoint');
       // handle response
   } catch (error) {
       console.error('API call failed:', error);
       throw error;
   }
   ```

## 🧪 Testing

1. **Start Backend:**
   ```bash
   cd backend-flask
   python main.py
   ```
   Backend will automatically use available port (8000, 8001, etc.)

2. **Start Frontend:**
   ```bash
   cd aoi-web-front
   npm run dev
   ```
   Frontend will automatically discover backend port

3. **Check Console:**
   - Look for: `🔍 Backend discovered on port: XXXX`
   - Vite proxy: `✅ Backend discovered on port XXXX for Vite proxy`

## 🎯 Benefits After Migration

- ✅ **Automatic Port Discovery** - No more connection failures
- ✅ **Better Error Handling** - Clear error messages  
- ✅ **Development Friendly** - No manual port configuration
- ✅ **Production Ready** - Fallbacks and retries built-in
- ✅ **Future Proof** - Scales with multiple backend instances

## 🔧 Immediate Fix for Testing

The current system will work for basic testing:
- Media API calls are already migrated
- Health check endpoint is working
- Port discovery is functional

For full functionality, migrate the remaining API calls using the patterns shown above.
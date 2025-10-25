# Korean Satellite Data Sources Guide

## 🇰🇷 Overview

This guide explains how to access and use high-quality satellite imagery specifically for South Korea locations. The application currently uses **ESRI World Imagery** which provides global satellite coverage, but you can enhance it with Korea-specific data sources for better resolution and more recent imagery.

---

## 📡 Available Korean Satellite Data Sources

### 1. **VWorld (브이월드)** - RECOMMENDED ✅

**Provider:** Korean Ministry of Land, Infrastructure and Transport  
**Website:** https://www.vworld.kr/  
**API Documentation:** https://www.vworld.kr/dev/v4dv_2dmapapi2d_guide.do

**Features:**
- ✅ FREE for non-commercial use
- ✅ High-resolution satellite imagery (up to 0.5m resolution)
- ✅ Updated regularly (quarterly)
- ✅ Covers all of South Korea
- ✅ No daily request limits for personal use
- ✅ Official government data

**How to Get API Key:**
1. Visit https://www.vworld.kr/
2. Click "회원가입" (Sign Up) - requires Korean phone number or i-PIN
3. Log in and go to "오픈API" menu
4. Click "API 신청" (Apply for API)
5. Fill out the form (purpose, website URL, etc.)
6. Approval is usually instant for personal projects
7. Copy your API key

**Tile URL Format:**
```
https://api.vworld.kr/req/wmts/1.0.0/{API_KEY}/Satellite/{z}/{y}/{x}.jpeg
```

**Integration Example:**
```typescript
// In App.tsx, replace the ESRI tile layer with:
<TileLayer
  attribution='© VWorld - Korean Ministry of Land'
  url={`https://api.vworld.kr/req/wmts/1.0.0/YOUR_API_KEY_HERE/Satellite/{z}/{y}/{x}.jpeg`}
  maxZoom={19}
/>
```

---

### 2. **Kakao Map (카카오맵)**

**Provider:** Kakao Corp  
**Website:** https://apis.map.kakao.com/  
**Documentation:** https://apis.map.kakao.com/web/guide/

**Features:**
- ✅ High-quality satellite imagery
- ✅ Skyview (스카이뷰) with detailed aerial photos
- ✅ Free tier: 300,000 requests/day
- ✅ Easy integration with React
- ⚠️ Requires Korean business registration for commercial use

**How to Get API Key:**
1. Visit https://developers.kakao.com/
2. Sign up (requires Korean phone or email)
3. Go to "내 애플리케이션" (My Applications)
4. Create new application
5. Go to "플랫폼" > "Web" and add your domain
6. Copy JavaScript key from "앱 키" section

**Integration Example:**
```typescript
// Add to public/index.html
<script src="//dapi.kakao.com/v2/maps/sdk.js?appkey=YOUR_APP_KEY&libraries=services"></script>

// Or use react-kakao-maps-sdk
npm install react-kakao-maps-sdk
```

---

### 3. **Naver Map (네이버 지도)**

**Provider:** Naver Corp  
**Website:** https://www.ncloud.com/product/applicationService/maps  
**Documentation:** https://api.ncloud-docs.com/docs/ai-naver-mapsgeocoding

**Features:**
- ✅ Satellite and hybrid view
- ✅ Street view integration
- ✅ Free tier: 50,000 requests/day
- ✅ Very detailed urban areas
- ⚠️ More complex setup than Kakao

**How to Get API Key:**
1. Visit https://www.ncloud.com/
2. Sign up (requires Korean ID verification)
3. Go to Console > AI·NAVER API > Application Registration
4. Enable "Maps" service
5. Get Client ID and Client Secret

---

### 4. **Sentinel Hub (European Space Agency)**

**Provider:** ESA/Copernicus  
**Website:** https://www.sentinel-hub.com/  
**Focus:** Korea Peninsula included

**Features:**
- ✅ FREE for research and development
- ✅ Very high resolution (10m multispectral, 10m-60m depending on band)
- ✅ Updated every 5 days
- ✅ Multi-spectral analysis capabilities
- ✅ Time-series data available
- ⚠️ Requires some technical knowledge

**How to Access:**
1. Sign up at https://www.sentinel-hub.com/
2. Create a new configuration
3. Use the API or WMS service

**Example Coordinates for Testing:**
- Seoul: 37.5665, 126.9780
- Incheon Airport: 37.4602, 126.4407
- Busan: 35.1796, 129.0756
- Jeju Island: 33.4996, 126.5312

---

### 5. **Google Maps Satellite API**

**Provider:** Google  
**Website:** https://developers.google.com/maps

**Features:**
- ✅ Excellent global coverage including Korea
- ✅ Very high resolution in urban areas
- ⚠️ $200 free credit per month
- ⚠️ Requires billing account after free tier
- ⚠️ Stricter terms of service

---

## 🔧 Implementation Guide

### Option 1: Using VWorld (Recommended for Korea)

**Step 1:** Get your API key from VWorld (see above)

**Step 2:** Update `frontend/src/App.tsx`:

```typescript
// Replace the current TileLayer with:
<TileLayer
  attribution='© VWorld (Korean Ministry of Land, Infrastructure and Transport)'
  url={`https://api.vworld.kr/req/wmts/1.0.0/${process.env.REACT_APP_VWORLD_API_KEY}/Satellite/{z}/{y}/{x}.jpeg`}
  maxZoom={19}
/>
```

**Step 3:** Create `.env` file in `frontend/` directory:

```bash
REACT_APP_VWORLD_API_KEY=your_api_key_here
```

**Step 4:** Add to `.gitignore`:
```
.env
.env.local
```

---

### Option 2: Using Kakao Map

**Step 1:** Install dependencies:
```bash
cd frontend
npm install react-kakao-maps-sdk
```

**Step 2:** Update `App.tsx` to use Kakao Map instead of Leaflet:

```typescript
import { Map, MapMarker } from "react-kakao-maps-sdk";

// Replace MapContainer with:
<Map
  center={{ lat: 37.5665, lng: 126.9780 }}
  style={{ width: "100%", height: "100%" }}
  level={3}
  mapTypeId={kakao.maps.MapTypeId.HYBRID} // Satellite + labels
>
  {/* Your markers here */}
</Map>
```

---

### Option 3: Multiple Tile Layer Support

Add a tile layer selector to switch between different sources:

```typescript
const [tileSource, setTileSource] = useState<'esri' | 'vworld' | 'google'>('esri');

const getTileLayer = () => {
  switch (tileSource) {
    case 'vworld':
      return (
        <TileLayer
          url={`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_API_KEY}/Satellite/{z}/{y}/{x}.jpeg`}
          maxZoom={19}
        />
      );
    case 'google':
      return (
        <TileLayer
          url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          maxZoom={20}
        />
      );
    default:
      return (
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          maxZoom={19}
        />
      );
  }
};
```

---

## 🗺️ Recommended Test Locations in Korea

### Major Cities
```
Seoul (서울): 37.5665, 126.9780
Busan (부산): 35.1796, 129.0756
Incheon (인천): 37.4563, 126.7052
Daegu (대구): 35.8714, 128.6014
Daejeon (대전): 36.3504, 127.3845
Gwangju (광주): 35.1595, 126.8526
```

### Airports (Good for Vehicle Detection)
```
Incheon International Airport: 37.4602, 126.4407
Gimpo Airport: 37.5583, 126.7906
Gimhae International Airport: 35.1795, 128.9381
Jeju International Airport: 33.5113, 126.4931
```

### Ports (High Vehicle Density)
```
Busan Port: 35.1041, 129.0404
Incheon Port: 37.4661, 126.5921
Ulsan Port: 35.5047, 129.3865
```

### Large Parking Areas
```
COEX Convention Center: 37.5113, 127.0594
World Cup Stadium: 37.5683, 126.8973
Lotte World Tower: 37.5125, 127.1025
```

---

## 📊 Resolution Comparison

| Source | Resolution | Update Frequency | Coverage | Cost |
|--------|-----------|------------------|----------|------|
| **VWorld** | 0.5m - 1m | Quarterly | South Korea | FREE |
| **ESRI World Imagery** | 0.3m - 15m | Varies | Global | FREE |
| **Kakao Map** | 0.5m - 1m | Monthly | South Korea | FREE Tier |
| **Naver Map** | 0.5m - 1m | Monthly | South Korea | FREE Tier |
| **Sentinel-2** | 10m - 60m | 5 days | Global | FREE |
| **Google Maps** | 0.15m - 15m | Varies | Global | $7/1000 requests |

---

## 🚀 Quick Setup for VWorld

**1. Get API Key:**
```bash
# Visit https://www.vworld.kr/
# Sign up and get your API key (takes 5 minutes)
```

**2. Add to Environment:**
```bash
# frontend/.env
REACT_APP_VWORLD_API_KEY=your_key_here
```

**3. Update Code:**
```typescript
// frontend/src/App.tsx
const VWORLD_KEY = process.env.REACT_APP_VWORLD_API_KEY;

<TileLayer
  attribution='© VWorld'
  url={`https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Satellite/{z}/{y}/{x}.jpeg`}
  maxZoom={19}
/>
```

**4. Restart Dev Server:**
```bash
cd frontend
npm start
```

---

## 🔍 Data Quality Tips

### For Best Results:
1. **Urban Areas**: VWorld or Kakao (highest resolution)
2. **Rural Areas**: ESRI World Imagery (better coverage)
3. **Time-Series Analysis**: Sentinel Hub (historical data)
4. **Real-time Updates**: Kakao or Naver (updated monthly)

### Zoom Level Guidelines:
- **Level 13-14**: City overview
- **Level 15-16**: District/neighborhood (current default)
- **Level 17-18**: Street level (good for vehicle detection)
- **Level 19-20**: Individual vehicles clearly visible

---

## ⚖️ Legal Considerations

### VWorld Terms:
- ✅ FREE for personal/non-commercial projects
- ✅ FREE for educational purposes
- ⚠️ Commercial use requires separate agreement
- ✅ Attribution required

### Kakao/Naver Terms:
- ✅ Free tier available
- ⚠️ Must display provider logo
- ⚠️ Commercial use may require paid plan
- ✅ Attribution required

### ESRI World Imagery:
- ✅ FREE for most applications
- ✅ Attribution required
- ✅ No API key needed

---

## 🛠️ Troubleshooting

### VWorld API Not Working?
1. Check API key is correct
2. Verify key is not expired
3. Check if daily limit exceeded
4. Ensure proper attribution is displayed

### Poor Image Quality?
1. Increase zoom level (16-18 recommended)
2. Try different tile source
3. Check internet connection
4. Some areas may have lower resolution

### CORS Errors?
1. Add proxy in `package.json`:
   ```json
   "proxy": "http://localhost:5000"
   ```
2. Or use environment variable for API calls

---

## 📧 Support & Resources

**VWorld Support:**
- Email: vworldhelp@lx.or.kr
- FAQ: https://www.vworld.kr/dev/v4dv_2dmapapi2d_faq.do

**Kakao Developers:**
- Forum: https://devtalk.kakao.com/
- Docs: https://apis.map.kakao.com/

**Community:**
- GitHub Issues: [Your Repo]
- Korean GIS Community: https://cafe.naver.com/gisdeveloper

---

## 🎯 Next Steps

1. ✅ Currently using ESRI World Imagery (working)
2. 📝 Get VWorld API key for Korea-specific high-res imagery
3. 🔧 Add tile layer selector in UI
4. 📊 Test with real satellite images
5. 🚀 Deploy with proper API key management

---

**Current Status:** ✅ Application is configured with ESRI satellite imagery covering all of Korea with good resolution. You can now see actual satellite photos instead of street maps!

**For Enhanced Korea Coverage:** Follow the VWorld setup guide above to get even better resolution (0.5m vs 1-2m) and more recent imagery of Korean locations.


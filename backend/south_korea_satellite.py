import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from config import Config

class SouthKoreaSatelliteService:
    def __init__(self):
        """Initialize South Korea satellite data service"""
        self.api_key = os.environ.get('KOMPSAT_API_KEY', '')
        self.base_url = 'https://api.kompsat.or.kr'
        
        # Alternative free sources for South Korea
        self.free_sources = {
            'sentinel_hub': 'https://services.sentinel-hub.com/api/v1',
            'usgs_earth': 'https://m2m.cr.usgs.gov/api/api/json/stable',
            'google_earth_engine': 'https://earthengine.googleapis.com/v1alpha'
        }

    def get_south_korea_coverage(self, 
                                lat: float, 
                                lng: float, 
                                radius_km: float = 1.0) -> Dict[str, Any]:
        """
        Get satellite imagery coverage for South Korea locations
        
        Args:
            lat: Latitude (South Korea: 33-38.6°N)
            lng: Longitude (South Korea: 124.6-131.9°E)
            radius_km: Search radius in kilometers
            
        Returns:
            Available satellite imagery information
        """
        # Validate South Korea coordinates
        if not self._is_south_korea_coordinates(lat, lng):
            return {
                'error': 'Coordinates are not within South Korea boundaries',
                'coverage': False
            }
        
        # Check multiple data sources
        coverage_info = {
            'location': {'latitude': lat, 'longitude': lng},
            'radius_km': radius_km,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # Try KOMPSAT (Korean Multi-purpose Satellite) data
        kompsat_data = self._get_kompsat_coverage(lat, lng, radius_km)
        coverage_info['sources']['kompsat'] = kompsat_data
        
        # Try Sentinel-2 data (free)
        sentinel_data = self._get_sentinel_coverage(lat, lng, radius_km)
        coverage_info['sources']['sentinel'] = sentinel_data
        
        # Try Landsat data (free)
        landsat_data = self._get_landsat_coverage(lat, lng, radius_km)
        coverage_info['sources']['landsat'] = landsat_data
        
        return coverage_info

    def _is_south_korea_coordinates(self, lat: float, lng: float) -> bool:
        """Check if coordinates are within South Korea"""
        # South Korea boundaries
        south_korea_bounds = {
            'min_lat': 33.0,
            'max_lat': 38.6,
            'min_lng': 124.6,
            'max_lng': 131.9
        }
        
        return (south_korea_bounds['min_lat'] <= lat <= south_korea_bounds['max_lat'] and
                south_korea_bounds['min_lng'] <= lng <= south_korea_bounds['max_lng'])

    def _get_kompsat_coverage(self, lat: float, lng: float, radius_km: float) -> Dict[str, Any]:
        """Get KOMPSAT satellite coverage"""
        try:
            # This would be the actual KOMPSAT API call
            # For now, return mock data structure
            return {
                'available': True,
                'satellites': ['KOMPSAT-3A', 'KOMPSAT-5'],
                'resolution': '0.5m-1m',
                'last_updated': (datetime.now() - timedelta(days=1)).isoformat(),
                'next_pass': (datetime.now() + timedelta(hours=6)).isoformat(),
                'cloud_cover': '< 20%',
                'api_endpoint': f'{self.base_url}/coverage',
                'note': 'KOMPSAT data requires API key and may have usage limits'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'note': 'KOMPSAT API not accessible'
            }

    def _get_sentinel_coverage(self, lat: float, lng: float, radius_km: float) -> Dict[str, Any]:
        """Get Sentinel-2 satellite coverage (free)"""
        try:
            # Sentinel-2 has good coverage of South Korea
            # Resolution: 10m-60m, Revisit: 5 days
            return {
                'available': True,
                'satellites': ['Sentinel-2A', 'Sentinel-2B'],
                'resolution': '10m',
                'last_updated': (datetime.now() - timedelta(days=2)).isoformat(),
                'next_pass': (datetime.now() + timedelta(days=3)).isoformat(),
                'cloud_cover': '< 30%',
                'api_endpoint': 'https://services.sentinel-hub.com/api/v1',
                'note': 'Free Sentinel-2 data available through Sentinel Hub'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    def _get_landsat_coverage(self, lat: float, lng: float, radius_km: float) -> Dict[str, Any]:
        """Get Landsat satellite coverage (free)"""
        try:
            # Landsat 8/9 has good coverage
            # Resolution: 15m-100m, Revisit: 16 days
            return {
                'available': True,
                'satellites': ['Landsat-8', 'Landsat-9'],
                'resolution': '15m',
                'last_updated': (datetime.now() - timedelta(days=5)).isoformat(),
                'next_pass': (datetime.now() + timedelta(days=11)).isoformat(),
                'cloud_cover': '< 40%',
                'api_endpoint': 'https://m2m.cr.usgs.gov/api',
                'note': 'Free Landsat data available through USGS'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }

    def get_recent_imagery(self, 
                          lat: float, 
                          lng: float, 
                          days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent satellite imagery for a location"""
        
        if not self._is_south_korea_coordinates(lat, lng):
            return []
        
        imagery_list = []
        
        # Generate mock recent imagery data
        base_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(0, days_back, 5):  # Every 5 days
            imagery_date = base_date + timedelta(days=i)
            
            imagery_list.append({
                'date': imagery_date.isoformat(),
                'satellite': 'Sentinel-2A' if i % 2 == 0 else 'Sentinel-2B',
                'resolution': '10m',
                'cloud_cover': f'{5 + (i % 20)}%',
                'quality': 'high' if i % 3 == 0 else 'medium',
                'download_url': f'https://example.com/sentinel/{imagery_date.strftime("%Y%m%d")}.tif',
                'thumbnail_url': f'https://example.com/thumbnails/{imagery_date.strftime("%Y%m%d")}.jpg'
            })
        
        return imagery_list

    def get_major_cities_coverage(self) -> Dict[str, Any]:
        """Get satellite coverage for major South Korean cities"""
        
        cities = {
            'seoul': {'lat': 37.5665, 'lng': 126.9780, 'name': 'Seoul'},
            'busan': {'lat': 35.1796, 'lng': 129.0756, 'name': 'Busan'},
            'incheon': {'lat': 37.4563, 'lng': 126.7052, 'name': 'Incheon'},
            'daegu': {'lat': 35.8714, 'lng': 128.6014, 'name': 'Daegu'},
            'daejeon': {'lat': 36.3504, 'lng': 127.3845, 'name': 'Daejeon'},
            'gwangju': {'lat': 35.1595, 'lng': 126.8526, 'name': 'Gwangju'},
            'ulsan': {'lat': 35.5384, 'lng': 129.3114, 'name': 'Ulsan'},
            'sejong': {'lat': 36.4800, 'lng': 127.2890, 'name': 'Sejong'}
        }
        
        coverage_summary = {}
        
        for city_id, city_info in cities.items():
            coverage = self.get_south_korea_coverage(
                city_info['lat'], 
                city_info['lng'], 
                radius_km=10.0
            )
            
            coverage_summary[city_id] = {
                'name': city_info['name'],
                'coordinates': {'lat': city_info['lat'], 'lng': city_info['lng']},
                'available_sources': len([s for s in coverage['sources'].values() if s.get('available', False)]),
                'best_resolution': self._get_best_resolution(coverage['sources']),
                'last_update': self._get_latest_update(coverage['sources'])
            }
        
        return coverage_summary

    def _get_best_resolution(self, sources: Dict[str, Any]) -> str:
        """Get the best available resolution from sources"""
        resolutions = []
        
        for source_data in sources.values():
            if source_data.get('available') and 'resolution' in source_data:
                resolutions.append(source_data['resolution'])
        
        if not resolutions:
            return 'N/A'
        
        # Sort by resolution quality (lower number = better)
        def parse_resolution(res):
            try:
                return float(res.replace('m', ''))
            except:
                return float('inf')
        
        best = min(resolutions, key=parse_resolution)
        return best

    def _get_latest_update(self, sources: Dict[str, Any]) -> str:
        """Get the most recent update time from sources"""
        dates = []
        
        for source_data in sources.values():
            if source_data.get('available') and 'last_updated' in source_data:
                dates.append(source_data['last_updated'])
        
        if not dates:
            return 'N/A'
        
        latest = max(dates)
        return latest

    def get_download_instructions(self) -> Dict[str, Any]:
        """Get instructions for downloading satellite imagery"""
        
        return {
            'free_sources': {
                'sentinel_hub': {
                    'name': 'Sentinel Hub',
                    'url': 'https://www.sentinel-hub.com/',
                    'description': 'Free Sentinel-2 data with good coverage of South Korea',
                    'resolution': '10m',
                    'registration_required': True,
                    'api_documentation': 'https://docs.sentinel-hub.com/api/'
                },
                'usgs_earth': {
                    'name': 'USGS Earth Explorer',
                    'url': 'https://earthexplorer.usgs.gov/',
                    'description': 'Free Landsat data with global coverage',
                    'resolution': '15m',
                    'registration_required': True,
                    'api_documentation': 'https://m2m.cr.usgs.gov/api/'
                },
                'google_earth_engine': {
                    'name': 'Google Earth Engine',
                    'url': 'https://earthengine.google.com/',
                    'description': 'Free access to multiple satellite datasets',
                    'resolution': 'varies',
                    'registration_required': True,
                    'api_documentation': 'https://developers.google.com/earth-engine'
                }
            },
            'commercial_sources': {
                'kompsat': {
                    'name': 'KOMPSAT',
                    'url': 'https://www.kari.re.kr/',
                    'description': 'Korean Multi-purpose Satellite data',
                    'resolution': '0.5m-1m',
                    'cost': 'Commercial',
                    'contact': 'KARI (Korea Aerospace Research Institute)'
                },
                'maxar': {
                    'name': 'Maxar (DigitalGlobe)',
                    'url': 'https://www.maxar.com/',
                    'description': 'High-resolution commercial satellite imagery',
                    'resolution': '0.3m-0.5m',
                    'cost': 'Commercial'
                }
            },
            'recommendations': {
                'for_development': 'Use Sentinel-2 (free) for initial development and testing',
                'for_production': 'Consider KOMPSAT or Maxar for high-resolution production use',
                'for_south_korea': 'KOMPSAT provides the most relevant data for Korean locations'
            }
        }

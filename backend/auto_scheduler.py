"""
자동 방치 차량 분석 스케줄러
12시간마다 (0시, 12시) 전국 방치 차량 분석 실행
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from abandoned_vehicle_detector import AbandonedVehicleDetector
from ngii_api_service import NGIIAPIService
from database import SessionLocal, engine
from models import AbandonedVehicle, Base

# 로거 설정
logger = logging.getLogger(__name__)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)


class AbandonedVehicleScheduler:
    """방치 차량 자동 분석 스케줄러"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.detector = AbandonedVehicleDetector(similarity_threshold=0.90)
        self.ngii_service = NGIIAPIService()
        self.is_running = False

    async def analyze_abandoned_vehicles(self):
        """
        전국 방치 차량 분석 실행
        - 주요 도시들의 주차장 영역을 분석
        - 결과를 DB에 저장
        """
        logger.info("🚗 자동 방치 차량 분석 시작")

        db: Session = SessionLocal()
        try:
            # 주요 분석 대상 지역 (전국 주요 도시)
            target_cities = [
                {"city": "서울특별시", "district": "강남구"},
                {"city": "서울특별시", "district": "강북구"},
                {"city": "부산광역시", "district": "해운대구"},
                {"city": "대구광역시", "district": "중구"},
                {"city": "인천광역시", "district": "남동구"},
                {"city": "광주광역시", "district": "동구"},
                {"city": "대전광역시", "district": "서구"},
                {"city": "울산광역시", "district": "남구"},
                {"city": "세종특별자치시", "district": None},
                {"city": "경기도", "district": "수원시"},
                {"city": "경기도", "district": "성남시"},
                {"city": "경기도", "district": "고양시"},
                {"city": "강원특별자치도", "district": "춘천시"},
                {"city": "충청북도", "district": "청주시"},
                {"city": "충청남도", "district": "천안시"},
                {"city": "전북특별자치도", "district": "전주시"},
                {"city": "전라남도", "district": "나주시"},
                {"city": "경상북도", "district": "포항시"},
                {"city": "경상남도", "district": "창원시"},
                {"city": "제주특별자치도", "district": "제주시"},
            ]

            total_found = 0
            total_analyzed = 0

            for location in target_cities:
                city = location["city"]
                district = location["district"]
                location_name = f"{city} {district}" if district else city

                logger.info(f"📍 {location_name} 분석 중...")

                try:
                    # NGII API를 통해 해당 지역의 항공 사진 좌표 가져오기
                    # (실제로는 주차장 위치 DB가 필요하지만, 여기서는 샘플로 중심 좌표 사용)
                    coordinates = await self.ngii_service.get_city_center_coords(city, district)

                    if not coordinates:
                        logger.warning(f"⚠️  {location_name} 좌표를 찾을 수 없습니다")
                        continue

                    # 해당 지역 주변 주차장 분석 (샘플: 1km 반경)
                    # 실제로는 parking_lot DB에서 해당 지역의 주차장들을 조회해야 함
                    analysis_result = await self.analyze_region(
                        lat=coordinates['lat'],
                        lon=coordinates['lon'],
                        city=city,
                        district=district,
                        db=db
                    )

                    total_found += analysis_result['found']
                    total_analyzed += analysis_result['analyzed']

                except Exception as e:
                    logger.error(f"❌ {location_name} 분석 실패: {e}")
                    continue

            logger.info(f"✅ 분석 완료: 총 {total_analyzed}개 구역 분석, {total_found}대 방치 차량 발견")

        except Exception as e:
            logger.error(f"❌ 자동 분석 실패: {e}")
        finally:
            db.close()

    async def analyze_region(self, lat: float, lon: float, city: str, district: str, db: Session) -> dict:
        """
        특정 지역의 방치 차량 분석

        Args:
            lat: 위도
            lon: 경도
            city: 시/도
            district: 시/군/구
            db: DB 세션

        Returns:
            분석 결과 (발견된 차량 수, 분석된 구역 수)
        """
        found_count = 0
        analyzed_count = 0

        try:
            # 샘플: 해당 좌표 주변 100m x 100m 영역을 분석
            # 실제로는 주차장 폴리곤 좌표를 사용해야 함

            # 2023년과 2024년 항공 사진 가져오기 (NGII API)
            image_2023 = await self.ngii_service.get_aerial_image(lat, lon, year=2023)
            image_2024 = await self.ngii_service.get_aerial_image(lat, lon, year=2024)

            if image_2023 is None or image_2024 is None:
                logger.warning(f"⚠️  항공 사진을 가져올 수 없습니다: {city} {district}")
                return {'found': 0, 'analyzed': 0}

            # 방치 차량 탐지
            results = self.detector.detect_abandoned_vehicles(
                image_year1=image_2023,
                image_year2=image_2024,
                year1=2023,
                year2=2024
            )

            analyzed_count = 1

            # 방치 차량이 발견되면 DB에 저장
            if results and len(results) > 0:
                for result in results:
                    # 중복 체크 (같은 위치의 차량)
                    existing = db.query(AbandonedVehicle).filter(
                        AbandonedVehicle.latitude == result['lat'],
                        AbandonedVehicle.longitude == result['lon']
                    ).first()

                    if existing:
                        # 기존 레코드 업데이트
                        existing.similarity_score = result['similarity']
                        existing.risk_level = result['risk_level']
                        existing.last_detected = datetime.now()
                        existing.detection_count += 1
                    else:
                        # 새로운 방치 차량 추가
                        new_vehicle = AbandonedVehicle(
                            vehicle_id=f"AV_{datetime.now().strftime('%Y%m%d%H%M%S')}_{found_count}",
                            latitude=result['lat'],
                            longitude=result['lon'],
                            city=city,
                            district=district,
                            address=f"{city} {district}",
                            similarity_score=result['similarity'],
                            risk_level=result['risk_level'],
                            year_from=2023,
                            year_to=2024,
                            first_detected=datetime.now(),
                            last_detected=datetime.now(),
                            detection_count=1,
                            status='detected',
                            verification_status='pending',
                            cctv_verified=False
                        )
                        db.add(new_vehicle)
                        found_count += 1

                db.commit()
                logger.info(f"✅ {city} {district}: {found_count}대 방치 차량 발견")

        except Exception as e:
            logger.error(f"❌ 지역 분석 실패 ({city} {district}): {e}")
            db.rollback()

        return {'found': found_count, 'analyzed': analyzed_count}

    def start(self):
        """스케줄러 시작 (매일 0시, 12시 실행)"""
        if self.is_running:
            logger.warning("⚠️  스케줄러가 이미 실행 중입니다")
            return

        # 매일 0시에 실행
        self.scheduler.add_job(
            self.analyze_abandoned_vehicles,
            trigger=CronTrigger(hour=0, minute=0),
            id='analysis_midnight',
            name='방치차량 분석 (0시)',
            replace_existing=True
        )

        # 매일 12시에 실행
        self.scheduler.add_job(
            self.analyze_abandoned_vehicles,
            trigger=CronTrigger(hour=12, minute=0),
            id='analysis_noon',
            name='방치차량 분석 (12시)',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("✅ 자동 분석 스케줄러 시작됨 (매일 0시, 12시 실행)")

    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("⏹️  자동 분석 스케줄러 중지됨")

    def run_now(self):
        """즉시 분석 실행 (테스트용)"""
        logger.info("▶️  수동 분석 실행")
        asyncio.create_task(self.analyze_abandoned_vehicles())


# 싱글톤 인스턴스
_scheduler_instance = None

def get_scheduler() -> AbandonedVehicleScheduler:
    """스케줄러 싱글톤 인스턴스 반환"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AbandonedVehicleScheduler()
    return _scheduler_instance

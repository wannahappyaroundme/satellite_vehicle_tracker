"""
보안 모듈: Rate Limiting, 입력 검증, 데이터 보호
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from fastapi import Request, HTTPException, status
import bleach


# Rate Limiting 저장소 (프로덕션에서는 Redis 사용 권장)
class RateLimiter:
    """
    Rate Limiting 구현
    """

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}

    def is_rate_limited(
        self,
        client_id: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Rate limit 확인

        Args:
            client_id: 클라이언트 식별자 (IP 주소 등)
            max_requests: 윈도우 내 최대 요청 수
            window_seconds: 시간 윈도우 (초)

        Returns:
            True면 차단, False면 허용
        """
        # IP 차단 확인
        if client_id in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[client_id]:
                return True
            else:
                del self.blocked_ips[client_id]

        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)

        # 오래된 요청 제거
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]

        # Rate limit 확인
        if len(self.requests[client_id]) >= max_requests:
            # 차단 (5분)
            self.blocked_ips[client_id] = now + timedelta(minutes=5)
            return True

        # 요청 기록
        self.requests[client_id].append(now)
        return False

    def clear_old_entries(self, max_age_hours: int = 1):
        """
        오래된 항목 정리
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

        # 오래된 요청 기록 삭제
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff
            ]
            if not self.requests[client_id]:
                del self.requests[client_id]

        # 만료된 차단 해제
        for client_id in list(self.blocked_ips.keys()):
            if datetime.utcnow() > self.blocked_ips[client_id]:
                del self.blocked_ips[client_id]


# 전역 rate limiter 인스턴스
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Rate limiting 데코레이터

    Usage:
        @app.get("/api/endpoint")
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"

            if rate_limiter.is_rate_limited(client_ip, max_requests, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "error_ko": "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
                        "retry_after_seconds": 300
                    }
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# 입력 검증
class InputValidator:
    """
    입력 데이터 검증 및 새니타이징
    """

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """
        좌표 검증

        Args:
            latitude: 위도 (-90 ~ 90)
            longitude: 경도 (-180 ~ 180)

        Returns:
            유효하면 True
        """
        return -90 <= latitude <= 90 and -180 <= longitude <= 180

    @staticmethod
    def validate_korean_address(address: str) -> bool:
        """
        한국 주소 형식 검증
        """
        if not address or len(address) > 200:
            return False

        # 한글, 숫자, 공백, 일부 특수문자만 허용
        pattern = r'^[가-힣a-zA-Z0-9\s\-,().]*$'
        return bool(re.match(pattern, address))

    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """
        문자열 새니타이징 (XSS 방지)

        Args:
            text: 입력 문자열
            max_length: 최대 길이

        Returns:
            새니타이징된 문자열
        """
        if not text:
            return ""

        # 길이 제한
        text = text[:max_length]

        # HTML 태그 제거
        text = bleach.clean(text, tags=[], strip=True)

        # 위험한 문자 이스케이프
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        return text.strip()

    @staticmethod
    def validate_vehicle_id(vehicle_id: str) -> bool:
        """
        차량 ID 형식 검증
        """
        if not vehicle_id or len(vehicle_id) > 100:
            return False

        # 영숫자, 하이픈, 언더스코어만 허용
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, vehicle_id))

    @staticmethod
    def validate_risk_level(risk_level: str) -> bool:
        """
        위험도 레벨 검증
        """
        valid_levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        return risk_level in valid_levels

    @staticmethod
    def validate_vehicle_type(vehicle_type: str) -> bool:
        """
        차량 타입 검증
        """
        valid_types = ['car', 'truck', 'bus']
        return vehicle_type in valid_types


# 데이터 보호
class DataProtection:
    """
    민감한 데이터 보호 (해싱, 암호화)
    """

    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
        """
        민감한 데이터 해싱 (SHA-256)

        Args:
            data: 해싱할 데이터
            salt: 솔트 (없으면 자동 생성)

        Returns:
            해시값 (hex)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hash_obj = hashlib.sha256()
        hash_obj.update(f"{salt}{data}".encode('utf-8'))

        return f"{salt}:{hash_obj.hexdigest()}"

    @staticmethod
    def verify_hash(data: str, hashed: str) -> bool:
        """
        해시 검증

        Args:
            data: 원본 데이터
            hashed: 해시값 (salt:hash 형식)

        Returns:
            일치하면 True
        """
        try:
            salt, hash_value = hashed.split(':', 1)
            computed_hash = DataProtection.hash_sensitive_data(data, salt)
            return computed_hash == hashed
        except:
            return False

    @staticmethod
    def mask_email(email: str) -> str:
        """
        이메일 마스킹 (로그에 기록 시)

        Args:
            email: 이메일 주소

        Returns:
            마스킹된 이메일 (예: b***@hanyang.ac.kr)
        """
        if not email or '@' not in email:
            return "***@***.***"

        local, domain = email.split('@', 1)

        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        전화번호 마스킹

        Args:
            phone: 전화번호

        Returns:
            마스킹된 전화번호 (예: 010-****-5119)
        """
        if not phone or len(phone) < 4:
            return "***-****-****"

        # 숫자만 추출
        digits = re.sub(r'\D', '', phone)

        if len(digits) >= 11:
            return f"{digits[:3]}-****-{digits[-4:]}"
        elif len(digits) >= 8:
            return f"{digits[:3]}-****-{digits[-4:]}"
        else:
            return "***-****-****"


# SQL Injection 방지
class SQLSafetyChecker:
    """
    SQL Injection 패턴 감지
    """

    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--|#|\/\*|\*\/)",  # SQL 주석
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*--)",
    ]

    @staticmethod
    def is_sql_injection(text: str) -> bool:
        """
        SQL Injection 패턴 감지

        Args:
            text: 검사할 텍스트

        Returns:
            의심스러우면 True
        """
        if not text:
            return False

        text_upper = text.upper()

        for pattern in SQLSafetyChecker.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True

        return False


# CORS 헤더 검증
def validate_origin(origin: Optional[str], allowed_origins: list) -> bool:
    """
    CORS Origin 검증

    Args:
        origin: 요청 Origin
        allowed_origins: 허용된 Origin 리스트

    Returns:
        허용되면 True
    """
    if not origin:
        return False

    # 완전 일치
    if origin in allowed_origins:
        return True

    # 와일드카드 매칭
    for allowed in allowed_origins:
        if allowed == "*":
            return True

        # 패턴 매칭 (예: *.example.com)
        if allowed.startswith("*."):
            domain = allowed[2:]
            if origin.endswith(domain):
                return True

    return False


# 입력 검증 데코레이터
validator = InputValidator()
data_protector = DataProtection()
sql_checker = SQLSafetyChecker()

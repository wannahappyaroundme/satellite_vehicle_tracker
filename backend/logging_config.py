"""
구조화된 로깅 시스템
JSON 형식으로 로그 기록 + 성능 모니터링
"""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import traceback
import sys

class JSONFormatter(logging.Formatter):
    """
    JSON 형식으로 로그를 출력하는 Formatter
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # 추가 필드가 있으면 포함
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # 예외 정보가 있으면 포함
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data, ensure_ascii=False)


class PerformanceLogger:
    """
    성능 모니터링을 위한 로거
    """

    def __init__(self, logger_name: str = 'performance'):
        self.logger = logging.getLogger(logger_name)

    def log_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        request_size: int = 0,
        response_size: int = 0,
        user_id: Optional[str] = None
    ):
        """
        API 요청 로깅
        """
        self.logger.info(
            f"{method} {endpoint}",
            extra={
                'extra_fields': {
                    'type': 'api_request',
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'duration_ms': round(duration_ms, 2),
                    'request_size_bytes': request_size,
                    'response_size_bytes': response_size,
                    'user_id': user_id
                }
            }
        )

    def log_analysis(
        self,
        analysis_type: str,
        vehicle_count: int,
        processing_time_ms: float,
        image_size: Optional[tuple] = None,
        success: bool = True
    ):
        """
        방치 차량 분석 로깅
        """
        self.logger.info(
            f"Analysis completed: {analysis_type}",
            extra={
                'extra_fields': {
                    'type': 'vehicle_analysis',
                    'analysis_type': analysis_type,
                    'vehicle_count': vehicle_count,
                    'processing_time_ms': round(processing_time_ms, 2),
                    'image_size': f"{image_size[0]}x{image_size[1]}" if image_size else None,
                    'success': success
                }
            }
        )

    def log_cache_hit(self, cache_key: str, hit: bool):
        """
        캐시 히트/미스 로깅
        """
        self.logger.debug(
            f"Cache {'HIT' if hit else 'MISS'}: {cache_key}",
            extra={
                'extra_fields': {
                    'type': 'cache',
                    'cache_key': cache_key,
                    'hit': hit
                }
            }
        )

    def log_database(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        rows_affected: int = 0
    ):
        """
        데이터베이스 작업 로깅
        """
        self.logger.info(
            f"DB {operation}: {table}",
            extra={
                'extra_fields': {
                    'type': 'database',
                    'operation': operation,
                    'table': table,
                    'duration_ms': round(duration_ms, 2),
                    'rows_affected': rows_affected
                }
            }
        )


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    json_format: bool = True
):
    """
    로깅 시스템 초기화

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 콘솔만)
        json_format: JSON 형식 사용 여부
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 기존 핸들러 제거
    root_logger.handlers = []

    # 포맷터 생성
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (옵션)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def log_performance(logger_name: str = 'performance'):
    """
    함수 실행 시간을 자동으로 로깅하는 데코레이터

    Usage:
        @log_performance()
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            perf_logger = PerformanceLogger(logger_name)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                perf_logger.logger.info(
                    f"Function executed: {func.__name__}",
                    extra={
                        'extra_fields': {
                            'type': 'function_performance',
                            'function': func.__name__,
                            'duration_ms': round(duration_ms, 2),
                            'success': True
                        }
                    }
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                perf_logger.logger.error(
                    f"Function failed: {func.__name__}",
                    exc_info=True,
                    extra={
                        'extra_fields': {
                            'type': 'function_performance',
                            'function': func.__name__,
                            'duration_ms': round(duration_ms, 2),
                            'success': False,
                            'error': str(e)
                        }
                    }
                )

                raise

        return wrapper
    return decorator


# 보안 감사 로거
class SecurityLogger:
    """
    보안 관련 이벤트 로깅
    """

    def __init__(self, logger_name: str = 'security'):
        self.logger = logging.getLogger(logger_name)

    def log_auth_attempt(
        self,
        user_id: Optional[str],
        ip_address: str,
        success: bool,
        reason: Optional[str] = None
    ):
        """
        인증 시도 로깅
        """
        level = logging.INFO if success else logging.WARNING

        self.logger.log(
            level,
            f"Authentication {'success' if success else 'failed'}: {user_id or 'unknown'}",
            extra={
                'extra_fields': {
                    'type': 'authentication',
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'success': success,
                    'reason': reason
                }
            }
        )

    def log_rate_limit(
        self,
        ip_address: str,
        endpoint: str,
        limit: int
    ):
        """
        Rate limiting 이벤트 로깅
        """
        self.logger.warning(
            f"Rate limit exceeded: {ip_address} -> {endpoint}",
            extra={
                'extra_fields': {
                    'type': 'rate_limit',
                    'ip_address': ip_address,
                    'endpoint': endpoint,
                    'limit': limit
                }
            }
        )

    def log_suspicious_activity(
        self,
        ip_address: str,
        activity: str,
        details: Dict[str, Any]
    ):
        """
        의심스러운 활동 로깅
        """
        self.logger.warning(
            f"Suspicious activity detected: {activity}",
            extra={
                'extra_fields': {
                    'type': 'suspicious_activity',
                    'ip_address': ip_address,
                    'activity': activity,
                    'details': details
                }
            }
        )


# 전역 로거 인스턴스
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()

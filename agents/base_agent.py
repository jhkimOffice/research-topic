"""
Base Agent 클래스
모든 에이전트의 기본 인터페이스를 정의
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

    @abstractmethod
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        에이전트의 주요 실행 로직

        Args:
            input_data: 에이전트에 전달되는 입력 데이터

        Returns:
            Dict[str, Any]: 에이전트 실행 결과
        """
        pass

    def log_info(self, message: str):
        """정보 로그 출력"""
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """에러 로그 출력"""
        self.logger.error(f"[{self.name}] {message}")

    def log_warning(self, message: str):
        """경고 로그 출력"""
        self.logger.warning(f"[{self.name}] {message}")

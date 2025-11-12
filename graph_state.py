"""
LangGraph State Definition
연구 시스템의 전체 workflow 상태를 정의
"""
from typing import TypedDict, List, Tuple, Dict, Any, Optional
from typing_extensions import Annotated
import operator


def merge_metadata(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """메타데이터를 병합하는 커스텀 reducer"""
    return {**left, **right}


class ResearchState(TypedDict):
    """연구 시스템의 전체 상태"""

    # 입력 데이터
    urls: List[str]  # 크롤링할 URL 목록
    query_keywords: List[Tuple[str, str]]  # [(키워드, 설명), ...]

    # 설정
    config: Dict[str, Any]  # 시스템 설정

    # 중간 단계 데이터
    crawled_data: Optional[Dict[str, Dict]]  # 크롤링된 데이터
    filtered_data: Optional[Dict[str, Dict]]  # 필터링된 데이터
    groups: Optional[List[Dict]]  # 그룹화된 요약 결과

    # 출력
    report_path: Optional[str]  # 생성된 보고서 경로

    # 메타데이터
    metadata: Annotated[Dict[str, Any], merge_metadata]  # 실행 메타데이터

    # 에러 처리
    errors: Annotated[List[str], operator.add]  # 발생한 에러 목록
    success: bool  # 전체 실행 성공 여부

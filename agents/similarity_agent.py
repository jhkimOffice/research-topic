"""
Similarity Agent
키워드와 설명을 기반으로 수집된 콘텐츠의 유사도를 계산하고 필터링
"""
from typing import Dict, List, Any, Tuple
from agents.base_agent import BaseAgent
import re


class SimilarityAgent(BaseAgent):
    """유사도 계산 에이전트"""

    def __init__(self, similarity_threshold: float = 0.3, use_transformer: bool = False):
        super().__init__("SimilarityAgent")
        self.similarity_threshold = similarity_threshold
        self.use_transformer = use_transformer
        self.model = None

        if use_transformer:
            try:
                from sentence_transformers import SentenceTransformer, util
                self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                self.util = util
                self.log_info("Sentence Transformer 모델 로드 완료")
            except ImportError:
                self.log_warning("sentence-transformers 미설치. TF-IDF 기반 유사도 사용")
                self.use_transformer = False

    def execute(self, input_data: Dict) -> Dict[str, Any]:
        """
        유사도 계산 및 필터링 실행

        Args:
            input_data: {
                'crawled_data': Dict[str, Dict],  # 크롤링된 데이터
                'query_keywords': List[Tuple[str, str]]  # [(키워드, 설명), ...]
            }

        Returns:
            Dict[str, Any]: {
                'success': bool,
                'filtered_data': Dict[str, Dict],  # 필터링된 데이터
                'similarity_scores': Dict[str, float]  # URL별 유사도 점수
            }
        """
        crawled_data = input_data.get('crawled_data', {})
        query_keywords = input_data.get('query_keywords', [])

        self.log_info(f"유사도 분석 시작 - 페이지: {len(crawled_data)}, 쿼리: {len(query_keywords)}")

        if not crawled_data:
            return {'success': False, 'filtered_data': {}, 'similarity_scores': {}}

        # 쿼리 텍스트 생성
        query_text = self._build_query_text(query_keywords)
        self.log_info(f"쿼리 텍스트: {query_text[:200]}...")

        # 유사도 계산
        similarity_scores = {}

        if self.use_transformer:
            similarity_scores = self._calculate_transformer_similarity(crawled_data, query_text)
        else:
            similarity_scores = self._calculate_keyword_similarity(crawled_data, query_keywords)

        # 필터링
        filtered_data = self._filter_by_similarity(crawled_data, similarity_scores)

        self.log_info(f"유사도 분석 완료 - 선택된 페이지: {len(filtered_data)}/{len(crawled_data)}")

        return {
            'success': True,
            'filtered_data': filtered_data,
            'similarity_scores': similarity_scores,
            'total_filtered': len(filtered_data)
        }

    def _build_query_text(self, query_keywords: List[Tuple[str, str]]) -> str:
        """쿼리 키워드와 설명을 조합하여 텍스트 생성"""
        query_parts = []
        for keyword, description in query_keywords:
            query_parts.append(f"{keyword}: {description}")
        return " ".join(query_parts)

    def _calculate_transformer_similarity(self, crawled_data: Dict, query_text: str) -> Dict[str, float]:
        """Transformer 모델을 사용한 의미적 유사도 계산"""
        self.log_info("Transformer 기반 유사도 계산 중...")

        query_embedding = self.model.encode(query_text, convert_to_tensor=True)
        similarity_scores = {}

        for url, data in crawled_data.items():
            doc_text = f"{data.get('title', '')} {data.get('content', '')}"
            doc_embedding = self.model.encode(doc_text, convert_to_tensor=True)

            similarity = self.util.cos_sim(query_embedding, doc_embedding).item()
            similarity_scores[url] = float(similarity)

        return similarity_scores

    def _calculate_keyword_similarity(self, crawled_data: Dict, query_keywords: List[Tuple[str, str]]) -> Dict[str, float]:
        """키워드 기반 유사도 계산 (단순 매칭)"""
        self.log_info("키워드 기반 유사도 계산 중...")

        similarity_scores = {}

        # 모든 키워드와 설명 단어 추출
        all_keywords = []
        for keyword, description in query_keywords:
            all_keywords.append(keyword.lower())
            # 설명에서 의미있는 단어 추출
            desc_words = re.findall(r'\b\w{2,}\b', description.lower())
            all_keywords.extend(desc_words)

        all_keywords = list(set(all_keywords))  # 중복 제거

        for url, data in crawled_data.items():
            doc_text = f"{data.get('title', '')} {data.get('content', '')}".lower()

            # 키워드 매칭 점수 계산
            match_count = 0
            weighted_score = 0.0

            for kw in all_keywords:
                count = doc_text.count(kw)
                if count > 0:
                    match_count += 1
                    # TF (Term Frequency) 계산
                    tf = count / max(len(doc_text.split()), 1)
                    weighted_score += tf * 100

            # 정규화
            if all_keywords:
                coverage = match_count / len(all_keywords)
                final_score = (coverage * 0.6) + (min(weighted_score, 1.0) * 0.4)
                similarity_scores[url] = float(final_score)
            else:
                similarity_scores[url] = 0.0

        return similarity_scores

    def _filter_by_similarity(self, crawled_data: Dict, similarity_scores: Dict[str, float]) -> Dict[str, Dict]:
        """유사도 점수를 기반으로 데이터 필터링"""
        filtered_data = {}

        for url, data in crawled_data.items():
            score = similarity_scores.get(url, 0.0)
            if score >= self.similarity_threshold:
                filtered_data[url] = {
                    **data,
                    'similarity_score': score
                }

        # 유사도 점수로 정렬
        filtered_data = dict(sorted(
            filtered_data.items(),
            key=lambda x: x[1].get('similarity_score', 0),
            reverse=True
        ))

        return filtered_data

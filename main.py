"""
Multi-Agent Research System with LangGraph
메인 실행 파일
"""
import bootstrap_env
import sys
import argparse
from config import Config
from utils import read_urls_from_file, read_keywords_from_file, validate_inputs
from graph_workflow import run_research_workflow, visualize_graph


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='Multi-Agent Research System')
    parser.add_argument(
        '--urls',
        type=str,
        default=Config.URLS_FILE,
        help=f'URL 목록 파일 경로 (기본값: {Config.URLS_FILE})'
    )
    parser.add_argument(
        '--keywords',
        type=str,
        default=Config.KEYWORDS_FILE,
        help=f'키워드 목록 파일 경로 (기본값: {Config.KEYWORDS_FILE})'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=Config.CRAWLER_MAX_DEPTH,
        help=f'크롤링 깊이 (기본값: {Config.CRAWLER_MAX_DEPTH})'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=Config.CRAWLER_MAX_PAGES,
        help=f'최대 페이지 수 (기본값: {Config.CRAWLER_MAX_PAGES})'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=Config.SIMILARITY_THRESHOLD,
        help=f'유사도 임계값 (기본값: {Config.SIMILARITY_THRESHOLD})'
    )
    parser.add_argument(
        '--use-transformer',
        action='store_true',
        help='Transformer 모델 사용 (느리지만 정확함)'
    )
    parser.add_argument(
        '--use-llm',
        action='store_true',
        default=Config.USE_LLM,
        help='LLM 요약 사용 (OpenAI API 키 필요)'
    )
    parser.add_argument(
        '--prefer-lang',
        type=str,
        default=Config.PREFER_LANG,
        help='요약 언어 (기본값: {Config.PREFER_LANG})'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='LangGraph workflow 시각화 (Mermaid diagram 출력)'
    )

    args = parser.parse_args()

    # 설정 업데이트
    Config.URLS_FILE = args.urls
    Config.KEYWORDS_FILE = args.keywords
    Config.CRAWLER_MAX_DEPTH = args.depth
    Config.CRAWLER_MAX_PAGES = args.max_pages
    Config.SIMILARITY_THRESHOLD = args.threshold
    Config.USE_TRANSFORMER = args.use_transformer
    Config.USE_LLM = args.use_llm

    # 설정 출력
    Config.print_config()

    # Graph 시각화 (옵션)
    if args.visualize:
        print("\n" + "=" * 80)
        print("LangGraph Workflow 구조")
        print("=" * 80)
        visualize_graph()
        print("=" * 80 + "\n")

    try:
        # 입력 파일 읽기
        print("입력 파일 로드 중...")
        urls = read_urls_from_file(Config.URLS_FILE)
        keywords = read_keywords_from_file(Config.KEYWORDS_FILE)

        # 입력 유효성 검사
        validate_inputs(urls, keywords)

        print(f"\n로드된 URL 목록:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")

        print(f"\n로드된 키워드:")
        for keyword, description in keywords:
            print(f"  - {keyword}: {description}")

        # LangGraph Workflow 실행
        print("\n\nLangGraph Workflow 시작...")
        result = run_research_workflow(
            urls=urls,
            query_keywords=keywords,
            config=Config.to_dict()
        )

        # 결과 출력
        if result.get('success'):
            print("\n\n" + "=" * 80)
            print("실행 성공!")
            print("=" * 80)
            print(f"\n보고서 경로: {result.get('report_path')}")

            metadata = result.get('metadata', {})
            print(f"\n통계:")
            print(f"  - 분석 URL: {metadata.get('total_urls', len(urls))}개")
            print(f"  - 크롤링된 페이지: {metadata.get('crawled_pages', 0)}개")
            print(f"  - 필터링된 페이지: {metadata.get('filtered_pages', 0)}개")
            print(f"  - 생성된 그룹: {metadata.get('total_groups', 0)}개")
            print(f"  - 소요 시간: {metadata.get('processing_time', 0):.2f}초")
            print("\n" + "=" * 80)

            return 0
        else:
            print("\n\n" + "=" * 80)
            print("실행 실패!")
            print("=" * 80)

            # 에러 메시지 출력
            errors = result.get('errors', [])
            if errors:
                print("발생한 오류:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"오류: {result.get('error', '알 수 없는 오류')}")

            print("=" * 80)
            return 1

    except FileNotFoundError as e:
        print(f"\n오류: {e}")
        print("\n입력 파일을 확인해주세요:")
        print(f"  - URLs: {Config.URLS_FILE}")
        print(f"  - Keywords: {Config.KEYWORDS_FILE}")
        return 1

    except ValueError as e:
        print(f"\n입력 오류: {e}")
        return 1

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        return 1

    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

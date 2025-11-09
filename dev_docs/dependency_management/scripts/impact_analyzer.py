#!/usr/bin/env python3
"""
변경 영향 분석 도구

기능:
- 코드 변경 전 영향 범위 파악
- 직접 의존성 + 간접 의존성 추적
- 예상 소요 시간 추정

사용 예시:
$ python scripts/impact_analyzer.py --change "explorer" --type "agent_rename" --new-name "opportunity_hunter"
$ python scripts/impact_analyzer.py --change "llm_mode" --type "config_change"
$ python scripts/impact_analyzer.py --change "ExplorerRAG" --type "class_rename"

지원 변경 유형:
- agent_rename: Agent ID 변경
- class_rename: 클래스 이름 변경
- module_move: 모듈 이동
- config_change: 설정 키 변경
- collection_rename: Collection 이름 변경
"""

import argparse
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class ImpactAnalyzer:
    """변경 영향 분석기"""
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.affected_files: Dict[str, List[str]] = {
            "code": [],
            "config": [],
            "data": [],
            "docs": [],
            "scripts": []
        }
        self.indirect_dependencies: List[Tuple[str, str]] = []
        
    def analyze(self, target: str, change_type: str, new_name: str = None) -> Dict:
        """변경 영향 분석"""
        print(f"🔍 변경 영향 분석")
        print(f"   대상: {target}")
        print(f"   유형: {change_type}")
        if new_name:
            print(f"   변경 후: {new_name}")
        print()
        
        if change_type == "agent_rename":
            return self._analyze_agent_rename(target, new_name)
        elif change_type == "class_rename":
            return self._analyze_class_rename(target, new_name)
        elif change_type == "config_change":
            return self._analyze_config_change(target, new_name)
        elif change_type == "collection_rename":
            return self._analyze_collection_rename(target, new_name)
        elif change_type == "module_move":
            return self._analyze_module_move(target, new_name)
        else:
            return {"error": f"지원하지 않는 변경 유형: {change_type}"}
    
    def _analyze_agent_rename(self, agent_id: str, new_id: str) -> Dict:
        """Agent ID 변경 영향 분석"""
        print("📋 Agent 이름 변경 영향 분석 중...")
        print()
        
        # 1. Python 코드
        print("1️⃣  Python 코드 검색...")
        self._search_in_python(agent_id)
        
        # 2. YAML 설정
        print("2️⃣  YAML 설정 검색...")
        self._search_in_yaml(agent_id)
        
        # 3. 문서
        print("3️⃣  문서 검색...")
        self._search_in_docs(agent_id)
        
        # 4. 데이터 (RAG 인덱스, chunks)
        print("4️⃣  데이터 파일 검색...")
        self._search_in_data(agent_id)
        
        # 5. 간접 의존성
        print("5️⃣  간접 의존성 분석...")
        self._find_indirect_dependencies(agent_id)
        
        return self._generate_report(agent_id, new_id, "agent_rename")
    
    def _analyze_class_rename(self, class_name: str, new_name: str) -> Dict:
        """클래스 이름 변경 영향 분석"""
        print("📋 클래스 이름 변경 영향 분석 중...")
        print()
        
        # Python 코드만 검색
        self._search_in_python(class_name)
        self._search_in_docs(class_name)
        
        return self._generate_report(class_name, new_name, "class_rename")
    
    def _analyze_config_change(self, config_key: str, new_key: str) -> Dict:
        """설정 키 변경 영향 분석"""
        print("📋 설정 키 변경 영향 분석 중...")
        print()
        
        # YAML 및 Python 코드에서 검색
        self._search_in_yaml(config_key)
        self._search_in_python(config_key)
        self._search_in_docs(config_key)
        
        return self._generate_report(config_key, new_key, "config_change")
    
    def _analyze_collection_rename(self, collection_name: str, new_name: str) -> Dict:
        """Collection 이름 변경 영향 분석"""
        print("📋 Collection 이름 변경 영향 분석 중...")
        print()
        
        # Python (collection_name=), YAML, 데이터 디렉토리
        self._search_in_python(collection_name)
        self._search_in_yaml(collection_name)
        self._search_in_data(collection_name)
        
        # ChromaDB 디렉토리
        chroma_dir = self.root / "data" / "chroma"
        if chroma_dir.exists():
            for item in chroma_dir.iterdir():
                if collection_name in item.name:
                    self.affected_files["data"].append(str(item.relative_to(self.root)))
        
        return self._generate_report(collection_name, new_name, "collection_rename")
    
    def _analyze_module_move(self, old_path: str, new_path: str) -> Dict:
        """모듈 이동 영향 분석"""
        print("📋 모듈 이동 영향 분석 중...")
        print()
        
        # import 문에서 해당 모듈 검색
        module_name = old_path.replace("/", ".").replace(".py", "")
        self._search_in_python(module_name)
        
        return self._generate_report(old_path, new_path, "module_move")
    
    def _search_in_python(self, pattern: str):
        """Python 파일에서 패턴 검색"""
        dirs_to_search = [
            self.root / "umis_rag",
            self.root / "scripts"
        ]
        
        for directory in dirs_to_search:
            if not directory.exists():
                continue
            
            for py_file in directory.rglob("*.py"):
                if any(exclude in str(py_file) for exclude in ["__pycache__", "venv", ".venv", "archive"]):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if pattern in content:
                        rel_path = str(py_file.relative_to(self.root))
                        
                        # 카테고리 분류
                        if rel_path.startswith("scripts/"):
                            self.affected_files["scripts"].append(rel_path)
                        else:
                            self.affected_files["code"].append(rel_path)
                        
                        # 매칭된 라인 찾기 (나중에 보고서에 표시)
                        
                except Exception:
                    pass
    
    def _search_in_yaml(self, pattern: str):
        """YAML 파일에서 패턴 검색"""
        yaml_dirs = [
            self.root / "config",
            self.root / "data" / "raw"
        ]
        
        for yaml_dir in yaml_dirs:
            if not yaml_dir.exists():
                continue
            
            for yaml_file in yaml_dir.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if pattern in content:
                        rel_path = str(yaml_file.relative_to(self.root))
                        self.affected_files["config"].append(rel_path)
                        
                except Exception:
                    pass
    
    def _search_in_docs(self, pattern: str):
        """문서 파일에서 패턴 검색"""
        doc_files = [
            "umis.yaml",
            "umis_core.yaml",
            ".cursorrules",
            "README.md",
            "umis_examples.yaml",
            "umis_deliverable_standards.yaml"
        ]
        
        for doc_file in doc_files:
            doc_path = self.root / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if pattern in content:
                        self.affected_files["docs"].append(doc_file)
                        
                except Exception:
                    pass
        
        # docs/ 디렉토리
        docs_dir = self.root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if pattern in content:
                        rel_path = str(doc_file.relative_to(self.root))
                        self.affected_files["docs"].append(rel_path)
                        
                except Exception:
                    pass
    
    def _search_in_data(self, pattern: str):
        """데이터 파일에서 패턴 검색"""
        data_dir = self.root / "data"
        
        if not data_dir.exists():
            return
        
        # chunks/ 디렉토리 (JSONL 파일명)
        chunks_dir = data_dir / "chunks"
        if chunks_dir.exists():
            for jsonl_file in chunks_dir.glob("*.jsonl"):
                if pattern in jsonl_file.name:
                    rel_path = str(jsonl_file.relative_to(self.root))
                    self.affected_files["data"].append(rel_path)
    
    def _find_indirect_dependencies(self, target: str):
        """간접 의존성 찾기"""
        # 직접 의존하는 파일들을 찾고,
        # 그 파일들을 import하는 다른 파일들을 찾기
        
        direct_files = (
            self.affected_files["code"] + 
            self.affected_files["scripts"]
        )
        
        for direct_file in direct_files:
            # 이 파일을 import하는 다른 파일 찾기
            module_name = direct_file.replace("/", ".").replace(".py", "")
            
            for py_file in self.root.rglob("*.py"):
                if any(exclude in str(py_file) for exclude in ["__pycache__", "venv", ".venv", "archive"]):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # import 문 검색
                    if re.search(rf'from\s+{re.escape(module_name)}|import\s+{re.escape(module_name)}', content):
                        rel_path = str(py_file.relative_to(self.root))
                        
                        # 직접 의존성이 아닌 경우만
                        if rel_path not in direct_files:
                            self.indirect_dependencies.append((direct_file, rel_path))
                            
                except Exception:
                    pass
    
    def _generate_report(self, target: str, new_name: str, change_type: str) -> Dict:
        """분석 보고서 생성"""
        total_files = sum(len(files) for files in self.affected_files.values())
        
        report = {
            "target": target,
            "new_name": new_name,
            "change_type": change_type,
            "total_affected_files": total_files,
            "direct_dependencies": self.affected_files,
            "indirect_dependencies_count": len(self.indirect_dependencies),
            "indirect_dependencies": self.indirect_dependencies,
            "estimated_time_minutes": self._estimate_time(total_files, change_type),
            "recommended_steps": self._get_recommended_steps(change_type)
        }
        
        return report
    
    def _estimate_time(self, file_count: int, change_type: str) -> int:
        """예상 소요 시간 추정 (분)"""
        base_time = {
            "agent_rename": 30,
            "class_rename": 15,
            "config_change": 20,
            "collection_rename": 25,
            "module_move": 20
        }
        
        base = base_time.get(change_type, 20)
        
        # 파일 수에 비례 (파일당 2분)
        estimated = base + (file_count * 2)
        
        # 간접 의존성 (추가 시간)
        estimated += len(self.indirect_dependencies) * 3
        
        return estimated
    
    def _get_recommended_steps(self, change_type: str) -> List[str]:
        """권장 단계"""
        common_steps = [
            "변경 전 현재 브랜치 커밋 또는 stash",
            "새 브랜치 생성: git checkout -b refactor/변경명",
        ]
        
        type_specific = {
            "agent_rename": [
                "scripts/safe_refactor.py 사용 (자동 리팩토링)",
                "YAML 설정 파일 수동 업데이트",
                "RAG 인덱스 재구축 (scripts/02_build_index.py)",
                "문서 업데이트 (umis.yaml, umis_core.yaml)",
            ],
            "class_rename": [
                "Rope 또는 IDE 리팩토링 기능 사용",
                "모든 import 문 자동 업데이트",
            ],
            "config_change": [
                "config/ 파일 업데이트",
                "umis_rag/core/config.py 스키마 업데이트",
                "관련 코드에서 참조 변경",
            ],
            "collection_rename": [
                "Agent 코드의 collection_name 업데이트",
                "RAG 인덱스 재구축",
                "ChromaDB 디렉토리 정리",
            ],
            "module_move": [
                "Rope 사용 권장",
                "모든 import 문 자동 업데이트",
            ]
        }
        
        steps = common_steps + type_specific.get(change_type, [])
        steps.extend([
            "pytest 실행 (테스트 존재 시)",
            "scripts/validate_consistency.py 실행",
            "의존성 매트릭스 재생성",
            "git commit -m 'refactor: 변경 설명'"
        ])
        
        return steps
    
    def print_report(self, report: Dict):
        """보고서 출력"""
        print()
        print("=" * 60)
        print(f"✅ 영향 분석 완료")
        print("=" * 60)
        print()
        
        print(f"🎯 변경 대상: {report['target']}")
        if report['new_name']:
            print(f"   변경 후: {report['new_name']}")
        print(f"   유형: {report['change_type']}")
        print()
        
        print(f"📊 영향 받는 파일: {report['total_affected_files']}개")
        print()
        
        for category, files in report['direct_dependencies'].items():
            if files:
                print(f"  {category.upper()}: {len(files)}개")
                for file in sorted(files)[:5]:  # 최대 5개만 표시
                    print(f"    - {file}")
                if len(files) > 5:
                    print(f"    ... 외 {len(files) - 5}개")
                print()
        
        if report['indirect_dependencies']:
            print(f"⚠️  간접 의존성: {report['indirect_dependencies_count']}개")
            print()
            for direct, indirect in report['indirect_dependencies'][:3]:
                print(f"  - {direct}")
                print(f"    → {indirect}")
                print()
            if len(report['indirect_dependencies']) > 3:
                print(f"  ... 외 {len(report['indirect_dependencies']) - 3}개")
                print()
        
        print(f"⏱️  예상 소요 시간: {report['estimated_time_minutes']}분")
        print()
        
        print("💡 권장 단계:")
        for idx, step in enumerate(report['recommended_steps'], 1):
            print(f"  {idx}. {step}")
        print()
        
        print("=" * 60)
        print()
        
        # JSON 저장
        json_path = self.root / "impact_analysis_result.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 상세 결과 저장: {json_path}")
        print()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="UMIS 변경 영향 분석 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # Agent 이름 변경
  python scripts/impact_analyzer.py --change explorer --type agent_rename --new-name opportunity_hunter
  
  # 클래스 이름 변경
  python scripts/impact_analyzer.py --change ExplorerRAG --type class_rename --new-name OpportunityHunterRAG
  
  # 설정 키 변경
  python scripts/impact_analyzer.py --change llm_mode --type config_change --new-name ai_mode
  
  # Collection 이름 변경
  python scripts/impact_analyzer.py --change explorer_knowledge_base --type collection_rename --new-name explorer_kb
        """
    )
    
    parser.add_argument("--change", required=True, help="변경 대상 (Agent ID, 클래스명, 설정 키 등)")
    parser.add_argument("--type", required=True, 
                       choices=["agent_rename", "class_rename", "config_change", "collection_rename", "module_move"],
                       help="변경 유형")
    parser.add_argument("--new-name", help="변경 후 이름 (선택)")
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    analyzer = ImpactAnalyzer(root_dir)
    report = analyzer.analyze(args.change, args.type, args.new_name)
    
    if "error" in report:
        print(f"❌ 에러: {report['error']}")
        return
    
    analyzer.print_report(report)


if __name__ == "__main__":
    main()


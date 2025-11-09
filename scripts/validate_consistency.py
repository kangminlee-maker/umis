#!/usr/bin/env python3
"""
UMIS 일관성 검증 도구

검증 항목:
1. Agent ID 일치성 (설정 ↔ 코드)
2. Collection 존재성 (코드 ↔ 실제 인덱스)
3. 설정 참조 유효성 (YAML 간 참조)
4. 문서-코드 일치성

사용:
$ python scripts/validate_consistency.py
$ python scripts/validate_consistency.py --strict  # 엄격 모드 (경고도 실패)

CI 통합:
- Exit code 0: 모든 검증 통과
- Exit code 1: 검증 실패
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Set
import re


class ConsistencyValidator:
    """일관성 검증기"""
    
    def __init__(self, root_dir: Path, strict: bool = False):
        self.root = root_dir
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> bool:
        """전체 검증"""
        print("🔍 UMIS 일관성 검증 시작...")
        print()
        
        # 1. Agent ID 검증
        print("1️⃣  Agent ID 일치성 검증...")
        self.validate_agent_ids()
        print()
        
        # 2. Collection 검증
        print("2️⃣  Collection 존재성 검증...")
        self.validate_collections()
        print()
        
        # 3. 설정 참조 검증
        print("3️⃣  YAML 설정 참조 검증...")
        self.validate_config_refs()
        print()
        
        # 4. 문서 일치성 검증
        print("4️⃣  문서-코드 일치성 검증...")
        self.validate_documentation()
        print()
        
        # 결과 출력
        return self.print_results()
    
    def validate_agent_ids(self):
        """Agent ID 일치성 검증"""
        # 정의된 Agent ID (config/agent_names.yaml)
        agent_names_path = self.root / "config" / "agent_names.yaml"
        
        if not agent_names_path.exists():
            self.errors.append("config/agent_names.yaml 파일이 없습니다")
            return
        
        with open(agent_names_path, 'r', encoding='utf-8') as f:
            agent_names = yaml.safe_load(f)
        
        defined_ids = set(agent_names.keys()) if agent_names else set()
        print(f"   설정 파일에 정의된 Agent: {sorted(defined_ids)}")
        
        # 구현된 Agent (umis_rag/agents/)
        agents_dir = self.root / "umis_rag" / "agents"
        
        if not agents_dir.exists():
            self.errors.append("umis_rag/agents/ 디렉토리가 없습니다")
            return
        
        implemented_ids = set()
        for py_file in agents_dir.glob("*.py"):
            if py_file.stem not in ["__init__", "__pycache__"]:
                implemented_ids.add(py_file.stem)
        
        print(f"   실제 구현된 Agent: {sorted(implemented_ids)}")
        
        # 비교
        missing_impl = defined_ids - implemented_ids
        extra_impl = implemented_ids - defined_ids
        
        if missing_impl:
            self.errors.append(f"설정에는 있지만 구현되지 않은 Agent: {missing_impl}")
        
        if extra_impl:
            self.warnings.append(f"구현되었지만 설정에 없는 Agent: {extra_impl}")
        
        # __init__.py 검증
        init_file = agents_dir / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r', encoding='utf-8') as f:
                init_content = f.read()
            
            for agent_id in defined_ids:
                expected_class = f"{agent_id.capitalize()}RAG"
                if expected_class not in init_content:
                    self.warnings.append(f"Agent {agent_id}가 __init__.py에서 export되지 않았습니다")
        
        if not missing_impl and not extra_impl:
            print("   ✅ Agent ID 일치성 검증 통과")
    
    def validate_collections(self):
        """Collection 존재성 검증"""
        # Agent 코드에서 사용하는 collection_name 추출
        agents_dir = self.root / "umis_rag" / "agents"
        
        if not agents_dir.exists():
            return
        
        used_collections = set()
        
        for agent_file in agents_dir.glob("*.py"):
            if agent_file.stem in ["__init__", "__pycache__"]:
                continue
            
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # collection_name= 패턴 찾기
                collections = re.findall(r'collection_name\s*=\s*["\']([^"\']+)["\']', content)
                used_collections.update(collections)
                
            except Exception as e:
                self.warnings.append(f"Agent 파일 읽기 실패: {agent_file} - {e}")
        
        print(f"   코드에서 사용 중인 Collection: {len(used_collections)}개")
        for collection in sorted(used_collections):
            print(f"     - {collection}")
        
        # 실제 ChromaDB에 존재하는 collection 확인
        chroma_dir = self.root / "data" / "chroma"
        
        if not chroma_dir.exists():
            self.warnings.append("data/chroma/ 디렉토리가 없습니다 (RAG 인덱스 미구축)")
            return
        
        # ChromaDB는 sqlite 파일로 collection 정보 저장
        # 여기서는 간단히 디렉토리 존재 여부만 체크
        try:
            import chromadb
            from umis_rag.core.config import settings
            
            client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
            existing_collections = {col.name for col in client.list_collections()}
            
            print(f"   실제 존재하는 Collection: {len(existing_collections)}개")
            
            # 비교
            missing = used_collections - existing_collections
            unused = existing_collections - used_collections
            
            if missing:
                self.warnings.append(f"사용 중이지만 인덱스 없음: {missing}")
                self.warnings.append("  → scripts/02_build_index.py 실행 필요")
            
            if unused:
                # 너무 많으면 경고 스킵
                if len(unused) <= 5:
                    self.warnings.append(f"인덱스는 있지만 미사용: {unused}")
            
        except Exception as e:
            self.warnings.append(f"ChromaDB 연결 실패: {e}")
        
        if not used_collections:
            self.errors.append("사용 중인 Collection이 하나도 없습니다")
        else:
            print("   ✅ Collection 검증 완료")
    
    def validate_config_refs(self):
        """YAML 설정 파일 간 참조 검증"""
        config_dir = self.root / "config"
        
        if not config_dir.exists():
            self.errors.append("config/ 디렉토리가 없습니다")
            return
        
        # routing_policy.yaml 검증
        routing_policy_path = config_dir / "routing_policy.yaml"
        
        if routing_policy_path.exists():
            with open(routing_policy_path, 'r', encoding='utf-8') as f:
                routing_policy = yaml.safe_load(f)
            
            # workflow에서 사용하는 agent 확인
            if routing_policy and "workflows" in routing_policy:
                # agent_names.yaml 로드
                agent_names_path = config_dir / "agent_names.yaml"
                with open(agent_names_path, 'r', encoding='utf-8') as f:
                    agent_names = yaml.safe_load(f)
                
                valid_agents = set(agent_names.keys()) if agent_names else set()
                
                for workflow_name, workflow_def in routing_policy["workflows"].items():
                    if "steps" in workflow_def:
                        for step in workflow_def["steps"]:
                            if "agent" in step:
                                agent_id = step["agent"]
                                if agent_id not in valid_agents:
                                    self.errors.append(
                                        f"routing_policy.yaml > {workflow_name} > agent '{agent_id}' not in agent_names.yaml"
                                    )
        
        # projection_rules.yaml 검증
        projection_rules_path = config_dir / "projection_rules.yaml"
        
        if projection_rules_path.exists():
            with open(projection_rules_path, 'r', encoding='utf-8') as f:
                projection_rules = yaml.safe_load(f)
            
            if projection_rules and "field_rules" in projection_rules:
                # agent_names.yaml 로드
                agent_names_path = config_dir / "agent_names.yaml"
                with open(agent_names_path, 'r', encoding='utf-8') as f:
                    agent_names = yaml.safe_load(f)
                
                valid_agents = set(agent_names.keys()) if agent_names else set()
                
                for field, rule in projection_rules["field_rules"].items():
                    if "agents" in rule:
                        for agent_id in rule["agents"]:
                            if agent_id not in valid_agents:
                                self.errors.append(
                                    f"projection_rules.yaml > field_rules > {field} > agent '{agent_id}' not in agent_names.yaml"
                                )
        
        print("   ✅ YAML 설정 참조 검증 완료")
    
    def validate_documentation(self):
        """문서-코드 일치성 검증"""
        # agent_names.yaml 로드
        agent_names_path = self.root / "config" / "agent_names.yaml"
        
        if not agent_names_path.exists():
            return
        
        with open(agent_names_path, 'r', encoding='utf-8') as f:
            agent_names = yaml.safe_load(f)
        
        valid_agents = set(agent_names.keys()) if agent_names else set()
        
        # 주요 문서 검증
        docs_to_check = [
            "umis.yaml",
            "umis_core.yaml",
            ".cursorrules"
        ]
        
        for doc_file in docs_to_check:
            doc_path = self.root / doc_file
            
            if not doc_path.exists():
                self.warnings.append(f"{doc_file} 파일이 없습니다")
                continue
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 모든 Agent가 문서에 언급되어 있는지 확인
            for agent_id in valid_agents:
                if agent_id not in content.lower():
                    self.warnings.append(f"{doc_file}에 Agent '{agent_id}' 언급 없음")
        
        print("   ✅ 문서 일치성 검증 완료")
    
    def print_results(self) -> bool:
        """검증 결과 출력"""
        print()
        print("=" * 60)
        
        has_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0
        
        if has_errors:
            print("❌ 일관성 검증 실패")
            print("=" * 60)
            print()
            print(f"🔴 에러: {len(self.errors)}개")
            for idx, error in enumerate(self.errors, 1):
                print(f"  {idx}. {error}")
            print()
        
        if has_warnings:
            print(f"⚠️  경고: {len(self.warnings)}개")
            for idx, warning in enumerate(self.warnings, 1):
                print(f"  {idx}. {warning}")
            print()
        
        if not has_errors and not has_warnings:
            print("✅ 모든 일관성 검증 통과!")
            print("=" * 60)
            print()
            return True
        
        if has_errors:
            print("💡 다음 단계:")
            print("  1. 위 에러를 수정하세요")
            print("  2. 다시 검증: python scripts/validate_consistency.py")
            print()
            print("=" * 60)
            return False
        
        if has_warnings and self.strict:
            print("❌ Strict 모드: 경고도 실패로 처리")
            print("=" * 60)
            print()
            return False
        
        print("✅ 검증 통과 (경고 있음)")
        print("=" * 60)
        print()
        return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UMIS 일관성 검증 도구")
    parser.add_argument("--strict", action="store_true", help="엄격 모드 (경고도 실패)")
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    validator = ConsistencyValidator(root_dir, strict=args.strict)
    success = validator.validate_all()
    
    # Exit code 설정 (CI 통합용)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


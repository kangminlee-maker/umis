#!/usr/bin/env python3
"""
의존성 매트릭스 생성 도구

기능:
1. Python 모듈 간 import 관계 분석
2. YAML 설정 간 참조 관계 분석
3. Agent ↔ Collection 매핑
4. 의존성 그래프 시각화 준비

출력:
- docs/architecture/DEPENDENCY_MATRIX.md
- dependency_analysis.json (분석 결과)

사용:
$ python scripts/generate_dependency_matrix.py
"""

import ast
import json
import yaml
from pathlib import Path
from typing import Dict, Set, List
from collections import defaultdict
from datetime import datetime


class DependencyAnalyzer:
    """의존성 분석기"""
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.python_imports: Dict[str, Set[str]] = {}
        self.yaml_refs: Dict[str, Dict] = {}
        self.agent_collections: Dict[str, List[str]] = defaultdict(list)
        self.collection_agents: Dict[str, List[str]] = defaultdict(list)
        
    def analyze_all(self):
        """전체 의존성 분석"""
        print("🔍 UMIS 의존성 분석 시작...")
        print()
        
        # 1. Python imports
        print("1️⃣ Python 모듈 의존성 분석...")
        self.analyze_python_imports()
        print(f"   ✅ {len(self.python_imports)}개 파일 분석 완료")
        print()
        
        # 2. YAML 참조
        print("2️⃣ YAML 설정 참조 분석...")
        self.analyze_yaml_refs()
        print(f"   ✅ {len(self.yaml_refs)}개 설정 파일 분석 완료")
        print()
        
        # 3. Agent-Collection 매핑
        print("3️⃣ Agent-Collection 매핑...")
        self.analyze_agent_collections()
        print(f"   ✅ {len(self.agent_collections)}개 Agent 매핑 완료")
        print()
        
    def analyze_python_imports(self):
        """모든 .py 파일의 import 분석"""
        umis_rag_dir = self.root / "umis_rag"
        scripts_dir = self.root / "scripts"
        
        for directory in [umis_rag_dir, scripts_dir]:
            if not directory.exists():
                continue
                
            for py_file in directory.rglob("*.py"):
                # 제외 디렉토리
                if any(exclude in str(py_file) for exclude in ["__pycache__", "venv", ".venv", "archive"]):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read(), filename=str(py_file))
                    
                    imports = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                # umis_rag 내부 import만
                                if node.module.startswith("umis_rag"):
                                    imports.add(node.module)
                    
                    if imports:
                        rel_path = str(py_file.relative_to(self.root))
                        self.python_imports[rel_path] = imports
                        
                except SyntaxError:
                    print(f"   ⚠️  구문 오류: {py_file}")
                except Exception as e:
                    print(f"   ⚠️  파싱 실패: {py_file} - {e}")
    
    def analyze_yaml_refs(self):
        """YAML 파일 참조 분석"""
        yaml_dirs = [
            self.root / "config",
            self.root / "data" / "raw"
        ]
        
        for yaml_dir in yaml_dirs:
            if not yaml_dir.exists():
                continue
                
            for yaml_file in yaml_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    if data:
                        rel_path = str(yaml_file.relative_to(self.root))
                        self.yaml_refs[rel_path] = {
                            "agents_mentioned": self._extract_agents(data),
                            "collections_mentioned": self._extract_collections(data),
                            "file_refs": self._extract_file_refs(data)
                        }
                except Exception as e:
                    print(f"   ⚠️  YAML 파싱 실패: {yaml_file} - {e}")
    
    def _extract_agents(self, data, path="") -> Set[str]:
        """YAML에서 agent 언급 추출"""
        agents = set()
        known_agents = ["observer", "explorer", "quantifier", "validator", "guardian", "estimator"]
        
        if isinstance(data, dict):
            for key, value in data.items():
                # 키 자체가 agent ID
                if key in known_agents:
                    agents.add(key)
                # 값에서 재귀 탐색
                agents.update(self._extract_agents(value, f"{path}.{key}"))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                agents.update(self._extract_agents(item, f"{path}[{idx}]"))
        elif isinstance(data, str):
            # 문자열에 agent ID 포함
            for agent in known_agents:
                if agent in data.lower():
                    agents.add(agent)
        
        return agents
    
    def _extract_collections(self, data) -> Set[str]:
        """YAML에서 collection 언급 추출"""
        collections = set()
        
        def search(obj):
            if isinstance(obj, dict):
                # collection_name 키 찾기
                if "collection_name" in obj:
                    collections.add(obj["collection_name"])
                for value in obj.values():
                    search(value)
            elif isinstance(obj, list):
                for item in obj:
                    search(item)
        
        search(data)
        return collections
    
    def _extract_file_refs(self, data) -> Set[str]:
        """YAML에서 파일 참조 추출"""
        refs = set()
        
        def search(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ["file", "path", "config_path", "data_path"]:
                        if isinstance(value, str):
                            refs.add(value)
                    search(value)
            elif isinstance(obj, list):
                for item in obj:
                    search(item)
        
        search(data)
        return refs
    
    def analyze_agent_collections(self):
        """Agent-Collection 매핑 분석"""
        # config/projection_rules.yaml에서 추출
        projection_rules_path = self.root / "config" / "projection_rules.yaml"
        
        if projection_rules_path.exists():
            with open(projection_rules_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data and "field_rules" in data:
                for field, rule in data["field_rules"].items():
                    if "agents" in rule:
                        for agent in rule["agents"]:
                            self.agent_collections[agent].append(f"field:{field}")
        
        # Agent 코드에서 collection_name 찾기
        agents_dir = self.root / "umis_rag" / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.py"):
                if agent_file.stem in ["__init__", "__pycache__"]:
                    continue
                
                agent_id = agent_file.stem
                
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # collection_name= 패턴 찾기
                    import re
                    collections = re.findall(r'collection_name\s*=\s*["\']([^"\']+)["\']', content)
                    
                    for collection in collections:
                        self.agent_collections[agent_id].append(collection)
                        self.collection_agents[collection].append(agent_id)
                        
                except Exception as e:
                    print(f"   ⚠️  Agent 파일 분석 실패: {agent_file} - {e}")
    
    def generate_matrix_markdown(self) -> str:
        """의존성 매트릭스 Markdown 생성"""
        md = f"""# UMIS 의존성 매트릭스
## Dependency Matrix

**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**버전**: UMIS v7.5.0

---

## 📊 개요

이 문서는 UMIS 코드베이스의 의존성 관계를 자동 분석한 결과입니다.

### 분석 범위

- **Python 모듈**: {len(self.python_imports)}개 파일
- **YAML 설정**: {len(self.yaml_refs)}개 파일
- **Agent**: {len(self.agent_collections)}개
- **Collection**: {len(self.collection_agents)}개

---

## 1. Agent-Collection 매핑

각 Agent가 사용하는 RAG Collection 목록입니다.

"""
        
        # Agent-Collection 테이블
        md += "| Agent | Collections | Count |\n"
        md += "|-------|-------------|-------|\n"
        
        for agent, collections in sorted(self.agent_collections.items()):
            if collections:
                collections_str = ", ".join(f"`{c}`" for c in sorted(set(collections)))
                md += f"| **{agent}** | {collections_str} | {len(set(collections))} |\n"
        
        md += "\n---\n\n"
        
        # Collection-Agent 역매핑
        md += "## 2. Collection-Agent 역매핑\n\n"
        md += "각 Collection을 사용하는 Agent 목록입니다.\n\n"
        md += "| Collection | Agents | Count |\n"
        md += "|------------|--------|-------|\n"
        
        for collection, agents in sorted(self.collection_agents.items()):
            if agents:
                agents_str = ", ".join(f"`{a}`" for a in sorted(set(agents)))
                md += f"| `{collection}` | {agents_str} | {len(set(agents))} |\n"
        
        md += "\n---\n\n"
        
        # Python 모듈 의존성
        md += "## 3. Python 모듈 의존성\n\n"
        md += "주요 모듈 간 import 관계입니다.\n\n"
        
        # Agent 모듈만 추출
        agent_files = {k: v for k, v in self.python_imports.items() if "umis_rag/agents" in k}
        
        if agent_files:
            md += "### 3.1 Agent 모듈\n\n"
            md += "| Agent 파일 | 의존 모듈 | Count |\n"
            md += "|------------|-----------|-------|\n"
            
            for file, imports in sorted(agent_files.items()):
                if imports:
                    # umis_rag 내부만
                    internal = [imp for imp in imports if imp.startswith("umis_rag")]
                    if internal:
                        imports_str = "<br>".join(f"`{imp}`" for imp in sorted(internal))
                        filename = Path(file).name
                        md += f"| `{filename}` | {imports_str} | {len(internal)} |\n"
        
        md += "\n---\n\n"
        
        # YAML 참조
        md += "## 4. YAML 설정 참조\n\n"
        md += "YAML 파일에서 참조하는 Agent 및 Collection입니다.\n\n"
        md += "| YAML 파일 | Agents | Collections |\n"
        md += "|-----------|--------|-------------|\n"
        
        for file, refs in sorted(self.yaml_refs.items()):
            agents = refs.get("agents_mentioned", set())
            collections = refs.get("collections_mentioned", set())
            
            if agents or collections:
                filename = Path(file).name
                agents_str = ", ".join(f"`{a}`" for a in sorted(agents)) if agents else "-"
                collections_str = ", ".join(f"`{c}`" for c in sorted(collections)) if collections else "-"
                md += f"| `{filename}` | {agents_str} | {collections_str} |\n"
        
        md += "\n---\n\n"
        
        # 고위험 의존성
        md += "## 5. 고위험 의존성 (High-Risk Dependencies)\n\n"
        md += "변경 시 영향 범위가 큰 모듈들입니다.\n\n"
        
        # 많이 import되는 모듈 찾기
        import_count = defaultdict(int)
        for file, imports in self.python_imports.items():
            for imp in imports:
                import_count[imp] += 1
        
        top_imports = sorted(import_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        md += "| 모듈 | 참조 횟수 | 위험도 |\n"
        md += "|------|-----------|--------|\n"
        
        for module, count in top_imports:
            if count >= 5:
                risk = "🔴 High"
            elif count >= 3:
                risk = "🟡 Medium"
            else:
                risk = "🟢 Low"
            
            md += f"| `{module}` | {count} | {risk} |\n"
        
        md += "\n---\n\n"
        
        # 변경 가이드
        md += """## 6. 변경 영향 가이드

### 6.1 Agent 이름 변경 시

영향 받는 곳:
- ✅ Python 코드 (import, 인스턴스 생성)
- ✅ YAML 설정 (agent_names.yaml, routing_policy.yaml 등)
- ✅ RAG 인덱스 메타데이터
- ✅ 문서 (umis.yaml, umis_core.yaml, .cursorrules)
- ✅ 스크립트 파일명 및 내용

권장 도구:
```bash
python scripts/impact_analyzer.py --change "agent_id" --type "agent_rename"
```

### 6.2 Collection 이름 변경 시

영향 받는 곳:
- ✅ Agent 코드 (collection_name 파라미터)
- ✅ ChromaDB 인덱스 (재구축 필요)
- ✅ 설정 파일 (projection_rules.yaml 등)
- ✅ 빌드 스크립트 (02_build_index.py)

권장 도구:
```bash
python scripts/impact_analyzer.py --change "collection_name" --type "collection_rename"
```

### 6.3 설정 키 변경 시

영향 받는 곳:
- ✅ 설정 로드 코드 (config.py, Settings 클래스)
- ✅ 다른 YAML 파일 (참조하는 경우)
- ✅ 문서

권장 도구:
```bash
python scripts/validate_consistency.py
```

---

## 7. 다음 단계

### 7.1 즉시 실행 가능

1. **의존성 그래프 시각화**
```bash
pip install pydeps
pydeps umis_rag -o docs/architecture/dependency_graph.svg
```

2. **순환 의존성 체크**
```bash
pip install import-linter
lint-imports
```

### 7.2 점진적 개선

1. Pydantic 스키마 추가 (타입 안정성)
2. 영향 분석 스크립트 작성
3. CI/CD 자동 검증 통합

---

**참고**: 이 매트릭스는 자동 생성됩니다. 정기적으로 재생성하세요.

```bash
python scripts/generate_dependency_matrix.py
```
"""
        
        return md
    
    def save_results(self):
        """결과 저장"""
        # 1. Markdown
        md_path = self.root / "docs" / "architecture" / "DEPENDENCY_MATRIX.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = self.generate_matrix_markdown()
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown 저장: {md_path}")
        
        # 2. JSON (상세 분석 결과)
        json_path = self.root / "dependency_analysis.json"
        
        analysis_data = {
            "generated_at": datetime.now().isoformat(),
            "python_imports": {k: list(v) for k, v in self.python_imports.items()},
            "yaml_refs": {k: {
                "agents": list(v["agents_mentioned"]),
                "collections": list(v["collections_mentioned"]),
                "files": list(v["file_refs"])
            } for k, v in self.yaml_refs.items()},
            "agent_collections": {k: list(set(v)) for k, v in self.agent_collections.items()},
            "collection_agents": {k: list(set(v)) for k, v in self.collection_agents.items()}
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON 저장: {json_path}")
        print()


def main():
    """메인 함수"""
    root_dir = Path(__file__).parent.parent
    
    analyzer = DependencyAnalyzer(root_dir)
    analyzer.analyze_all()
    analyzer.save_results()
    
    print("=" * 60)
    print("✅ 의존성 분석 완료!")
    print("=" * 60)
    print()
    print("📄 생성된 파일:")
    print("  - docs/architecture/DEPENDENCY_MATRIX.md")
    print("  - dependency_analysis.json")
    print()
    print("💡 다음 단계:")
    print("  1. docs/architecture/DEPENDENCY_MATRIX.md 검토")
    print("  2. pydeps 설치 및 그래프 생성:")
    print("     pip install pydeps")
    print("     pydeps umis_rag -o docs/architecture/dependency_graph.svg")
    print()


if __name__ == "__main__":
    main()


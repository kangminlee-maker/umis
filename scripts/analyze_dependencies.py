#!/usr/bin/env python3
"""
UMIS Dependency Analyzer
Python 파일 간 의존성을 분석하고 시각화합니다.

기능:
- Python 파일 스캔 및 import 분석 (ast 활용)
- 의존성 그래프 생성 (networkx)
- 순환 의존성 감지
- Critical Node 식별 (높은 의존성)
- 의존성 변경 감지 (diff)
- 그래프 시각화 (matplotlib, graphviz)

Usage:
    python3 scripts/analyze_dependencies.py
    python3 scripts/analyze_dependencies.py --visualize
    python3 scripts/analyze_dependencies.py --check-circular
    python3 scripts/analyze_dependencies.py --save-graph
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import json
from collections import defaultdict, deque
import argparse

# 외부 라이브러리 (선택적)
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("⚠️  networkx not installed. Graph analysis features disabled.")
    print("   Install: pip install networkx")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not installed. Visualization disabled.")
    print("   Install: pip install matplotlib")


@dataclass
class ImportInfo:
    """Import 정보"""
    module: str
    alias: Optional[str] = None
    is_from_import: bool = False
    imported_names: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class FileNode:
    """파일 노드 정보"""
    path: Path
    module_name: str
    imports: List[ImportInfo] = field(default_factory=list)
    imports_from_project: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    is_init_file: bool = False
    line_count: int = 0
    
    @property
    def dependency_count(self) -> int:
        """이 파일이 의존하는 파일 수"""
        return len(self.imports_from_project)
    
    @property
    def dependent_count(self) -> int:
        """이 파일에 의존하는 파일 수"""
        return len(self.imported_by)


class DependencyAnalyzer:
    """의존성 분석기"""
    
    def __init__(self, root_dir: Path, package_name: str = "umis_rag"):
        self.root_dir = root_dir
        self.package_name = package_name
        self.files: Dict[str, FileNode] = {}
        self.external_imports: Set[str] = set()
        
    def scan_directory(self) -> None:
        """디렉토리 스캔 및 Python 파일 분석"""
        print(f"\n🔍 Scanning {self.root_dir / self.package_name}...")
        
        package_dir = self.root_dir / self.package_name
        if not package_dir.exists():
            raise FileNotFoundError(f"Package directory not found: {package_dir}")
        
        python_files = list(package_dir.rglob("*.py"))
        print(f"   Found {len(python_files)} Python files")
        
        for py_file in python_files:
            self._analyze_file(py_file)
        
        print(f"   ✅ Analyzed {len(self.files)} modules")
        print(f"   ✅ Found {len(self.external_imports)} external dependencies")
    
    def _analyze_file(self, file_path: Path) -> None:
        """단일 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
            
            # 모듈 이름 생성
            rel_path = file_path.relative_to(self.root_dir)
            module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            # Import 추출
            imports = self._extract_imports(tree)
            
            # FileNode 생성
            node = FileNode(
                path=file_path,
                module_name=module_name,
                imports=imports,
                is_init_file=file_path.name == "__init__.py",
                line_count=len(content.splitlines())
            )
            
            self.files[module_name] = node
            
        except SyntaxError as e:
            print(f"   ⚠️  Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"   ⚠️  Error analyzing {file_path}: {e}")
    
    def _extract_imports(self, tree: ast.AST) -> List[ImportInfo]:
        """AST에서 import 문 추출"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        is_from_import=False,
                        line_number=node.lineno
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names = [alias.name for alias in node.names]
                    imports.append(ImportInfo(
                        module=node.module,
                        is_from_import=True,
                        imported_names=imported_names,
                        line_number=node.lineno
                    ))
        
        return imports
    
    def build_dependency_graph(self) -> None:
        """의존성 그래프 구축"""
        print("\n🔗 Building dependency graph...")
        
        for module_name, file_node in self.files.items():
            for import_info in file_node.imports:
                imported_module = import_info.module
                
                # 프로젝트 내부 import인지 확인
                if imported_module.startswith(self.package_name):
                    # 정확한 매칭
                    if imported_module in self.files:
                        file_node.imports_from_project.add(imported_module)
                        self.files[imported_module].imported_by.add(module_name)
                    else:
                        # __init__.py를 통한 import 처리
                        possible_init = imported_module + ".__init__"
                        if possible_init in self.files:
                            file_node.imports_from_project.add(possible_init)
                            self.files[possible_init].imported_by.add(module_name)
                else:
                    # 외부 라이브러리
                    self.external_imports.add(imported_module)
        
        print(f"   ✅ Graph built with {sum(f.dependency_count for f in self.files.values())} edges")
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """순환 의존성 탐지 (Tarjan's algorithm)"""
        print("\n🔄 Checking for circular dependencies...")
        
        if not HAS_NETWORKX:
            print("   ⚠️  networkx required for circular dependency detection")
            return []
        
        # NetworkX 그래프 생성
        G = nx.DiGraph()
        for module_name, file_node in self.files.items():
            for dep in file_node.imports_from_project:
                G.add_edge(module_name, dep)
        
        # 강결합 컴포넌트 찾기 (크기 > 1)
        cycles = [c for c in nx.strongly_connected_components(G) if len(c) > 1]
        
        if cycles:
            print(f"   ⚠️  Found {len(cycles)} circular dependency group(s):")
            for i, cycle in enumerate(cycles, 1):
                print(f"      Cycle {i}: {len(cycle)} modules")
                for module in sorted(cycle)[:5]:
                    print(f"         - {module}")
                if len(cycle) > 5:
                    print(f"         ... and {len(cycle) - 5} more")
        else:
            print("   ✅ No circular dependencies found!")
        
        return cycles
    
    def find_critical_nodes(self, top_n: int = 10) -> List[Tuple[str, int, int]]:
        """Critical Node 식별 (높은 의존성)"""
        print(f"\n⭐ Finding top {top_n} critical nodes...")
        
        # (module_name, dependency_count, dependent_count, total_score)
        scores = []
        for module_name, file_node in self.files.items():
            dep_count = file_node.dependency_count
            dependent_count = file_node.dependent_count
            # 가중치: 이 파일에 의존하는 파일이 더 중요
            total_score = dep_count + (dependent_count * 2)
            scores.append((module_name, dep_count, dependent_count, total_score))
        
        # 점수순 정렬
        scores.sort(key=lambda x: x[3], reverse=True)
        
        print(f"\n   {'Module':<50} {'Depends On':>12} {'Imported By':>12} {'Score':>8}")
        print("   " + "-" * 85)
        
        for module, dep_count, dependent_count, score in scores[:top_n]:
            short_name = module.replace(f"{self.package_name}.", "")
            if len(short_name) > 47:
                short_name = "..." + short_name[-44:]
            print(f"   {short_name:<50} {dep_count:>12} {dependent_count:>12} {score:>8}")
        
        return [(m, d, dc) for m, d, dc, _ in scores[:top_n]]
    
    def find_entry_points(self) -> List[str]:
        """진입점 찾기 (다른 파일에 의존하지 않는 파일)"""
        entry_points = [
            name for name, node in self.files.items()
            if node.dependency_count == 0 and not node.is_init_file
        ]
        return entry_points
    
    def find_leaf_nodes(self) -> List[str]:
        """리프 노드 찾기 (다른 파일이 의존하지 않는 파일)"""
        leaf_nodes = [
            name for name, node in self.files.items()
            if node.dependent_count == 0 and not node.is_init_file
        ]
        return leaf_nodes
    
    def generate_report(self) -> Dict:
        """의존성 분석 리포트 생성"""
        print("\n📊 Generating dependency report...")
        
        report = {
            "summary": {
                "total_files": len(self.files),
                "total_dependencies": sum(f.dependency_count for f in self.files.values()),
                "external_dependencies": len(self.external_imports),
                "total_lines": sum(f.line_count for f in self.files.values())
            },
            "critical_nodes": [],
            "circular_dependencies": [],
            "entry_points": self.find_entry_points(),
            "leaf_nodes": self.find_leaf_nodes(),
            "external_imports": sorted(self.external_imports)
        }
        
        # Critical nodes
        critical = self.find_critical_nodes(top_n=15)
        report["critical_nodes"] = [
            {
                "module": m,
                "depends_on": d,
                "imported_by": dc
            }
            for m, d, dc in critical
        ]
        
        # Circular dependencies
        if HAS_NETWORKX:
            cycles = self.find_circular_dependencies()
            report["circular_dependencies"] = [list(c) for c in cycles]
        
        return report
    
    def save_report(self, output_path: Path) -> None:
        """리포트 JSON 저장"""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Report saved to: {output_path}")
    
    def visualize_graph(self, output_path: Path, max_nodes: int = 50) -> None:
        """의존성 그래프 시각화"""
        if not HAS_NETWORKX or not HAS_MATPLOTLIB:
            print("⚠️  networkx and matplotlib required for visualization")
            return
        
        print(f"\n📈 Visualizing dependency graph (top {max_nodes} nodes)...")
        
        # Critical nodes만 선택
        critical = self.find_critical_nodes(top_n=max_nodes)
        critical_modules = {m for m, _, _ in critical}
        
        # NetworkX 그래프 생성
        G = nx.DiGraph()
        for module_name in critical_modules:
            file_node = self.files[module_name]
            for dep in file_node.imports_from_project:
                if dep in critical_modules:
                    G.add_edge(module_name, dep)
        
        # 레이아웃
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 노드 크기 (dependent count 기반)
        node_sizes = [
            300 + (self.files[node].dependent_count * 100)
            for node in G.nodes()
        ]
        
        # 그리기
        plt.figure(figsize=(20, 16))
        nx.draw(
            G, pos,
            with_labels=True,
            node_size=node_sizes,
            node_color='lightblue',
            font_size=8,
            font_weight='bold',
            arrows=True,
            arrowsize=10,
            edge_color='gray',
            alpha=0.7
        )
        
        plt.title(f"UMIS Dependency Graph (Top {max_nodes} Critical Nodes)", fontsize=16)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ Graph saved to: {output_path}")


def compare_dependencies(old_report_path: Path, new_report_path: Path) -> Dict:
    """의존성 변경 비교"""
    print("\n🔍 Comparing dependency changes...")
    
    with open(old_report_path, 'r') as f:
        old_report = json.load(f)
    
    with open(new_report_path, 'r') as f:
        new_report = json.load(f)
    
    changes = {
        "summary_changes": {},
        "critical_node_changes": [],
        "new_circular_dependencies": [],
        "resolved_circular_dependencies": [],
        "new_external_deps": [],
        "removed_external_deps": []
    }
    
    # Summary 변경
    old_summary = old_report["summary"]
    new_summary = new_report["summary"]
    
    for key in old_summary:
        old_val = old_summary[key]
        new_val = new_summary[key]
        if old_val != new_val:
            changes["summary_changes"][key] = {
                "old": old_val,
                "new": new_val,
                "delta": new_val - old_val
            }
    
    # Critical node 변경
    old_critical = {n["module"]: n for n in old_report["critical_nodes"]}
    new_critical = {n["module"]: n for n in new_report["critical_nodes"]}
    
    for module, new_data in new_critical.items():
        if module in old_critical:
            old_data = old_critical[module]
            if (old_data["imported_by"] != new_data["imported_by"] or
                old_data["depends_on"] != new_data["depends_on"]):
                changes["critical_node_changes"].append({
                    "module": module,
                    "old_imported_by": old_data["imported_by"],
                    "new_imported_by": new_data["imported_by"],
                    "old_depends_on": old_data["depends_on"],
                    "new_depends_on": new_data["depends_on"]
                })
    
    # 순환 의존성 변경
    old_cycles = set(tuple(sorted(c)) for c in old_report.get("circular_dependencies", []))
    new_cycles = set(tuple(sorted(c)) for c in new_report.get("circular_dependencies", []))
    
    changes["new_circular_dependencies"] = [list(c) for c in new_cycles - old_cycles]
    changes["resolved_circular_dependencies"] = [list(c) for c in old_cycles - new_cycles]
    
    # 외부 의존성 변경
    old_external = set(old_report["external_imports"])
    new_external = set(new_report["external_imports"])
    
    changes["new_external_deps"] = sorted(new_external - old_external)
    changes["removed_external_deps"] = sorted(old_external - new_external)
    
    # 출력
    if changes["summary_changes"]:
        print("\n   📊 Summary Changes:")
        for key, change in changes["summary_changes"].items():
            delta_str = f"+{change['delta']}" if change['delta'] > 0 else str(change['delta'])
            print(f"      {key}: {change['old']} → {change['new']} ({delta_str})")
    
    if changes["critical_node_changes"]:
        print("\n   ⭐ Critical Node Changes:")
        for change in changes["critical_node_changes"]:
            module = change["module"].replace("umis_rag.", "")
            print(f"      {module}:")
            print(f"         imported_by: {change['old_imported_by']} → {change['new_imported_by']}")
            print(f"         depends_on: {change['old_depends_on']} → {change['new_depends_on']}")
    
    if changes["new_circular_dependencies"]:
        print("\n   🚨 NEW Circular Dependencies:")
        for cycle in changes["new_circular_dependencies"]:
            print(f"      - {len(cycle)} modules involved")
    
    if changes["resolved_circular_dependencies"]:
        print("\n   ✅ RESOLVED Circular Dependencies:")
        for cycle in changes["resolved_circular_dependencies"]:
            print(f"      - {len(cycle)} modules fixed")
    
    if changes["new_external_deps"]:
        print("\n   📦 NEW External Dependencies:")
        for dep in changes["new_external_deps"]:
            print(f"      + {dep}")
    
    if changes["removed_external_deps"]:
        print("\n   🗑️  REMOVED External Dependencies:")
        for dep in changes["removed_external_deps"]:
            print(f"      - {dep}")
    
    if not any([
        changes["summary_changes"],
        changes["critical_node_changes"],
        changes["new_circular_dependencies"],
        changes["resolved_circular_dependencies"],
        changes["new_external_deps"],
        changes["removed_external_deps"]
    ]):
        print("   ✅ No changes detected")
    
    return changes


def main():
    parser = argparse.ArgumentParser(description="UMIS Dependency Analyzer")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization")
    parser.add_argument("--check-circular", action="store_true", help="Only check circular dependencies")
    parser.add_argument("--save-graph", action="store_true", help="Save dependency graph as JSON")
    parser.add_argument("--max-nodes", type=int, default=50, help="Max nodes in visualization")
    parser.add_argument("--output-dir", type=str, default="dev_docs", help="Output directory")
    parser.add_argument("--compare", type=str, help="Compare with previous report (path to old JSON)")
    
    args = parser.parse_args()
    
    # Root directory
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print("=" * 80)
    print("  UMIS Dependency Analyzer")
    print("=" * 80)
    
    # 분석기 초기화
    analyzer = DependencyAnalyzer(root_dir=root_dir, package_name="umis_rag")
    
    # 스캔 및 분석
    analyzer.scan_directory()
    analyzer.build_dependency_graph()
    
    # 순환 의존성만 체크
    if args.check_circular:
        analyzer.find_circular_dependencies()
        return
    
    # 리포트 생성
    output_dir = root_dir / args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / "dependency_analysis.json"
    analyzer.save_report(report_path)
    
    # 의존성 변경 비교
    if args.compare:
        compare_path = Path(args.compare)
        if compare_path.exists():
            changes = compare_dependencies(compare_path, report_path)
            
            # 변경사항 저장
            changes_path = output_dir / "dependency_changes.json"
            with open(changes_path, 'w', encoding='utf-8') as f:
                json.dump(changes, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Changes saved to: {changes_path}")
        else:
            print(f"\n⚠️  Comparison file not found: {compare_path}")
    
    # 시각화
    if args.visualize:
        graph_path = output_dir / "dependency_graph.png"
        analyzer.visualize_graph(graph_path, max_nodes=args.max_nodes)
    
    # 그래프 저장
    if args.save_graph and HAS_NETWORKX:
        # NetworkX 그래프를 GraphML로 저장
        G = nx.DiGraph()
        for module_name, file_node in analyzer.files.items():
            for dep in file_node.imports_from_project:
                G.add_edge(module_name, dep)
        
        graphml_path = output_dir / "dependency_graph.graphml"
        nx.write_graphml(G, graphml_path)
        print(f"✅ Graph saved to: {graphml_path}")
    
    print("\n" + "=" * 80)
    print("  Analysis Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

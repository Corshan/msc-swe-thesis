from dataclasses import dataclass, field
from typing import Set, Dict, List
from pathlib import Path

@dataclass
class FeatureSets:
    feature_name: str
    common: Set[str] = field(default_factory=set)
    involved: Set[str] = field(default_factory=set)
    essential: Set[str] = field(default_factory=set)
    unique: Set[str] = field(default_factory=set)

class ReconnaissanceAnalyzer:
    def __init__(self):
        pass

    def load_traces(self, trace_dir: Path) -> Dict[str, Set[str]]:
        traces: Dict[str, Set[str]] = {}
        for trace_file in trace_dir.glob("*.trace"):
            if trace_file.stem == "out":
                continue

            traces[trace_file.stem] = set()
            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    traces[trace_file.stem].add(line[7:])
          
        return traces

    def compute_sets(self, traces: Dict[str, Set[str]], feature_mapping: Dict[str, List[str]] = None) -> Dict[str, FeatureSets]:
        """
        Computes the software reconnaissance sets.
            
        Args:
            traces: mapping of test_case -> set of executed components (e.g., functions)
            feature_mapping: Optional mapping of feature_name -> list of test cases. If None, each test case is treated as a separate feature.
        
        Returns:
            Mapping of feature -> FeatureSets
        """
        all_test_cases = set(traces.keys())
        all_components = set()
        for components in traces.values():
            all_components.update(components)

        # 1. Common: Components executed in ALL test cases
        common_set = set(all_components)
        for components in traces.values():
            common_set.intersection_update(components)

        if feature_mapping is None:
            feature_mapping = {test: [test] for test in traces.keys()}

        results = {}
        for feature, feature_tests in feature_mapping.items():
            feature_sets = FeatureSets(feature_name=feature)
            feature_sets.common = common_set
            
            # Involved: Components executed in at least one test case of the feature
            involved_set = set()
            for test in feature_tests:
                if test in traces:
                    involved_set.update(traces[test])
            feature_sets.involved = involved_set
            
            # Essential: Components executed in ALL test cases of the feature
            essential_set = None
            for test in feature_tests:
                if test in traces:
                    if essential_set is None:
                        essential_set = set(traces[test])
                    else:
                        essential_set.intersection_update(traces[test])
            feature_sets.essential = essential_set if essential_set is not None else set()
            
            # Unique: Components executed in this feature's tests, but nowhere else
            other_tests = all_test_cases - set(feature_tests)
            other_involved = set()
            for test in other_tests:
                other_involved.update(traces[test])
            
            feature_sets.unique = involved_set - other_involved
            results[feature] = feature_sets
            
        return results

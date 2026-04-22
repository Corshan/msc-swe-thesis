class ReconAnalyzer:
    def __init__(self, features, testcases, mapping, profile_loader):
        """
        features: list of feature names
        testcases: list of all testcase file names
        mapping: list of lists, mapping[i] is test cases for features[i]
        profile_loader: function that takes a filename and returns a set of procedures
        """
        self.features = features
        self.testcases = testcases
        self.mapping = mapping
        self.profile_loader = profile_loader
        
        # Cache for profiles to avoid redundant reads
        self.profiles = {}
        self._load_all_profiles()

    def _load_all_profiles(self):
        for tc in self.testcases:
            if tc not in self.profiles:
                self.profiles[tc] = self.profile_loader(tc)

    def calculate_celems(self):
        """Common software elements (intersection of all test cases)."""
        if not self.profiles:
            return set()
        all_sets = list(self.profiles.values())
        return set.intersection(*all_sets)

    def calculate_ielems(self, feature_idx):
        """Involved software elements (union of test cases exhibiting a feature)."""
        feature_testcases = self.mapping[feature_idx]
        if not feature_testcases:
            return set()
        sets = [self.profiles[tc] for tc in feature_testcases if tc in self.profiles]
        return set.union(*sets) if sets else set()

    def calculate_iielems(self, feature_idx):
        """Indispensably involved software elements (intersection of test cases exhibiting a feature)."""
        feature_testcases = self.mapping[feature_idx]
        if not feature_testcases:
            return set()
        sets = [self.profiles[tc] for tc in feature_testcases if tc in self.profiles]
        return set.intersection(*sets) if sets else set()

    def calculate_relems(self, iielems, celems):
        """Relevant software elements (IIELEMS - CELEMS)."""
        return iielems - celems

    def calculate_uelems(self, ielems, feature_idx):
        """Unique software elements (IELEMS - union of test cases NOT exhibiting a feature)."""
        exhibiting = set(self.mapping[feature_idx])
        not_exhibiting = [tc for tc in self.testcases if tc not in exhibiting]
        
        if not not_exhibiting:
            return ielems
            
        sets_not_exhibiting = [self.profiles[tc] for tc in not_exhibiting if tc in self.profiles]
        union_not_exhibiting = set.union(*sets_not_exhibiting) if sets_not_exhibiting else set()
        
        return ielems - union_not_exhibiting

    def calculate_shared(self, iielems, uelems, celems):
        """Shared software elements (IIELEMS - UELEMS - CELEMS)."""
        return iielems - uelems - celems

    def analyze_all(self):
        results = {
            "celems": self.calculate_celems(),
            "features": []
        }
        
        celems = results["celems"]
        
        for i, name in enumerate(self.features):
            ielems = self.calculate_ielems(i)
            iielems = self.calculate_iielems(i)
            relems = self.calculate_relems(iielems, celems)
            uelems = self.calculate_uelems(ielems, i)
            shared = self.calculate_shared(iielems, uelems, celems)
            
            results["features"].append({
                "name": name,
                "ielems": ielems,
                "iielems": iielems,
                "relems": relems,
                "uelems": uelems,
                "shared": shared
            })
            
        return results

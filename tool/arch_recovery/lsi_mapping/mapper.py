import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from typing import Dict, List

class LSIMapper:
    def __init__(self, n_features: int = 5):
        self.n_features = n_features

    def map_features(self, function_texts: Dict[str, str], output_file: str = "detected_mapping.yaml") -> Dict[str, List[str]]:
        """
        Uses LSI to map function text documents to abstract features.
        """
        if not function_texts:
            print("No functions to map.")
            return {}

        identifiers = list(function_texts.keys())
        texts = list(function_texts.values())

        # 1. TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(texts)

        # 2. LSI (TruncatedSVD)
        # n_components cannot be larger than the number of documents or features
        n_components = min(100, len(identifiers) - 1)
        if n_components < 1:
            n_components = 1
            
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        lsi_matrix = svd.fit_transform(tfidf_matrix)

        # 3. Clustering into features
        n_clusters = min(self.n_features, len(identifiers))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(lsi_matrix)

        # 4. Create Mapping
        feature_mapping = {}
        for i in range(n_clusters):
            feature_mapping[f"Feature_{i}"] = []

        for idx, label in enumerate(labels):
            feature_name = f"Feature_{label}"
            feature_mapping[feature_name].append(identifiers[idx])

        # 5. Output to YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(feature_mapping, f, default_flow_style=False)
            
        print(f"LSI mapping written to {output_file}")
        return feature_mapping

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import json


class IncidentClusterer:
    """Cluster and deduplicate incidents using TF-IDF and cosine similarity."""
    
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.incident_vectors = None
        self.incidents = []
    
    def fit(self, incidents: List[Dict[str, Any]]):
        """Fit the clusterer on incident data."""
        self.incidents = incidents
        
        texts = []
        for incident in incidents:
            title = incident.get('title', '')
            description = incident.get('description', '')
            text = f"{title} {description}"
            texts.append(text)
        
        if texts:
            self.incident_vectors = self.vectorizer.fit_transform(texts)
    
    def find_similar(self, query_incident: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar incidents to the query."""
        if self.incident_vectors is None or not self.incidents:
            return []
        
        title = query_incident.get('title', '')
        description = query_incident.get('description', '')
        query_text = f"{title} {description}"
        
        query_vector = self.vectorizer.transform([query_text])
        
        similarities = cosine_similarity(query_vector, self.incident_vectors)[0]
        
        similar_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in similar_indices:
            if similarities[idx] >= self.similarity_threshold:
                results.append({
                    'incident': self.incidents[idx],
                    'similarity_score': float(similarities[idx]),
                    'incident_id': self.incidents[idx].get('id', f'incident_{idx}')
                })
        
        return results
    
    def is_duplicate(self, query_incident: Dict[str, Any]) -> Tuple[bool, Optional[str], float]:
        """Check if incident is a duplicate."""
        similar = self.find_similar(query_incident, top_k=1)
        
        if not similar:
            return False, None, 0.0
        
        best_match = similar[0]
        similarity = best_match['similarity_score']
        
        if similarity >= 0.85:
            return True, best_match['incident_id'], similarity
        
        return False, None, similarity
    
    def cluster_incidents(self, incidents: List[Dict[str, Any]], min_cluster_size: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster incidents into groups."""
        if not incidents:
            return {}
        
        self.fit(incidents)
        
        clusters = defaultdict(list)
        assigned = set()
        
        for i, incident in enumerate(incidents):
            if i in assigned:
                continue
            
            cluster_id = f"cluster_{len(clusters)}"
            clusters[cluster_id].append(incident)
            assigned.add(i)
            
            similar = self.find_similar(incident, top_k=10)
            
            for match in similar:
                match_incident = match['incident']
                match_idx = self.incidents.index(match_incident)
                
                if match_idx not in assigned and match['similarity_score'] >= self.similarity_threshold:
                    clusters[cluster_id].append(match_incident)
                    assigned.add(match_idx)
        
        filtered_clusters = {
            cid: incidents_list 
            for cid, incidents_list in clusters.items() 
            if len(incidents_list) >= min_cluster_size
        }
        
        return filtered_clusters
    
    def get_cluster_summary(self, cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of a cluster."""
        if not cluster:
            return {}
        
        severities = [inc.get('severity', 'unknown') for inc in cluster]
        categories = [inc.get('category', 'unknown') for inc in cluster]
        
        severity_counts = defaultdict(int)
        for sev in severities:
            severity_counts[sev] += 1
        
        category_counts = defaultdict(int)
        for cat in categories:
            category_counts[cat] += 1
        
        most_common_severity = max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else 'unknown'
        most_common_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'unknown'
        
        return {
            'cluster_size': len(cluster),
            'most_common_severity': most_common_severity,
            'most_common_category': most_common_category,
            'severity_distribution': dict(severity_counts),
            'category_distribution': dict(category_counts),
            'incident_ids': [inc.get('id', 'unknown') for inc in cluster]
        }


def detect_alert_storm(
    incidents: List[Dict[str, Any]],
    time_window_minutes: int = 60,
    min_incidents: int = 10
) -> Dict[str, Any]:
    """Detect alert storms (high volume of similar incidents in short time)."""
    if len(incidents) < min_incidents:
        return {
            'is_alert_storm': False,
            'incident_count': len(incidents),
            'message': 'Incident count below threshold'
        }
    
    clusterer = IncidentClusterer(similarity_threshold=0.70)
    clusters = clusterer.cluster_incidents(incidents, min_cluster_size=min_incidents)
    
    if not clusters:
        return {
            'is_alert_storm': False,
            'incident_count': len(incidents),
            'clusters_found': 0,
            'message': 'No significant clusters detected'
        }
    
    largest_cluster = max(clusters.values(), key=len)
    cluster_summary = clusterer.get_cluster_summary(largest_cluster)
    
    return {
        'is_alert_storm': True,
        'incident_count': len(incidents),
        'clusters_found': len(clusters),
        'largest_cluster_size': len(largest_cluster),
        'cluster_summary': cluster_summary,
        'message': f'Alert storm detected: {len(largest_cluster)} similar incidents',
        'recommended_action': 'Consolidate incidents and investigate root cause'
    }


def deduplicate_incident_batch(
    new_incidents: List[Dict[str, Any]],
    existing_incidents: List[Dict[str, Any]],
    similarity_threshold: float = 0.85
) -> Dict[str, Any]:
    """Batch deduplicate new incidents against existing ones."""
    clusterer = IncidentClusterer(similarity_threshold=similarity_threshold)
    clusterer.fit(existing_incidents)
    
    duplicates = []
    unique = []
    
    for incident in new_incidents:
        is_dup, dup_of, score = clusterer.is_duplicate(incident)
        
        if is_dup:
            duplicates.append({
                'incident': incident,
                'duplicate_of': dup_of,
                'similarity_score': score
            })
        else:
            unique.append(incident)
    
    return {
        'total_processed': len(new_incidents),
        'duplicates_found': len(duplicates),
        'unique_incidents': len(unique),
        'duplicate_rate': len(duplicates) / len(new_incidents) if new_incidents else 0.0,
        'duplicates': duplicates,
        'unique': unique
    }

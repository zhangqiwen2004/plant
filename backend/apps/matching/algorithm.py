from collections import defaultdict
from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from apps.users.models import User, UserTag
from .models import TagWeight


class UserMatchingAlgorithm:
    ULT_WEIGHTS = {
        'plant_type': 1.5,
        'care_environment': 1.0,
        'interest': 1.2,
        'problem': 1.3,
    }
    
    REGION_WEIGHTS = {
        'same': 1.0,
        'adjacent': 0.5,
        'different': 0.2,
    }
    
    ADJACENT_REGIONS = {
        'north': ['northeast', 'northwest', 'central'],
        'northeast': ['north'],
        'east': ['central', 'south'],
        'central': ['north', 'east', 'south', 'southwest'],
        'south': ['east', 'central', 'southwest'],
        'southwest': ['central', 'south', 'northwest'],
        'northwest': ['north', 'southwest'],
    }
    
    def __init__(self):
        self.tag_weights = dict(self.DEFAULT_WEIGHTS)
    
    def _load_tag_weights(self):
        weights = dict(self.ULT_WEIGHTS)
        try:
            for tw in TagWeight.objects.all():
                weights[tw.tag_type] = tw.weight
        except (OperationalError, ProgrammingError):
            return weights
        return weights
    
    def _get_user_tag_vector(self, user):
        tags = UserTag.objects.filter(user=user)
        tag_dict = defaultdict(list)
        for tag in tags:
            tag_dict[tag.tag_type].append({
                'value': tag.tag_value,
                'weight': tag.weight
            })
        return tag_dict
    
    def _calculate_tag_similarity(self, tags1, tags2):
        all_tag_types = set(tags1.keys()) | set(tags2.keys())
        if not all_tag_types:
            return 0.0, []
        self.tag_weights = self._load_tag_weights()
        
        total_score = 0.0
        total_weight = 0.0
        matched_tags = []
        
        for tag_type in all_tag_types:
            type_weight = self.tag_weights.get(tag_type, 1.0)
            values1 = set(t['value'] for t in tags1.get(tag_type, []))
            values2 = set(t['value'] for t in tags2.get(tag_type, []))
            
            if values1 and values2:
                intersection = values1 & values2
                union = values1 | values2
                jaccard = len(intersection) / len(union) if union else 0
                
                total_score += jaccard * type_weight
                total_weight += type_weight
                
                if intersection:
                    matched_tags.extend([
                        {'type': tag_type, 'value': v} for v in intersection
                    ])
            elif values1 or values2:
                total_weight += type_weight * 0.5
        
        similarity = total_score / total_weight if total_weight > 0 else 0.0
        return similarity, matched_tags
    
    def _calculate_region_score(self, region1, region2):
        if not region1 or not region2:
            return 0.5
        if region1 == region2:
            return self.REGION_WEIGHTS['same']
        if region2 in self.ADJACENT_REGIONS.get(region1, []):
            return self.REGION_WEIGHTS['adjacent']
        return self.REGION_WEIGHTS['different']
    
    def _calculate_experience_score(self, exp1, exp2, match_type='peer'):
        exp_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        
        try:
            level1 = exp_levels.index(exp1)
            level2 = exp_levels.index(exp2)
        except ValueError:
            return 0.5
        
        if match_type == 'expert':
            return 1.0 if level2 >= level1 else 0.5
        else:
            diff = abs(level1 - level2)
            return max(0, 1.0 - diff * 0.25)
    
    def calculate_match_score(self, user1, user2, match_type='peer'):
        tags1 = self._get_user_tag_vector(user1)
        tags2 = self._get_user_tag_vector(user2)
        
        tag_similarity, matched_tags = self._calculate_tag_similarity(tags1, tags2)
        region_score = self._calculate_region_score(user1.region, user2.region)
        exp_score = self._calculate_experience_score(
            user1.experience_level, user2.experience_level, match_type
        )
        
        if match_type == 'expert':
            final_score = tag_similarity * 0.6 + region_score * 0.2 + exp_score * 0.2
        else:
            final_score = tag_similarity * 0.5 + region_score * 0.3 + exp_score * 0.2
        
        return {
            'score': round(final_score, 4),
            'tag_similarity': round(tag_similarity, 4),
            'region_score': round(region_score, 4),
            'experience_score': round(exp_score, 4),
            'matched_tags': matched_tags
        }
    
    def find_expert_matches(self, user, limit=10):
        experts = User.objects.filter(
            role='expert',
            is_expert_verified=True
        ).exclude(pk=user.pk)
        
        matches = []
        for expert in experts:
            result = self.calculate_match_score(user, expert, match_type='expert')
            if result['score'] > 0.1:
                matches.append({
                    'user': expert,
                    **result
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
    
    def find_peer_matches(self, user, limit=10):
        peers = User.objects.filter(
            role__in=['user', 'expert']
        ).exclude(pk=user.pk)
        
        matches = []
        for peer in peers:
            result = self.calculate_match_score(user, peer, match_type='peer')
            if result['score'] > 0.2:
                matches.append({
                    'user': peer,
                    **result
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
    
    def generate_match_reason(self, matched_tags, region_match, exp_match):
        reasons = []
        
        if matched_tags:
            tag_values = [t['value'] for t in matched_tags[:3]]
            reasons.append(f"共同关注: {', '.join(tag_values)}")
        
        if region_match:
            reasons.append("同一地区")
        
        if exp_match:
            reasons.append("经验水平相近")
        
        return "; ".join(reasons) if reasons else "基于综合标签匹配"


matching_algorithm = UserMatchingAlgorithm()

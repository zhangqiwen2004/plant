from collections import defaultdict

from apps.users.models import User, UserTag
from .models import TagWeight


class UserMatchingAlgorithm:
    DEFAULT_WEIGHTS = {
        'plant_type': 3.0,
        'region': 2.0,
        'care_environment': 1.5,
        'experience_level': 1.0,
    }

    EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']
    MAX_PLANT_TAGS = 2
    MAX_ENVIRONMENT_TAGS = 1
    MAX_CORE_TAGS = 5

    def __init__(self):
        self.tag_weights = dict(self.DEFAULT_WEIGHTS)

    def _load_tag_weights(self):
        weights = dict(self.DEFAULT_WEIGHTS)
        try:
            for tag_weight in TagWeight.objects.all():
                if tag_weight.tag_type in weights:
                    weights[tag_weight.tag_type] = tag_weight.weight
        except Exception:
            return weights
        return weights

    def _get_priority_tags(self, user, tag_type, limit):
        return list(
            UserTag.objects.filter(user=user, tag_type=tag_type).order_by('-weight', 'created_at')[:limit]
        )

    def _get_user_core_tags(self, user):
        self.tag_weights = self._load_tag_weights()
        core_tags = []

        for tag in self._get_priority_tags(user, 'plant_type', self.MAX_PLANT_TAGS):
            core_tags.append({
                'type': 'plant_type',
                'value': tag.tag_value,
                'label': tag.tag_value,
                'weight': self.tag_weights['plant_type'],
            })

        for tag in self._get_priority_tags(user, 'care_environment', self.MAX_ENVIRONMENT_TAGS):
            core_tags.append({
                'type': 'care_environment',
                'value': tag.tag_value,
                'label': tag.tag_value,
                'weight': self.tag_weights['care_environment'],
            })

        if user.region:
            core_tags.append({
                'type': 'region',
                'value': user.region,
                'label': user.get_region_display() or user.region,
                'weight': self.tag_weights['region'],
            })

        if user.experience_level:
            core_tags.append({
                'type': 'experience_level',
                'value': user.experience_level,
                'label': user.get_experience_level_display() or user.experience_level,
                'weight': self.tag_weights['experience_level'],
            })

        return core_tags[:self.MAX_CORE_TAGS]

    def _build_tag_index(self, core_tags):
        tag_index = defaultdict(set)
        for tag in core_tags:
            tag_index[tag['type']].add(tag['value'])
        return tag_index

    def _experience_matches(self, requester_level, candidate_level, match_type='peer'):
        try:
            requester_index = self.EXPERIENCE_LEVELS.index(requester_level)
            candidate_index = self.EXPERIENCE_LEVELS.index(candidate_level)
        except ValueError:
            return False

        if match_type == 'expert':
            return candidate_index >= requester_index
        return candidate_index == requester_index

    def calculate_match_score(self, user1, user2, match_type='peer'):
        requester_core_tags = self._get_user_core_tags(user1)
        candidate_core_tags = self._get_user_core_tags(user2)
        candidate_tag_index = self._build_tag_index(candidate_core_tags)

        matched_tags = []
        priority_hits = {
            'plant_type': 0,
            'region': 0,
            'care_environment': 0,
            'experience_level': 0,
        }
        weighted_overlap = 0.0
        total_possible_weight = sum(tag['weight'] for tag in requester_core_tags) or 1.0

        for tag in requester_core_tags:
            tag_type = tag['type']
            is_match = False
            matched_label = tag['label']

            if tag_type == 'experience_level':
                is_match = self._experience_matches(tag['value'], user2.experience_level, match_type)
                if is_match:
                    matched_label = user2.get_experience_level_display() or user2.experience_level
            else:
                is_match = tag['value'] in candidate_tag_index.get(tag_type, set())

            if is_match:
                weighted_overlap += tag['weight']
                priority_hits[tag_type] += 1
                matched_tags.append({
                    'type': tag_type,
                    'value': tag['value'],
                    'label': matched_label,
                    'weight': tag['weight'],
                })

        overlap_count = len(matched_tags)
        score = weighted_overlap / total_possible_weight if requester_core_tags else 0.0
        tag_similarity = overlap_count / len(requester_core_tags) if requester_core_tags else 0.0
        region_score = 1.0 if priority_hits['region'] else 0.0
        experience_score = 1.0 if priority_hits['experience_level'] else 0.0

        return {
            'score': round(score, 4),
            'tag_similarity': round(tag_similarity, 4),
            'region_score': round(region_score, 4),
            'experience_score': round(experience_score, 4),
            'matched_tags': matched_tags,
            'overlap_count': overlap_count,
            'core_tag_count': len(requester_core_tags),
            'priority_hits': priority_hits,
        }

    def _match_sort_key(self, match):
        priority_hits = match['priority_hits']
        return (
            priority_hits.get('plant_type', 0),
            priority_hits.get('region', 0),
            priority_hits.get('care_environment', 0),
            priority_hits.get('experience_level', 0),
            match['overlap_count'],
            match['score'],
        )

    def find_expert_matches(self, user, limit=10):
        experts = User.objects.filter(role='expert', is_expert_verified=True).exclude(pk=user.pk)
        matches = []
        for expert in experts:
            result = self.calculate_match_score(user, expert, match_type='expert')
            if result['score'] > 0:
                matches.append({'user': expert, **result})
        matches.sort(key=self._match_sort_key, reverse=True)
        return matches[:limit]

    def find_peer_matches(self, user, limit=10):
        peers = User.objects.filter(role__in=['user', 'expert']).exclude(pk=user.pk)
        matches = []
        for peer in peers:
            result = self.calculate_match_score(user, peer, match_type='peer')
            if result['score'] > 0:
                matches.append({'user': peer, **result})
        matches.sort(key=self._match_sort_key, reverse=True)
        return matches[:limit]

    def generate_match_reason(self, matched_tags, region_match, exp_match):
        reasons = []
        plant_matches = [tag['label'] for tag in matched_tags if tag['type'] == 'plant_type']
        environment_matches = [tag['label'] for tag in matched_tags if tag['type'] == 'care_environment']
        if plant_matches:
            reasons.append(f"植物类型重合: {', '.join(plant_matches[:2])}")
        if region_match:
            reasons.append('地区匹配')
        if environment_matches:
            reasons.append(f"养护环境一致: {', '.join(environment_matches[:1])}")
        if exp_match:
            reasons.append('经验等级匹配')
        return '; '.join(reasons) if reasons else '基于核心标签重合度匹配'


matching_algorithm = UserMatchingAlgorithm()

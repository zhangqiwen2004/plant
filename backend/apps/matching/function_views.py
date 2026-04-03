from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .basic_algorithm import matching_algorithm
from .constants import MATCH_MODE_API_VALUES, MATCH_MODE_OPTIONS


def _serialize_match(match):
    user = match['user']
    return {
        'user': {
            'id': user.id,
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None,
            'bio': user.bio,
            'experience_level': user.experience_level,
            'experience_display': user.get_experience_level_display(),
            'region': user.region,
            'region_display': user.get_region_display(),
            'expert_specialty': user.expert_specialty,
            'is_expert_verified': user.is_expert_verified,
        },
        'score': match['score'],
        'tag_similarity': match['tag_similarity'],
        'region_score': match['region_score'],
        'experience_score': match['experience_score'],
        'matched_tags': match['matched_tags'],
        'overlap_count': match['overlap_count'],
        'core_tag_count': match['core_tag_count'],
        'priority_hits': match['priority_hits'],
        'match_reason': matching_algorithm.generate_match_reason(
            match['matched_tags'],
            match['region_score'] >= 1,
            match['experience_score'] >= 1,
        ),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def basic_match_results(request):
    match_type = request.query_params.get('match_type', MATCH_MODE_OPTIONS[0]['api_value'])
    try:
        limit = max(1, min(int(request.query_params.get('limit', 10)), 20))
    except ValueError:
        limit = 10

    if match_type not in MATCH_MODE_API_VALUES:
        match_type = MATCH_MODE_OPTIONS[0]['api_value']

    if match_type == 'peer':
        matches = matching_algorithm.find_peer_matches(request.user, limit=limit)
    else:
        match_type = MATCH_MODE_OPTIONS[0]['api_value']
        matches = matching_algorithm.find_expert_matches(request.user, limit=limit)

    return Response({
        'match_type': match_type,
        'results': [_serialize_match(match) for match in matches],
    })

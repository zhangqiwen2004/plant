from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime as dt, time

from .constants import TREND_PRESETS
from .models import DailyStatistics, UserActivity
from .serializers import (
    DailyStatisticsSerializer, UserActivitySerializer,
    OverviewSerializer, TrendDataSerializer
)
from apps.users.models import User, ExpertApplication
from apps.users.permissions import IsAdmin
from apps.community.models import Post, Question, Answer, Comment


def get_today_range():
    """获取今天的时区感知的时间范围（解决MySQL时区表缺失的问题）"""
    today = timezone.localdate()
    start = timezone.make_aware(dt.combine(today, time.min))
    end = timezone.make_aware(dt.combine(today, time.max))
    return start, end


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        today_start, today_end = get_today_range()
        
        total_users = User.objects.count()
        total_experts = User.objects.filter(role='expert', is_expert_verified=True).count()
        total_posts = Post.objects.filter(status='approved').count()
        total_questions = Question.objects.count()
        total_answers = Answer.objects.count()
        pending_posts = Post.objects.filter(status='pending').count()
        pending_applications = ExpertApplication.objects.filter(status='pending').count()
        
        today_active = UserActivity.objects.filter(
            created_at__range=(today_start, today_end)
        ).values('user').distinct().count()
        
        today_new = User.objects.filter(
            created_at__range=(today_start, today_end)
        ).count()
        
        from apps.matching.models import MatchRecord
        total_matches = MatchRecord.objects.count()
        success_matches = MatchRecord.objects.filter(is_contacted=True).count()
        match_rate = round(success_matches / total_matches * 100, 2) if total_matches > 0 else 0
        
        data = {
            'total_users': total_users,
            'total_experts': total_experts,
            'total_posts': total_posts,
            'total_questions': total_questions,
            'total_answers': total_answers,
            'pending_posts': pending_posts,
            'pending_applications': pending_applications,
            'today_active_users': today_active,
            'today_new_users': today_new,
            'match_success_rate': match_rate,
        }
        
        return Response(data)


class AnalyticsTrendView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        try:
            days = int(request.query_params.get('days', TREND_PRESETS[0]))
        except ValueError:
            days = TREND_PRESETS[0]
        if days not in TREND_PRESETS:
            days = TREND_PRESETS[0]
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        dates = []
        new_users = []
        active_users = []
        posts = []
        interactions = []
        
        current_date = start_date
        stats_dict = {s.date: s for s in stats}
        
        while current_date <= end_date:
            dates.append(current_date)
            stat = stats_dict.get(current_date)
            if stat:
                new_users.append(stat.new_users)
                active_users.append(stat.active_users)
                posts.append(stat.new_posts)
                interactions.append(stat.total_interactions)
            else:
                new_users.append(0)
                active_users.append(0)
                posts.append(0)
                interactions.append(0)
            current_date += timedelta(days=1)
        
        return Response({
            'dates': dates,
            'new_users': new_users,
            'active_users': active_users,
            'posts': posts,
            'interactions': interactions,
        })


class DailyStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyStatistics.objects.all()
    serializer_class = DailyStatisticsSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['date']
    
    @action(detail=False, methods=['post'])
    def generate_today(self, request):
        today = timezone.localdate()
        today_start, today_end = get_today_range()
        
        new_users = User.objects.filter(created_at__range=(today_start, today_end)).count()
        active_users = UserActivity.objects.filter(
            created_at__range=(today_start, today_end)
        ).values('user').distinct().count()
        total_users = User.objects.count()
        
        new_posts = Post.objects.filter(created_at__range=(today_start, today_end)).count()
        new_questions = Question.objects.filter(created_at__range=(today_start, today_end)).count()
        new_answers = Answer.objects.filter(created_at__range=(today_start, today_end)).count()
        new_comments = Comment.objects.filter(created_at__range=(today_start, today_end)).count()
        
        total_interactions = new_posts + new_questions + new_answers + new_comments
        
        from apps.matching.models import MatchRecord
        match_count = MatchRecord.objects.filter(created_at__range=(today_start, today_end)).count()
        match_success = MatchRecord.objects.filter(
            created_at__range=(today_start, today_end), is_contacted=True
        ).count()
        
        stat, created = DailyStatistics.objects.update_or_create(
            date=today,
            defaults={
                'new_users': new_users,
                'active_users': active_users,
                'total_users': total_users,
                'new_posts': new_posts,
                'new_questions': new_questions,
                'new_answers': new_answers,
                'new_comments': new_comments,
                'total_interactions': total_interactions,
                'match_count': match_count,
                'match_success_count': match_success,
            }
        )
        
        serializer = DailyStatisticsSerializer(stat)
        return Response(serializer.data)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.select_related('user').all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['user', 'action']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = int(request.query_params.get('limit', 50))
        activities = UserActivity.objects.select_related('user').all()[:limit]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': '需要提供user_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        stats = UserActivity.objects.filter(user_id=user_id).values('action').annotate(
            count=Count('id')
        )
        
        return Response(list(stats))

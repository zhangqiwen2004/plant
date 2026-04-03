<template>
  <div class="page-container post-detail-page" v-loading="loading">
    <el-page-header @back="$router.push('/community')" title="返回社区" />

    <div v-if="post" class="detail-shell">
      <el-card class="post-detail-card">
        <div class="detail-hero">
          <div class="detail-topbar">
            <div class="author-wrap">
              <div class="author-avatar-shell">
                <el-avatar :size="52" :src="resolveAvatarUrl(post.author_info?.avatar, post.author_info?.id)">
                  {{ post.author_info?.username?.[0] || '匿' }}
                </el-avatar>
              </div>
              <div class="author-info">
                <span class="author-name">
                  {{ post.author_info?.username || '匿名用户' }}
                  <el-tag v-if="post.author_info?.is_expert" size="small" type="warning">达人</el-tag>
                </span>
                <span class="post-time">发布于 {{ formatTime(post.created_at) }}</span>
              </div>
            </div>

            <div class="hero-badges">
              <el-tag v-if="post.is_top" type="danger">置顶</el-tag>
              <el-tag v-if="post.is_essence" type="warning">精华</el-tag>
              <el-tag v-if="post.topic_name" type="success" effect="plain"># {{ post.topic_name }}</el-tag>
            </div>
          </div>

          <div class="title-block">
            <h1 class="post-title">{{ post.title }}</h1>
            <p class="post-intro">把养护场景、问题背景和处理经验集中展示，阅读节奏会更清晰。</p>
          </div>

          <div class="hero-stats">
            <div class="hero-stat-item">
              <span class="hero-stat-value">{{ post.like_count }}</span>
              <span class="hero-stat-label">点赞</span>
            </div>
            <div class="hero-stat-item">
              <span class="hero-stat-value">{{ post.comment_count || commentsTotal }}</span>
              <span class="hero-stat-label">评论</span>
            </div>
            <div class="hero-stat-item">
              <span class="hero-stat-value">{{ post.view_count }}</span>
              <span class="hero-stat-label">浏览</span>
            </div>
          </div>
        </div>

        <div class="post-content">{{ post.content }}</div>

        <div v-if="post.images?.length" class="post-gallery">
          <img v-for="(image, index) in post.images" :key="`${post.id}-image-${index}`" :src="image" :alt="post.title" />
        </div>

        <div class="post-actions">
          <el-button :icon="Star" :type="post.is_liked ? 'warning' : 'default'" @click="handleLike">
            {{ post.is_liked ? '已点赞' : '点赞支持' }}
          </el-button>
          <span class="view-count"><el-icon><View /></el-icon> {{ post.view_count }} 浏览</span>
        </div>
      </el-card>

      <el-card class="comments-card">
        <template #header>
          <div class="comments-header">
            <div>
              <h3>评论区</h3>
              <p>留下你的观察和建议，让讨论更完整。</p>
            </div>
            <span class="comment-total">{{ post.comment_count || commentsTotal }} 条评论</span>
          </div>
        </template>

        <div v-if="userStore.isLoggedIn" class="comment-input">
          <div class="comment-compose">
            <el-avatar class="compose-avatar" :size="42" :src="resolveAvatarUrl(userStore.user?.avatar, userStore.user?.id)">
              {{ userStore.user?.username?.[0] || '我' }}
            </el-avatar>
            <div class="compose-main">
              <el-input v-model="newComment" type="textarea" :rows="4" placeholder="写下你的评论..." />
              <div class="compose-actions">
                <span class="compose-tip">补充你的环境、频率和观察结果，评论更有帮助。</span>
                <el-button type="primary" @click="handleComment" :loading="submitting">
                  发表评论
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <el-divider v-if="userStore.isLoggedIn" />

        <div v-if="comments.length === 0" class="no-comments">
          <el-empty description="暂无评论，快来抢沙发吧~" />
        </div>

        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <el-avatar class="comment-avatar" :size="42" :src="resolveAvatarUrl(comment.author_info?.avatar, comment.author_info?.id)">
            {{ comment.author_info?.username?.[0] || '匿' }}
          </el-avatar>
          <div class="comment-content">
            <div class="comment-header">
              <div class="comment-meta">
                <span class="comment-author">{{ comment.author_info?.username || '匿名用户' }}</span>
                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              </div>
            </div>
            <p class="comment-text">{{ comment.content }}</p>
          </div>
        </div>

        <div class="pagination-wrap" v-if="commentsTotal > commentPageSize">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="commentsTotal"
            :page-size="commentPageSize"
            :current-page="commentPage"
            @current-change="handleCommentPageChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, View } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import dayjs from 'dayjs'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const route = useRoute()
const userStore = useUserStore()
const post = ref(null)
const comments = ref([])
const loading = ref(true)
const newComment = ref('')
const submitting = ref(false)
const commentsTotal = ref(0)
const commentPage = ref(1)
const commentPageSize = 10

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : (data?.results?.length || 0))

const fetchComments = async () => {
  const res = await api.get(`/api/community/comments/?post=${route.params.id}&page=${commentPage.value}&page_size=${commentPageSize}`)
  comments.value = normalizeList(res.data)
  commentsTotal.value = getListTotal(res.data)
}

const handleCommentPageChange = (page) => {
  commentPage.value = page
  fetchComments()
}

const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    if (post.value.is_liked) {
      await api.delete(`/api/community/posts/${route.params.id}/unlike/`)
      post.value.is_liked = false
      post.value.like_count--
    } else {
      await api.post(`/api/community/posts/${route.params.id}/like/`)
      post.value.is_liked = true
      post.value.like_count++
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/api/community/comments/', {
      post: route.params.id,
      content: newComment.value
    })
    ElMessage.success('评论成功')
    newComment.value = ''

    commentPage.value = 1
    await fetchComments()
    post.value.comment_count++
  } catch (error) {
    ElMessage.error('评论失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [postRes, commentsRes] = await Promise.all([
      api.get(`/api/community/posts/${route.params.id}/`),
      api.get(`/api/community/comments/?post=${route.params.id}&page=${commentPage.value}&page_size=${commentPageSize}`)
    ])
    post.value = postRes.data
    comments.value = normalizeList(commentsRes.data)
    commentsTotal.value = getListTotal(commentsRes.data)
  } catch (error) {
    ElMessage.error('获取帖子失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.post-detail-page {
  display: flex;
  flex-direction: column;
}

.detail-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.post-detail-card,
.comments-card {
  overflow: hidden;
}

.post-detail-card :deep(.el-card__body) {
  padding: 0;
}

.detail-hero {
  padding: 28px 28px 24px;
  background:
    linear-gradient(135deg, rgba(245, 250, 246, 0.98), rgba(236, 243, 237, 0.9)),
    radial-gradient(circle at top right, rgba(92, 153, 103, 0.14), transparent 28%);
}

.detail-topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
}

.author-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.author-avatar-shell {
  width: 60px;
  height: 60px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(77, 139, 87, 0.16), rgba(77, 139, 87, 0.06));
  flex-shrink: 0;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: #203226;
}

.post-time {
  display: block;
  color: #7d8d80;
  font-size: 13px;
  margin-top: 6px;
}

.hero-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.title-block {
  margin-top: 24px;
}

.post-title {
  font-size: 40px;
  line-height: 1.18;
  color: #1d2d23;
}

.post-intro {
  margin-top: 14px;
  color: #6b7b6e;
  font-size: 15px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
}

.hero-stat-item {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.hero-stat-value {
  display: block;
  font-size: 26px;
  font-weight: 700;
  color: #203226;
}

.hero-stat-label {
  display: block;
  margin-top: 8px;
  color: #7b8b7e;
  font-size: 13px;
}

.post-content {
  padding: 28px;
  color: #3f4f44;
  font-size: 16px;
  line-height: 1.95;
  white-space: pre-wrap;
}

.post-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  padding: 0 28px 28px;
}

.post-gallery img {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 18px;
  object-fit: cover;
  display: block;
}

.post-actions {
  padding: 0 28px 28px;
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.view-count {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #809083;
}

.comments-card :deep(.el-card__header) {
  padding: 22px 24px 16px;
}

.comments-card :deep(.el-card__body) {
  padding: 0 24px 24px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.comments-header h3 {
  color: #203226;
  font-size: 22px;
}

.comments-header p {
  margin-top: 8px;
  color: #7a8b7e;
  font-size: 14px;
}

.comment-total {
  color: #6f8073;
  font-size: 13px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(240, 246, 241, 0.9);
}

.comment-input {
  margin-bottom: 20px;
}

.comment-compose {
  display: flex;
  gap: 14px;
  padding: 20px;
  border-radius: 22px;
  background: rgba(248, 251, 248, 0.9);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.compose-avatar,
.comment-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4d8b57 0%, #2f6739 100%);
  color: #ffffff;
  font-weight: 700;
  flex-shrink: 0;
}

.compose-main {
  flex: 1;
}

.compose-actions {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.compose-tip {
  color: #7b8b7e;
  font-size: 13px;
}

.comment-item {
  display: flex;
  gap: 14px;
  padding: 18px 0;
  border-bottom: 1px solid rgba(56, 97, 64, 0.08);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.comment-author {
  color: #233428;
  font-weight: 700;
}

.comment-time {
  color: #88988c;
  font-size: 13px;
}

.comment-text {
  margin-top: 10px;
  color: #5c6d60;
  line-height: 1.8;
}

.pagination-wrap {
  margin-top: 22px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .detail-hero,
  .post-content,
  .post-actions {
    padding-left: 20px;
    padding-right: 20px;
  }

  .detail-topbar,
  .comments-header,
  .compose-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .post-title {
    font-size: 28px;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .comment-compose {
    flex-direction: column;
  }

  .compose-actions {
    width: 100%;
  }

  .compose-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>

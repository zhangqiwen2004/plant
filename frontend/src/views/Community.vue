<template>
  <div class="page-container community-page">
    <section class="community-hero">
      <el-card class="hero-card">
        <div class="hero-layout">
          <div class="hero-copy">
            <div>
              <span class="hero-eyebrow">社区广场</span>
              <h1>像内容平台一样浏览植物养护动态，把重点内容一眼看清。</h1>
              <p>
                我把发布入口、话题筛选、内容信息层级和右侧导航重新整理成更现代的内容流布局，浏览和互动都会顺手很多。
              </p>
            </div>

            <div>
              <div class="hero-actions">
                <el-button type="primary" :icon="Plus" @click="userStore.isLoggedIn ? showCreateDialog = true : router.push('/login')">
                  {{ userStore.isLoggedIn ? '发布动态' : '登录后参与互动' }}
                </el-button>
                <el-button plain @click="clearTopic">查看全部动态</el-button>
              </div>

              <div class="hero-stats">
                <div v-for="item in communityStats" :key="item.label" class="stat-card">
                  <span class="stat-value">{{ item.value }}</span>
                  <span class="stat-label">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="hero-side">
            <div class="side-panel">
              <span class="side-label">当前筛选</span>
              <h3>{{ activeTopicName }}</h3>
              <p>{{ selectedTopic ? '你正在查看指定话题下的动态内容。' : '这里展示社区中最新通过审核的动态。' }}</p>
            </div>

            <div class="side-panel compact-panel">
              <span class="side-label">快速进入</span>
              <div class="hero-topic-grid">
                <button
                  v-for="topic in quickTopics"
                  :key="topic.id"
                  type="button"
                  class="hero-topic-chip"
                  :class="{ active: selectedTopic === topic.id }"
                  @click="selectTopic(topic.id)"
                >
                  <span># {{ topic.name }}</span>
                  <span>{{ topic.post_count }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </section>

    <div class="community-shell">
      <div class="community-main">
        <el-card class="feed-header-card">
          <div class="feed-header">
            <div>
              <h2>动态列表</h2>
              <p>按照内容社区的浏览习惯，保留高频信息并弱化噪音。</p>
            </div>
            <button v-if="selectedTopic" type="button" class="clear-filter" @click="clearTopic">
              清除当前话题
            </button>
          </div>

          <div class="quick-filter-row">
            <button
              type="button"
              class="quick-filter"
              :class="{ active: !selectedTopic }"
              @click="clearTopic"
            >
              全部
            </button>
            <button
              v-for="topic in quickTopics"
              :key="topic.id"
              type="button"
              class="quick-filter"
              :class="{ active: selectedTopic === topic.id }"
              @click="selectTopic(topic.id)"
            >
              # {{ topic.name }}
            </button>
          </div>
        </el-card>

        <div class="post-list" v-loading="loading">
          <article v-for="post in posts" :key="post.id" class="post-card" @click="router.push(`/posts/${post.id}`)">
            <div class="post-header">
              <div class="post-author-block">
                <div class="avatar-shell">
                  <el-avatar :size="46" :src="resolveAvatarUrl(post.author_info?.avatar, post.author_info?.id)">
                    {{ post.author_info?.username?.[0] || '匿' }}
                  </el-avatar>
                </div>
                <div class="post-author">
                  <span class="author-name">
                    {{ post.author_info?.username || '匿名用户' }}
                    <el-tag v-if="post.author_info?.is_expert" size="small" type="warning">达人</el-tag>
                  </span>
                  <span class="post-time">{{ formatTime(post.created_at) }}</span>
                </div>
              </div>

              <div class="post-badges">
                <el-tag v-if="post.is_top" type="danger" size="small">置顶</el-tag>
                <el-tag v-if="post.is_essence" type="warning" size="small">精华</el-tag>
              </div>
            </div>

            <div class="post-body">
              <h3>{{ post.title }}</h3>
              <p>{{ getPostExcerpt(post.content) }}</p>
            </div>

            <div v-if="post.images?.length" class="post-gallery">
              <img v-for="(image, index) in post.images.slice(0, 3)" :key="`${post.id}-${index}`" :src="image" :alt="post.title" />
              <div v-if="post.images.length > 3" class="post-gallery-more">+{{ post.images.length - 3 }}</div>
            </div>

            <div class="post-footer">
              <div class="post-topic" v-if="post.topic_name"># {{ post.topic_name }}</div>
              <div class="post-actions">
                <button type="button" class="action" :class="{ active: post.is_liked }" @click.stop="handleLike(post)">
                  <el-icon><Star /></el-icon>
                  <span>{{ post.like_count }}</span>
                </button>
                <button type="button" class="action" @click.stop="router.push(`/posts/${post.id}`)">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>{{ post.comment_count }}</span>
                </button>
                <span class="action static-action">
                  <el-icon><View /></el-icon>
                  <span>{{ post.view_count }}</span>
                </span>
              </div>
            </div>
          </article>

          <el-empty v-if="!loading && posts.length === 0" description="暂无动态" />
        </div>

        <div class="pagination-wrap" v-if="postsTotal > postPageSize">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="postsTotal"
            :page-size="postPageSize"
            :current-page="postPage"
            @current-change="handlePostPageChange"
          />
        </div>
      </div>

      <div class="community-side">
        <el-card class="topics-card">
          <template #header>
            <div class="sidebar-header">
              <span>话题导航</span>
              <span class="sidebar-tip">{{ topics.length }} 个话题</span>
            </div>
          </template>

          <div class="topics-list">
            <button
              type="button"
              class="topic-item"
              :class="{ active: !selectedTopic }"
              @click="clearTopic"
            >
              <span># 全部动态</span>
              <span class="count">{{ postsTotal }}</span>
            </button>

            <button
              v-for="topic in topics"
              :key="topic.id"
              type="button"
              class="topic-item"
              :class="{ active: selectedTopic === topic.id }"
              @click="selectTopic(topic.id)"
            >
              <span># {{ topic.name }}</span>
              <span class="count">{{ topic.post_count }}</span>
            </button>
          </div>
        </el-card>

        <el-card class="guide-card">
          <div class="guide-content">
            <span class="side-label">社区玩法</span>
            <h3>想让内容更容易被看见？</h3>
            <ul class="guide-list">
              <li>标题里直接写出植物名称或问题场景。</li>
              <li>正文里补充环境、浇水频率和异常变化。</li>
              <li>发布到合适的话题下，浏览和互动会更集中。</li>
            </ul>
            <el-button type="primary" plain @click="userStore.isLoggedIn ? showCreateDialog = true : router.push('/login')">
              {{ userStore.isLoggedIn ? '立即发动态' : '先去登录' }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    
    <el-dialog v-model="showCreateDialog" title="发布动态" width="620px" @closed="resetPostForm">
      <el-form :model="postForm" :rules="postRules" ref="postFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="postForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="话题" prop="topic">
          <el-select v-model="postForm.topic" placeholder="选择话题（可选）" clearable style="width: 100%">
            <el-option v-for="topic in topics" :key="topic.id" :label="topic.name" :value="topic.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="postForm.content" type="textarea" :rows="6" placeholder="分享你的养护心得..." />
        </el-form-item>
        <el-form-item label="图片">
          <el-upload
            v-model:file-list="postImageFiles"
            :auto-upload="false"
            list-type="picture-card"
            multiple
            accept="image/*"
            :limit="6"
            :before-upload="beforePostImageUpload"
            :on-exceed="handlePostFileExceed"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-helper">支持 jpg、jpeg、png、webp，单张不超过 5MB，最多 6 张。</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePost" :loading="submitting">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Star, ChatDotRound, View, TrendCharts } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import dayjs from 'dayjs'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const posts = ref([])
const topics = ref([])
const loading = ref(true)
const selectedTopic = ref(null)
const showCreateDialog = ref(false)
const submitting = ref(false)
const postFormRef = ref(null)
const postImageFiles = ref([])
const postsTotal = ref(0)
const postPage = ref(1)
const postPageSize = 8

const postForm = ref({ title: '', content: '', topic: '' })
const postRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

const quickTopics = computed(() => topics.value.slice(0, 6))
const activeTopicName = computed(() => {
  if (!selectedTopic.value) return '全部动态'
  return topics.value.find(topic => topic.id === selectedTopic.value)?.name || '当前话题'
})

const communityStats = computed(() => [
  { label: '当前动态', value: postsTotal.value || 0 },
  { label: '热门话题', value: topics.value.length || 0 },
  { label: '浏览模式', value: selectedTopic.value ? '话题内' : '广场' }
])

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const normalizeList = (data) => {
  if (Array.isArray(data)) return data
  return data?.results || []
}

const getListTotal = (data) => {
  if (Array.isArray(data)) return data.length
  if (typeof data?.count === 'number') return data.count
  return data?.results?.length || 0
}

const getPostExcerpt = (content = '', limit = 180) => {
  if (!content) return '作者暂时还没有补充更多内容。'
  return content.length > limit ? `${content.substring(0, limit)}...` : content
}

const getRequestErrorMessage = (error, fallback) => {
  const data = error.response?.data
  if (!data || typeof data !== 'object') return fallback
  const firstKey = Object.keys(data)[0]
  const value = data[firstKey]
  if (Array.isArray(value) && value.length > 0) return value[0]
  return typeof value === 'string' ? value : fallback
}

const beforePostImageUpload = (file) => {
  const isImage = file.type?.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 <= 5
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('单张图片大小不能超过 5MB')
    return false
  }
  return true
}

const handlePostFileExceed = () => {
  ElMessage.warning('最多上传 6 张图片')
}

const validatePostImages = () => {
  for (const file of postImageFiles.value) {
    const rawFile = file.raw || file
    if (!beforePostImageUpload(rawFile)) {
      return false
    }
  }
  return true
}

const resetPostForm = () => {
  postForm.value = { title: '', content: '', topic: '' }
  postImageFiles.value = []
}

const buildPostPayload = () => {
  const formData = new FormData()
  formData.append('title', postForm.value.title)
  formData.append('content', postForm.value.content)
  if (postForm.value.topic) {
    formData.append('topic', String(postForm.value.topic))
  }
  postImageFiles.value.forEach(file => {
    if (file.raw) {
      formData.append('uploaded_images', file.raw)
    }
  })
  return formData
}

const syncTopicFromRoute = () => {
  const topicId = Number.parseInt(route.query.topic, 10)
  selectedTopic.value = Number.isNaN(topicId) ? null : topicId
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('status', 'approved')
    params.append('page', String(postPage.value))
    params.append('page_size', String(postPageSize))
    if (selectedTopic.value) params.append('topic', selectedTopic.value)

    const res = await api.get(`/api/community/posts/?${params.toString()}`)
    posts.value = normalizeList(res.data)
    postsTotal.value = getListTotal(res.data)
  } catch (error) {
} finally {
    loading.value = false
  }
}

const handlePostPageChange = (page) => {
  postPage.value = page
  fetchPosts()
}

const selectTopic = (topicId) => {
  const nextTopic = selectedTopic.value === topicId ? undefined : topicId
  router.replace({ path: '/community', query: nextTopic ? { topic: String(nextTopic) } : {} })
}

const clearTopic = () => {
  router.replace({ path: '/community', query: {} })
}

const handleLike = async (post) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    if (post.is_liked) {
      await api.delete(`/api/community/posts/${post.id}/unlike/`)
      post.is_liked = false
      post.like_count--
    } else {
      await api.post(`/api/community/posts/${post.id}/like/`)
      post.is_liked = true
      post.like_count++
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleCreatePost = async () => {
  const valid = await postFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!validatePostImages()) return

  submitting.value = true
  try {
    await api.post('/api/community/posts/', buildPostPayload())
    ElMessage.success('发布成功，等待审核')
    showCreateDialog.value = false
    resetPostForm()
    fetchPosts()
  } catch (error) {
    ElMessage.error(getRequestErrorMessage(error, '发布失败'))
  } finally {
    submitting.value = false
  }
}

watch(() => route.query.topic, () => {
  syncTopicFromRoute()
  postPage.value = 1
  fetchPosts()
})

onMounted(async () => {
  syncTopicFromRoute()

  try {
    const res = await api.get('/api/community/topics/?page_size=100')
    topics.value = normalizeList(res.data)
  } catch (error) {
}

  fetchPosts()
})
</script>

<style scoped>
.community-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.hero-card :deep(.el-card__body) {
  padding: 0;
}

.hero-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) 360px;
  gap: 22px;
  padding: 28px;
  background:
    linear-gradient(135deg, rgba(245, 250, 246, 0.96), rgba(236, 243, 237, 0.9)),
    radial-gradient(circle at top right, rgba(102, 163, 113, 0.14), transparent 28%);
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
}

.hero-eyebrow,
.side-label {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #708174;
}

.hero-copy h1 {
  margin-top: 16px;
  max-width: 780px;
  font-size: 40px;
  line-height: 1.14;
  color: #1d2d23;
}

.hero-copy p {
  margin-top: 14px;
  max-width: 720px;
  color: #67786b;
  font-size: 16px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
}

.stat-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.stat-value {
  display: block;
  font-size: 28px;
  line-height: 1.1;
  font-weight: 700;
  color: #203226;
}

.stat-label {
  display: block;
  margin-top: 8px;
  color: #758679;
  font-size: 13px;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-panel {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.side-panel h3 {
  margin-top: 12px;
  font-size: 22px;
  color: #203226;
}

.side-panel p {
  margin-top: 10px;
  color: #6a7a6e;
  line-height: 1.7;
  font-size: 14px;
}

.compact-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero-topic-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.hero-topic-chip {
  border: none;
  background: rgba(244, 248, 244, 0.95);
  border-radius: 16px;
  padding: 12px;
  color: #385d40;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.hero-topic-chip.active {
  background: linear-gradient(135deg, #4d8b57 0%, #2f6739 100%);
  color: #ffffff;
}

.community-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) 340px;
  gap: 22px;
}

.community-main,
.community-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.feed-header-card :deep(.el-card__body) {
  padding: 22px 24px 24px;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.feed-header h2 {
  font-size: 24px;
  color: #203226;
}

.feed-header p {
  margin-top: 8px;
  color: #74857a;
  font-size: 14px;
}

.clear-filter {
  border: none;
  background: rgba(240, 246, 241, 0.95);
  color: #355b3d;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
}

.quick-filter-row {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-filter {
  border: none;
  background: rgba(244, 248, 244, 0.95);
  color: #567058;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.quick-filter:hover {
  transform: translateY(-1px);
}

.quick-filter.active {
  background: linear-gradient(135deg, #4d8b57 0%, #2f6739 100%);
  color: #ffffff;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination-wrap {
  margin-top: 6px;
  display: flex;
  justify-content: center;
}

.post-card {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(56, 97, 64, 0.08);
  box-shadow: 0 18px 34px rgba(31, 49, 38, 0.08);
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 42px rgba(31, 49, 38, 0.11);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.post-author-block {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.avatar-shell {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(77, 139, 87, 0.16), rgba(77, 139, 87, 0.04));
  flex-shrink: 0;
}

.post-author {
  min-width: 0;
}

.author-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: #203226;
}

.post-time {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: #87988b;
}

.post-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.post-body {
  margin-top: 18px;
}

.post-body h3 {
  font-size: 22px;
  line-height: 1.35;
  color: #1d2d23;
}

.post-body p {
  margin-top: 12px;
  color: #67786b;
  line-height: 1.85;
  font-size: 15px;
}

.post-gallery {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.post-gallery img,
.post-gallery-more {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 16px;
}

.post-gallery img {
  object-fit: cover;
  display: block;
}

.post-gallery-more {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(77, 139, 87, 0.12);
  color: #2f6739;
  font-weight: 700;
}

.post-footer {
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid rgba(56, 97, 64, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.post-topic {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(238, 245, 239, 0.95);
  color: #355b3d;
  font-size: 13px;
  font-weight: 600;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.action {
  border: none;
  background: rgba(245, 248, 245, 0.92);
  color: #738577;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
}

.action.active,
.action:hover {
  background: rgba(232, 243, 234, 0.95);
  color: #355b3d;
}

.action.static-action {
  cursor: default;
}

.upload-helper {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.static-action:hover {
  background: rgba(245, 248, 245, 0.92);
  color: #738577;
}

.topics-card,
.guide-card {
  position: sticky;
  top: 112px;
}

.topics-card :deep(.el-card__body),
.guide-card :deep(.el-card__body) {
  padding: 20px 22px 22px;
}

.guide-card {
  top: 476px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.sidebar-tip {
  color: #87988b;
  font-size: 12px;
}

.topics-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
}

.topic-item {
  border: none;
  background: rgba(246, 249, 246, 0.95);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border-radius: 16px;
  color: #44604b;
  cursor: pointer;
}

.topic-item.active {
  background: linear-gradient(135deg, rgba(77, 139, 87, 0.16), rgba(77, 139, 87, 0.08));
  color: #24422b;
}

.count {
  color: #809083;
  font-size: 13px;
}

.guide-content h3 {
  margin-top: 12px;
  color: #203226;
}

.guide-list {
  margin: 16px 0 20px;
  padding-left: 18px;
  color: #66776a;
  display: flex;
  flex-direction: column;
  gap: 10px;
  line-height: 1.7;
}

@media (max-width: 1200px) {
  .community-shell {
    grid-template-columns: 1fr;
  }

  .community-side {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .topics-card,
  .guide-card {
    position: static;
  }
}

@media (max-width: 1024px) {
  .hero-layout {
    grid-template-columns: 1fr;
  }

  .hero-copy h1 {
    font-size: 34px;
  }
}

@media (max-width: 768px) {
  .hero-layout,
  .post-card {
    padding: 20px;
  }

  .hero-stats,
  .hero-topic-grid,
  .community-side {
    grid-template-columns: 1fr;
  }

  .hero-actions,
  .post-footer,
  .feed-header {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }

  .post-header {
    flex-direction: column;
  }

  .post-body h3 {
    font-size: 19px;
  }

  .post-actions {
    width: 100%;
    justify-content: space-between;
  }

  .action {
    justify-content: center;
    flex: 1;
  }
}
</style>

<template>
  <div class="page-container home-page">
    
    <section class="hero-section">
      <el-card class="hero-main">
        <div class="hero-grid">
          <div class="hero-copy">
            <div>
              <span class="hero-eyebrow">植物社区新首页</span>
              <h1>把植物百科、交流内容和达人建议整理成更顺手的养护工作台</h1>
              <p>
                从植物资料、社区经验到问答互助，你可以在更清晰的布局中快速找到下一步要做什么。
              </p>
            </div>

            <div>
              <div class="banner-actions">
                <el-button type="primary" size="large" @click="$router.push('/plants')">
                  <el-icon><Search /></el-icon>探索植物百科
                </el-button>
                <el-button size="large" @click="$router.push('/community')">
                  <el-icon><ChatDotRound /></el-icon>进入社区广场
                </el-button>
              </div>

              <div class="hero-stats">
                <div v-for="item in heroStats" :key="item.label" class="hero-stat">
                  <span class="hero-stat-value">{{ item.value }}</span>
                  <span class="hero-stat-label">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="hero-side">
            <div class="insight-panel">
              <span class="insight-label">社区热度</span>
              <h3>{{ leadTopic ? `# ${leadTopic.name}` : '今日值得关注的话题' }}</h3>
              <p>
                {{ leadTopic ? `当前已有 ${leadTopic.post_count} 篇讨论，适合快速加入互动。` : '暂时还没有热门话题，去社区发起一条新的讨论。' }}
              </p>
              <button
                type="button"
                class="hero-link"
                @click="$router.push(leadTopic ? `/community?topic=${leadTopic.id}` : '/community')"
              >
                去看热议话题
              </button>
            </div>

            <div v-if="leadPost" class="floating-post" @click="$router.push(`/posts/${leadPost.id}`)">
              <span class="floating-label">最近动态</span>
              <h4>{{ leadPost.title }}</h4>
              <p>{{ leadPost.content?.substring(0, 88) }}{{ leadPost.content?.length > 88 ? '...' : '' }}</p>
              <div class="floating-meta">
                <span>{{ leadPost.author_info?.username || '匿名用户' }}</span>
                <span><el-icon><View /></el-icon>{{ leadPost.view_count }}</span>
                <span><el-icon><ChatDotRound /></el-icon>{{ leadPost.comment_count }}</span>
              </div>
            </div>

            <div v-else class="floating-post empty-state">
              <span class="floating-label">最近动态</span>
              <h4>社区内容正在准备中</h4>
              <p>等第一条动态出现后，这里会展示最新的社区交流内容。</p>
            </div>
          </div>
        </div>
      </el-card>
    </section>

    
    <section class="feature-row">
      <article v-for="item in features" :key="item.title" class="feature-card" @click="$router.push(item.link)">
        <div class="feature-icon" :style="{ background: item.bg, color: item.color }">
          <el-icon :size="28"><component :is="item.icon" /></el-icon>
        </div>
        <div class="feature-copy">
          <div class="feature-head">
            <h3>{{ item.title }}</h3>
            <span class="feature-tag">{{ item.tag }}</span>
          </div>
          <p>{{ item.desc }}</p>
        </div>
      </article>
    </section>

    <div class="home-grid">
      <div class="home-main">
        
        <el-card class="section-card plants-section">
          <template #header>
            <div class="section-header">
              <span class="section-title"><el-icon><TrendCharts /></el-icon>热门植物</span>
              <el-button text type="primary" @click="$router.push('/plants')">查看更多</el-button>
            </div>
          </template>

          <div class="plants-grid">
            <article v-for="plant in popularPlants" :key="plant.id" class="plant-card" @click="$router.push(`/plants/${plant.id}`)">
              <div class="plant-image">
                <img :src="plant.image_url" :alt="plant.name" class="plant-photo" loading="lazy" @error="handleImageError" />
              </div>
              <div class="plant-copy">
                <h4>{{ plant.name }}</h4>
                <p>{{ plant.alias || '从基础习性、光照和浇水建议开始了解它。' }}</p>
              </div>
              <div class="plant-footer">
                <el-tag size="small" :type="getDifficultyType(plant.difficulty)">
                  {{ plant.difficulty_display }}
                </el-tag>
                <span class="plant-views"><el-icon><View /></el-icon>{{ plant.view_count }}</span>
              </div>
            </article>
          </div>
        </el-card>

        
        <el-card class="section-card">
          <template #header>
            <div class="section-header">
              <span class="section-title"><el-icon><ChatDotRound /></el-icon>热门话题</span>
              <el-button text type="primary" @click="$router.push('/community')">查看更多</el-button>
            </div>
          </template>

          <div class="topics-list">
            <button
              v-for="topic in topics"
              :key="topic.id"
              type="button"
              class="topic-pill"
              @click="$router.push(`/community?topic=${topic.id}`)"
            >
              <span class="topic-name"># {{ topic.name }}</span>
              <span class="topic-count">{{ topic.post_count }} 篇</span>
            </button>
          </div>
        </el-card>
      </div>

      <div class="home-side">
        
        <el-card class="section-card activity-section">
          <template #header>
            <div class="section-header">
              <span class="section-title"><el-icon><Document /></el-icon>最新动态</span>
              <el-button text type="primary" @click="$router.push('/community')">查看更多</el-button>
            </div>
          </template>

          <div class="activity-list">
            <article v-for="post in recentPosts" :key="post.id" class="post-item" @click="$router.push(`/posts/${post.id}`)">
              <el-avatar class="post-avatar" :size="42" :src="resolveAvatarUrl(post.author_info?.avatar, post.author_info?.id)">
                {{ post.author_info?.username?.[0] || '匿' }}
              </el-avatar>
              <div class="post-content">
                <h4>{{ post.title }}</h4>
                <p>{{ post.content?.substring(0, 78) }}{{ post.content?.length > 78 ? '...' : '' }}</p>
                <div class="post-meta">
                  <span>{{ post.author_info?.username || '匿名用户' }}</span>
                  <span><el-icon><View /></el-icon>{{ post.view_count }}</span>
                  <span><el-icon><ChatDotRound /></el-icon>{{ post.comment_count }}</span>
                </div>
              </div>
            </article>
          </div>
        </el-card>

        <el-card class="section-card callout-section">
          <div class="callout-box">
            <span class="callout-eyebrow">下一步行动</span>
            <h3>不确定该从哪里开始？</h3>
            <p>你可以先浏览适合新手的植物，或者直接去问答区向达人发起提问。</p>
            <div class="callout-actions">
              <el-button @click="$router.push('/matching')">
                <el-icon><Connection /></el-icon>匹配达人
              </el-button>
              <el-button plain @click="$router.push('/questions')">
                <el-icon><QuestionFilled /></el-icon>去提问
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Search, TrendCharts, ChatDotRound, Document, View, Reading, QuestionFilled, Connection } from '@element-plus/icons-vue'
import api from '../utils/api'
import { PLACEHOLDER_PLANT_IMAGE, withPlantImage } from '../utils/plantImages'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const features = [
  {
    title: '植物百科',
    desc: '从品种信息到养护节奏，快速找到你要的植物资料。',
    link: '/plants',
    icon: Reading,
    color: '#3f7f4b',
    bg: 'linear-gradient(135deg, rgba(93, 162, 104, 0.2), rgba(93, 162, 104, 0.08))',
    tag: '知识库'
  },
  {
    title: '社区交流',
    desc: '像内容社区一样浏览养护心得、经验记录和生活分享。',
    link: '/community',
    icon: ChatDotRound,
    color: '#3c7fc9',
    bg: 'linear-gradient(135deg, rgba(77, 149, 231, 0.18), rgba(77, 149, 231, 0.08))',
    tag: '内容流'
  },
  {
    title: '问答互助',
    desc: '聚焦问题本身，快速收集解决方案和达人建议。',
    link: '/questions',
    icon: QuestionFilled,
    color: '#b88524',
    bg: 'linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.08))',
    tag: '互助区'
  },
  {
    title: '达人匹配',
    desc: '根据经验与需求匹配更合适的养护建议来源。',
    link: '/matching',
    icon: Connection,
    color: '#d46a50',
    bg: 'linear-gradient(135deg, rgba(245, 108, 108, 0.18), rgba(245, 108, 108, 0.08))',
    tag: '服务区'
  }
]

const popularPlants = ref([])
const topics = ref([])
const recentPosts = ref([])

const normalizeList = (data) => {
  if (Array.isArray(data)) return data
  return data?.results || []
}

const leadTopic = computed(() => topics.value[0] || null)
const leadPost = computed(() => recentPosts.value[0] || null)

const heroStats = computed(() => [
  { label: '热门植物', value: `${popularPlants.value.length || 0}+` },
  { label: '热议话题', value: `${topics.value.length || 0}+` },
  { label: '近期动态', value: `${recentPosts.value.length || 0}+` }
])

const getDifficultyType = (difficulty) => {
  const types = { easy: 'success', medium: 'warning', hard: 'danger' }
  return types[difficulty] || 'info'
}

const handleImageError = (event) => {
  if (event?.target && event.target.src !== window.location.origin + PLACEHOLDER_PLANT_IMAGE) {
    event.target.src = PLACEHOLDER_PLANT_IMAGE
  }
}

onMounted(async () => {
  try {
    const [plantsRes, topicsRes, postsRes] = await Promise.all([
      api.get('/api/plants/popular/'),
      api.get('/api/community/topics/?page_size=10'),
      api.get('/api/community/posts/?status=approved&page_size=6')
    ])

    popularPlants.value = normalizeList(plantsRes.data).slice(0, 6).map(withPlantImage)
    topics.value = normalizeList(topicsRes.data).slice(0, 8)
    recentPosts.value = normalizeList(postsRes.data).slice(0, 4)
  } catch (error) {
}
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.hero-main :deep(.el-card__body) {
  padding: 0;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) 360px;
  gap: 22px;
  padding: 28px;
  background:
    linear-gradient(135deg, rgba(245, 250, 246, 0.96), rgba(237, 244, 238, 0.86)),
    linear-gradient(135deg, rgba(77, 139, 87, 0.08), transparent 60%);
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 26px;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(77, 139, 87, 0.12);
  color: #376540;
  font-size: 13px;
  font-weight: 700;
}

.hero-copy h1 {
  margin-top: 18px;
  font-size: 42px;
  line-height: 1.12;
  color: #1d2d23;
  max-width: 760px;
}

.hero-copy p {
  margin-top: 16px;
  max-width: 680px;
  font-size: 16px;
  line-height: 1.8;
  color: #65766a;
}

.banner-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.hero-stat {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(56, 97, 64, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.hero-stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1f3126;
}

.hero-stat-label {
  display: block;
  margin-top: 6px;
  color: #708174;
  font-size: 13px;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-panel,
.floating-post {
  padding: 24px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.insight-panel {
  min-height: 170px;
}

.insight-label,
.floating-label,
.callout-eyebrow {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7a8b7e;
}

.insight-panel h3,
.floating-post h4,
.callout-box h3 {
  margin-top: 12px;
  color: #203226;
}

.insight-panel h3 {
  font-size: 22px;
}

.insight-panel p,
.floating-post p,
.callout-box p {
  margin-top: 10px;
  color: #6a7a6e;
  line-height: 1.7;
  font-size: 14px;
}

.hero-link {
  margin-top: 14px;
  border: none;
  background: transparent;
  padding: 0;
  color: #376540;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.floating-post {
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(240, 246, 241, 0.86));
}

.floating-post:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 34px rgba(31, 49, 38, 0.1);
}

.floating-meta,
.post-meta,
.plant-views {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: #7a8b7e;
  font-size: 13px;
}

.floating-meta {
  margin-top: 16px;
}

.floating-meta span,
.post-meta span,
.plant-views {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.feature-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(56, 97, 64, 0.08);
  box-shadow: 0 18px 38px rgba(31, 49, 38, 0.07);
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 44px rgba(31, 49, 38, 0.1);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-copy {
  flex: 1;
}

.feature-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.feature-head h3 {
  font-size: 17px;
  color: #1f3126;
}

.feature-tag {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(238, 245, 239, 0.95);
  color: #718275;
  font-size: 12px;
}

.feature-copy p {
  margin-top: 10px;
  color: #6d7f71;
  line-height: 1.7;
  font-size: 14px;
}

.home-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) 380px;
  gap: 22px;
}

.home-main,
.home-side {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.section-card :deep(.el-card__header) {
  padding: 22px 24px 16px;
}

.section-card :deep(.el-card__body) {
  padding: 22px 24px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.plants-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.plant-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(248, 251, 248, 0.9);
  border: 1px solid rgba(56, 97, 64, 0.08);
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.plant-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 32px rgba(31, 49, 38, 0.08);
}

.plant-image {
  width: 62px;
  height: 62px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(93, 162, 104, 0.18), rgba(93, 162, 104, 0.06));
}

.plant-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: inherit;
}

.plant-copy h4 {
  margin-top: 14px;
  font-size: 17px;
  color: #203226;
}

.plant-copy p {
  margin-top: 8px;
  color: #6c7d70;
  line-height: 1.6;
  min-height: 44px;
  font-size: 14px;
}

.plant-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.topic-pill {
  border: none;
  background: linear-gradient(135deg, rgba(247, 250, 247, 0.96), rgba(239, 246, 240, 0.9));
  padding: 12px 16px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.topic-pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 22px rgba(31, 49, 38, 0.08);
}

.topic-name {
  color: #27432e;
  font-weight: 600;
}

.topic-count {
  color: #7a8b7e;
  font-size: 12px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.post-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 20px;
  background: rgba(248, 251, 248, 0.92);
  border: 1px solid rgba(56, 97, 64, 0.08);
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(31, 49, 38, 0.08);
}

.post-avatar {
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

.post-content {
  flex: 1;
}

.post-content h4 {
  color: #223427;
  font-size: 15px;
}

.post-content p {
  margin-top: 8px;
  color: #67796b;
  font-size: 14px;
  line-height: 1.7;
}

.post-meta {
  margin-top: 12px;
}

.callout-box {
  padding: 4px 2px;
}

.callout-actions {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.empty-state {
  cursor: default;
}

@media (max-width: 1200px) {
  .feature-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .home-grid {
    grid-template-columns: 1fr;
  }

  .home-side {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  }
}

@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy h1 {
    font-size: 34px;
  }
}

@media (max-width: 768px) {
  .hero-grid {
    padding: 20px;
  }

  .hero-copy h1 {
    font-size: 28px;
  }

  .hero-stats,
  .feature-row,
  .plants-grid,
  .home-side {
    grid-template-columns: 1fr;
  }

  .feature-card,
  .post-item {
    padding: 16px;
  }

  .section-card :deep(.el-card__header),
  .section-card :deep(.el-card__body) {
    padding-left: 18px;
    padding-right: 18px;
  }

  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .banner-actions,
  .callout-actions {
    flex-direction: column;
  }

  .banner-actions :deep(.el-button),
  .callout-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>

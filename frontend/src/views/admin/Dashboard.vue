<template>
  <div class="page-container admin-dashboard">
    <div class="hero-panel">
      <div>
        <span class="hero-eyebrow">Admin Console</span>
        <h2 class="page-title">管理后台总控台</h2>
        <p class="hero-copy">管理员默认进入这里，集中处理植物百科、社区内容、匹配配置、用户与运营管理，不再先落到普通用户前台。</p>
      </div>
      <div class="hero-actions">
        <el-button @click="$router.push('/admin/plants')">植物百科</el-button>
        <el-button @click="$router.push('/admin/topics')">话题管理</el-button>
        <el-button type="primary" @click="$router.push('/admin/posts')">帖子审核</el-button>
        <el-button @click="$router.push('/admin/moderation')">问答评论</el-button>
        <el-button @click="$router.push('/admin/matching')">匹配管理</el-button>
        <el-button @click="$router.push('/admin/users')">用户管理</el-button>
        <el-button @click="$router.push('/admin/analytics')">运营统计</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="stat in statCards" :key="stat.label">
        <el-card class="stat-card">
          <el-icon :size="30" :color="stat.color"><component :is="stat.icon" /></el-icon>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="10">
        <el-card class="panel-card">
          <template #header><span>待处理事项</span></template>
          <div class="todo-list">
            <button type="button" class="todo-item" @click="$router.push('/admin/posts')">
              <div class="todo-info">
                <el-icon color="#e6a23c"><Document /></el-icon>
                <span>待审核帖子</span>
              </div>
              <el-badge :value="stats?.pending_posts || 0" type="warning" />
            </button>
            <button type="button" class="todo-item" @click="$router.push('/admin/moderation')">
              <div class="todo-info">
                <el-icon color="#409eff"><QuestionFilled /></el-icon>
                <span>问答与评论管理</span>
              </div>
              <span class="todo-text">{{ stats?.total_questions || 0 }} 个问题</span>
            </button>
            <button type="button" class="todo-item" @click="$router.push('/admin/experts')">
              <div class="todo-info">
                <el-icon color="#f56c6c"><Medal /></el-icon>
                <span>待审核达人申请</span>
              </div>
              <el-badge :value="stats?.pending_applications || 0" type="danger" />
            </button>
            <button type="button" class="todo-item" @click="$router.push('/admin/matching')">
              <div class="todo-info">
                <el-icon color="#7a5af8"><Connection /></el-icon>
                <span>匹配配置与概览</span>
              </div>
              <span class="todo-text">{{ stats?.match_success_rate || 0 }}%</span>
            </button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="panel-card">
          <template #header><span>管理模块</span></template>
          <div class="module-grid">
            <button v-for="item in managementModules" :key="item.title" type="button" class="module-card" @click="openModule(item)">
              <el-icon :size="28" :color="item.color"><component :is="item.icon" /></el-icon>
              <div class="module-copy">
                <span class="module-title">{{ item.title }}</span>
                <span class="module-desc">{{ item.desc }}</span>
              </div>
            </button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card section-gap">
      <template #header><span>Django Admin 系统入口</span></template>
      <div class="backend-grid">
        <button v-for="item in djangoAdminLinks" :key="item.title" type="button" class="backend-link" @click="openBackendAdmin(item.path)">
          <span class="backend-title">{{ item.title }}</span>
          <span class="backend-desc">{{ item.desc }}</span>
        </button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Medal, Document, QuestionFilled, TrendCharts, Connection, Reading, CollectionTag, DataLine } from '@element-plus/icons-vue'

import api from '../../utils/api'

const router = useRouter()
const stats = ref(null)
const backendOrigin = (import.meta.env.VITE_BACKEND_ORIGIN || `${window.location.protocol}//${window.location.hostname}:8001`).replace(/\/$/, '')

const djangoAdminBase = computed(() => `${backendOrigin}/admin`)

const statCards = computed(() => [
  { label: '总用户数', value: stats.value?.total_users || 0, icon: User, color: '#409eff' },
  { label: '认证达人', value: stats.value?.total_experts || 0, icon: Medal, color: '#e6a23c' },
  { label: '帖子总数', value: stats.value?.total_posts || 0, icon: Document, color: '#67c23a' },
  { label: '问题总数', value: stats.value?.total_questions || 0, icon: QuestionFilled, color: '#909399' },
  { label: '今日活跃', value: stats.value?.today_active_users || 0, icon: TrendCharts, color: '#f56c6c' },
  { label: '匹配成功率', value: `${stats.value?.match_success_rate || 0}%`, icon: Connection, color: '#7a5af8' }
])

const managementModules = [
  { title: '植物百科', desc: '维护植物资料、分类层级和植物标签。', icon: Reading, color: '#2d8a5c', route: '/admin/plants' },
  { title: '话题管理', desc: '维护社区话题、启用状态和基础信息。', icon: CollectionTag, color: '#1f8aa6', route: '/admin/topics' },
  { title: '帖子审核', desc: '处理通过、拒绝、置顶和精华设置。', icon: Document, color: '#67c23a', route: '/admin/posts' },
  { title: '问答评论', desc: '管理问题、回答和评论等公开互动内容。', icon: QuestionFilled, color: '#409eff', route: '/admin/moderation' },
  { title: '达人审核', desc: '审核认证申请并查看审核意见。', icon: Medal, color: '#e6a23c', route: '/admin/experts' },
  { title: '用户管理', desc: '查看用户角色、标签、注册时间和认证状态。', icon: User, color: '#409eff', route: '/admin/users' },
  { title: '匹配管理', desc: '查看请求概览并配置匹配标签权重。', icon: Connection, color: '#7a5af8', route: '/admin/matching' },
  { title: '运营统计', desc: '查看概览、趋势和近期活动。', icon: DataLine, color: '#f56c6c', route: '/admin/analytics' }
]

const djangoAdminLinks = [
  { title: '用户与权限', desc: '用户、标签与达人申请', path: 'users/' },
  { title: '植物百科', desc: '植物、分类与植物标签', path: 'plants/' },
  { title: '社区内容', desc: '话题、帖子、评论、问答、回答', path: 'community/' },
  { title: '匹配配置', desc: '匹配记录与标签权重配置', path: 'matching/' },
  { title: '数据分析', desc: '日统计与用户活动日志', path: 'analytics/' }
]

const openModule = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}

const openBackendAdmin = (path = '') => {
  window.open(`${djangoAdminBase.value}/${path}`, '_blank')
}

onMounted(async () => {
  try {
    const res = await api.get('/api/analytics/overview/')
    stats.value = res.data
  } catch (error) {
}
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-panel {
  margin-bottom: 4px;
  padding: 24px 26px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(245, 249, 246, 0.98), rgba(235, 242, 236, 0.92));
  border: 1px solid rgba(56, 97, 64, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.hero-eyebrow {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(77, 139, 87, 0.12);
  color: #355b3d;
  font-size: 12px;
  font-weight: 700;
}

.page-title {
  margin-top: 14px;
}

.hero-copy {
  margin-top: 10px;
  color: #6d7e71;
  max-width: 720px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-card__body) {
  padding: 18px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 10px 0 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.panel-card :deep(.el-card__body) {
  padding: 18px 20px 20px;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  background: #f7f9fb;
  cursor: pointer;
}

.todo-item:hover {
  background: #eef3f7;
}

.todo-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
}

.todo-text {
  color: #909399;
  font-size: 13px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.module-card {
  border: 1px solid #ebeef5;
  border-radius: 14px;
  background: #fff;
  padding: 16px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  cursor: pointer;
  text-align: left;
}

.module-card:hover {
  background: #f8fafc;
}

.module-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.module-title {
  font-weight: 700;
  color: #303133;
}

.module-desc {
  color: #909399;
  line-height: 1.6;
  font-size: 13px;
}

.section-gap {
  margin-top: 4px;
}

.backend-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.backend-link {
  border: 1px solid #ebeef5;
  border-radius: 14px;
  background: #fff;
  padding: 16px;
  text-align: left;
  cursor: pointer;
}

.backend-link:hover {
  background: #f8fafc;
}

.backend-title {
  display: block;
  font-weight: 700;
  color: #303133;
}

.backend-desc {
  display: block;
  margin-top: 8px;
  color: #909399;
  line-height: 1.6;
  font-size: 13px;
}

@media (max-width: 1300px) {
  .backend-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .hero-panel {
    flex-direction: column;
  }

  .module-grid,
  .backend-grid {
    grid-template-columns: 1fr;
  }
}
</style>

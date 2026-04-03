<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>运营统计</span></template>
    </el-page-header>

    <el-card class="toolbar-card">
      <div class="toolbar">
        <el-radio-group v-model="days" @change="fetchTrend">
          <el-radio-button v-for="option in trendPresetOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </el-radio-button>
        </el-radio-group>
        <div class="toolbar-actions">
          <el-button @click="fetchAllData" :loading="loading">刷新</el-button>
          <el-button type="primary" plain @click="generateToday" :loading="generating">生成今日统计</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16" class="overview-row">
      <el-col :span="6" v-for="item in overviewCards" :key="item.label">
        <el-card class="overview-card">
          <div class="overview-value">{{ item.value }}</div>
          <div class="overview-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card>
          <template #header><span>趋势数据</span></template>
          <el-table :data="trendRows" v-loading="loading" class="trend-table">
            <el-table-column prop="date" label="日期" min-width="120" />
            <el-table-column prop="newUsers" label="新增用户" min-width="100" />
            <el-table-column prop="activeUsers" label="活跃用户" min-width="100" />
            <el-table-column prop="posts" label="新增内容" min-width="100" />
            <el-table-column prop="interactions" label="互动量" min-width="100" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card>
          <template #header><span>最近活动</span></template>
          <div v-loading="activityLoading">
            <el-empty v-if="activities.length === 0" description="暂无活动记录" />
            <div v-for="activity in activities" :key="activity.id" class="activity-item">
              <div class="activity-main">
                <div class="activity-title">
                  <span>{{ getActivityUsername(activity) }}</span>
                  <el-tag size="small">{{ activity.action_display || activity.action }}</el-tag>
                </div>
                <div class="activity-desc">
                  {{ translateTargetType(activity.target_type) }} #{{ activity.target_id || '-' }}
                </div>
              </div>
              <div class="activity-time">{{ formatTime(activity.created_at) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'

const metaStore = useMetaStore()
const loading = ref(true)
const activityLoading = ref(true)
const generating = ref(false)
const overview = ref({})
const trend = ref({ dates: [], new_users: [], active_users: [], posts: [], interactions: [] })
const activities = ref([])
const days = ref(null)
const trendPresetOptions = computed(() => metaStore.trendPresets.map(value => ({
  value,
  label: `近${value}天`
})))

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')
const getActivityUsername = (activity) => activity.user_info?.username || activity.username || '未知用户'

const TARGET_TYPE_MAP = {
  post: '帖子', question: '问题', answer: '回答', comment: '评论',
  matchrecord: '匹配记录', matchrequest: '匹配请求',
  consultationsession: '咨询会话', consultationmessage: '咨询消息',
  user: '用户', plant: '植物', userplant: '用户植物',
}
const translateTargetType = (type) => TARGET_TYPE_MAP[type] || type || '系统'

const overviewCards = computed(() => [
  { label: '总用户数', value: overview.value.total_users || 0 },
  { label: '帖子总数', value: overview.value.total_posts || 0 },
  { label: '问题总数', value: overview.value.total_questions || 0 },
  { label: '匹配成功率', value: `${overview.value.match_success_rate || 0}%` }
])

const trendRows = computed(() => {
  const dates = trend.value.dates || []
  return dates.map((date, index) => ({
    date,
    newUsers: trend.value.new_users?.[index] || 0,
    activeUsers: trend.value.active_users?.[index] || 0,
    posts: trend.value.posts?.[index] || 0,
    interactions: trend.value.interactions?.[index] || 0
  })).reverse()
})

const fetchOverview = async () => {
  const res = await api.get('/api/analytics/overview/')
  overview.value = res.data
}

const fetchTrend = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/analytics/trend/', { params: { days: days.value } })
    trend.value = res.data
  } catch (error) {
} finally {
    loading.value = false
  }
}

const fetchActivities = async () => {
  activityLoading.value = true
  try {
    const res = await api.get('/api/analytics/activities/recent/?limit=12')
    activities.value = res.data.results || res.data
  } catch (error) {
} finally {
    activityLoading.value = false
  }
}

const fetchAllData = async () => {
  loading.value = true
  activityLoading.value = true
  try {
    const [overviewRes, trendRes, activityRes] = await Promise.all([
      api.get('/api/analytics/overview/'),
      api.get('/api/analytics/trend/', { params: { days: days.value } }),
      api.get('/api/analytics/activities/recent/?limit=12')
    ])
    overview.value = overviewRes.data
    trend.value = trendRes.data
    activities.value = activityRes.data.results || activityRes.data
  } catch (error) {
} finally {
    loading.value = false
    activityLoading.value = false
  }
}

const generateToday = async () => {
  generating.value = true
  try {
    await api.post('/api/analytics/daily-stats/generate_today/')
    ElMessage.success('今日统计已生成')
    await fetchAllData()
  } catch (error) {
    ElMessage.error('生成统计失败')
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  metaStore.fetchMetadata()
    .then(() => {
      if (!days.value && trendPresetOptions.value.length > 0) {
        days.value = trendPresetOptions.value[0].value
      }
    })
    .catch((error) => {
})
    .finally(() => {
      fetchAllData()
    })
})
</script>

<style scoped>
.toolbar-card {
  margin-top: 20px;
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.overview-row {
  margin-bottom: 16px;
}

.overview-card {
  text-align: center;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.overview-label {
  margin-top: 6px;
  color: #909399;
}

.trend-table :deep(.el-table__row td) {
  padding: 14px 0;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.activity-desc,
.activity-time {
  margin-top: 4px;
  color: #909399;
  font-size: 13px;
}

@media (max-width: 900px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-actions {
    justify-content: flex-end;
  }
}
</style>

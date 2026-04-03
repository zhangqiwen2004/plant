<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>帖子管理</span></template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <div class="filter-bar">
        <el-radio-group v-model="filter" @change="fetchPosts">
          <el-radio-button v-for="option in postStatusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <div class="summary-row">
      <el-card v-for="item in summaryCards" :key="item.label" class="summary-card">
        <div class="summary-value">{{ item.value }}</div>
        <div class="summary-label">{{ item.label }}</div>
      </el-card>
    </div>

    <el-card>
      <el-table :data="posts" v-loading="loading" style="width: 100%">
        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <el-icon v-if="row.is_top" color="#f56c6c"><Top /></el-icon>
              <el-icon v-if="row.is_essence" color="#e6a23c"><Star /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="author_info.username" label="作者" width="120" />
        <el-table-column prop="topic_name" label="话题" width="120">
          <template #default="{ row }">{{ row.topic_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display || getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="120">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button text type="primary" @click="$router.push(`/posts/${row.id}`)">查看</el-button>
              <template v-if="row.status === 'pending'">
                <el-button text type="success" @click="handleReview(row.id, 'approve')">通过</el-button>
                <el-button text type="danger" @click="handleReview(row.id, 'reject')">拒绝</el-button>
              </template>
              <template v-if="row.status === 'approved'">
                <el-button text :type="row.is_top ? 'danger' : 'default'" @click="handleToggleTop(row)">
                  {{ row.is_top ? '取消置顶' : '置顶' }}
                </el-button>
                <el-button text :type="row.is_essence ? 'warning' : 'default'" @click="handleToggleEssence(row)">
                  {{ row.is_essence ? '取消精华' : '精华' }}
                </el-button>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && posts.length === 0" description="暂无帖子" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Top, Star } from '@element-plus/icons-vue'
import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'
import dayjs from 'dayjs'

const metaStore = useMetaStore()
const posts = ref([])
const loading = ref(true)
const filter = ref('all')
const postStats = ref({})
const postStatusOptions = computed(() => [
  { value: 'all', label: '全部' },
  ...metaStore.postStatuses
])

const summaryCards = computed(() => [
  { label: '帖子总数', value: postStats.value.total || 0 },
  { label: '已通过', value: postStats.value.approved || 0 },
  { label: '待审核', value: postStats.value.pending || 0 },
  { label: '已拒绝', value: postStats.value.rejected || 0 },
  { label: '置顶', value: postStats.value.top || 0 },
  { label: '精华', value: postStats.value.essence || 0 },
])

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD')

const getStatusType = (status) => {
  const types = { approved: 'success', rejected: 'danger', pending: 'warning' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => postStatusOptions.value.find(option => option.value === status)?.label || status

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = filter.value !== 'all' ? `?status=${filter.value}` : ''
    const res = await api.get(`/api/community/posts/${params}`)
    posts.value = res.data.results || res.data
  } catch (error) {
} finally {
    loading.value = false
  }
}

const handleReview = async (postId, action) => {
  try {
    await api.post(`/api/community/posts/${postId}/review/`, { action })
    ElMessage.success(action === 'approve' ? '已通过' : '已拒绝')
    fetchPosts()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleToggleTop = async (post) => {
  try {
    const res = await api.post(`/api/community/posts/${post.id}/set_top/`)
    ElMessage.success(res.data.message)
    post.is_top = res.data.is_top
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleToggleEssence = async (post) => {
  try {
    const res = await api.post(`/api/community/posts/${post.id}/set_essence/`)
    ElMessage.success(res.data.message)
    post.is_essence = res.data.is_essence
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
  } catch (error) {
}
  fetchPosts()
  api.get('/api/community/posts/stats/').then(res => { postStats.value = res.data }).catch(() => {})
})
</script>

<style scoped>
.filter-bar {
  margin-bottom: 0;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.summary-card {
  text-align: center;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.summary-label {
  margin-top: 6px;
  color: #909399;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  white-space: nowrap;
}
</style>

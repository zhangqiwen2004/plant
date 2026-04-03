<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>达人审核</span></template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <div class="filter-bar">
        <el-radio-group v-model="filter" @change="fetchApplications">
          <el-radio-button v-for="option in expertStatusOptions" :key="option.value" :value="option.value">
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
      <div v-loading="loading">
        <el-card v-for="app in applications" :key="app.id" class="application-card">
          <div class="app-header">
            <div class="user-info">
              <el-avatar :size="50" :src="resolveAvatarUrl(app.user?.avatar, app.user?.id)">
                {{ app.user?.username?.[0] }}
              </el-avatar>
              <div>
                <h4>{{ app.user?.username }}</h4>
                <p>{{ app.user?.email }}</p>
              </div>
            </div>
            <el-tag :type="getStatusType(app.status)">{{ app.status_display }}</el-tag>
          </div>
          
          <div class="app-content">
            <div class="info-item">
              <span class="label">擅长领域</span>
              <span class="value">{{ app.specialty }}</span>
            </div>
            <div class="info-item">
              <span class="label">养护经验</span>
              <span class="value">{{ app.experience_desc }}</span>
            </div>
          </div>
          
          <div class="app-footer">
            <span class="time">申请时间：{{ formatTime(app.created_at) }}</span>
            <div v-if="app.status === 'pending'" class="actions">
              <el-button type="primary" @click="openReviewDialog(app)">审核</el-button>
            </div>
            <div v-else-if="app.review_comment" class="review-comment">
              审核意见：{{ app.review_comment }}
            </div>
          </div>
        </el-card>
        
        <el-empty v-if="!loading && applications.length === 0" :description="emptyDescription" />
      </div>
    </el-card>

    
    <el-dialog v-model="showReviewDialog" title="审核达人申请" width="450px">
      <div class="review-info">
        <p><strong>申请人：</strong>{{ selectedApp?.user?.username }}</p>
        <p><strong>擅长领域：</strong>{{ selectedApp?.specialty }}</p>
      </div>
      <el-form-item label="审核意见（可选）">
        <el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="输入审核意见..." />
      </el-form-item>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="danger" @click="handleReview('rejected')" :loading="submitting">拒绝</el-button>
        <el-button type="success" @click="handleReview('approved')" :loading="submitting">通过</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../utils/api'
import dayjs from 'dayjs'
import { useMetaStore } from '../../stores/meta'
import { resolveMediaUrl, resolveAvatarUrl } from '../../utils/media'

const metaStore = useMetaStore()
const applications = ref([])
const loading = ref(true)
const filter = ref('all')
const showReviewDialog = ref(false)
const selectedApp = ref(null)
const reviewComment = ref('')
const submitting = ref(false)
const expertStats = ref({})
const expertStatusOptions = computed(() => [
  { value: 'all', label: '全部' },
  ...metaStore.expertApplicationStatuses
])

const summaryCards = computed(() => [
  { label: '申请总数', value: expertStats.value.total || 0 },
  { label: '待审核', value: expertStats.value.pending || 0 },
  { label: '已通过', value: expertStats.value.approved || 0 },
  { label: '已拒绝', value: expertStats.value.rejected || 0 },
])

const activeStatusOption = computed(() => {
  return expertStatusOptions.value.find(option => option.value === filter.value) || expertStatusOptions.value[0]
})

const emptyDescription = computed(() => {
  if (activeStatusOption.value?.value === 'all') {
    return '当前还没有达人认证申请，普通用户可在个人中心提交申请'
  }
  return `当前没有“${activeStatusOption.value?.label || ''}”的达人申请`
})

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const getStatusType = (status) => {
  const types = { approved: 'success', rejected: 'danger', pending: 'warning' }
  return types[status] || 'info'
}

const fetchApplications = async () => {
  loading.value = true
  try {
    const params = filter.value !== 'all' ? `?status=${filter.value}` : ''
    const res = await api.get(`/api/users/expert-applications/${params}`)
    applications.value = res.data.results || res.data
  } catch (error) {
} finally {
    loading.value = false
  }
}

const openReviewDialog = (app) => {
  selectedApp.value = app
  reviewComment.value = ''
  showReviewDialog.value = true
}

const handleReview = async (status) => {
  submitting.value = true
  try {
    await api.post(`/api/users/expert-applications/${selectedApp.value.id}/review/`, {
      status,
      review_comment: reviewComment.value
    })
    ElMessage.success(status === 'approved' ? '已通过' : '已拒绝')
    showReviewDialog.value = false
    fetchApplications()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
  } catch (error) {
}
  fetchApplications()
  api.get('/api/users/expert-applications/stats/').then(res => { expertStats.value = res.data }).catch(() => {})
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

.application-card {
  margin-bottom: 15px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info h4 {
  margin: 0 0 5px;
}

.user-info p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.app-content {
  margin-bottom: 15px;
}

.info-item {
  margin-bottom: 10px;
}

.info-item .label {
  display: block;
  color: #909399;
  font-size: 13px;
  margin-bottom: 5px;
}

.info-item .value {
  color: #606266;
  white-space: pre-wrap;
}

.app-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.time {
  color: #909399;
  font-size: 13px;
}

.review-comment {
  color: #909399;
  font-size: 13px;
}

.review-info {
  margin-bottom: 20px;
}

.review-info p {
  margin: 10px 0;
}
</style>

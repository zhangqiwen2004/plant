<template>
  <div class="page-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>智能匹配</h2>
          <p class="subtitle">基于您的标签和偏好，为您推荐最合适的用户</p>
        </div>
        <div class="header-actions">
          <el-radio-group v-model="matchType" @change="fetchMatches">
            <el-radio-button v-for="option in matchModeOptions" :key="option.value" :value="option.value">
              <el-icon><component :is="option.value === 'experts' ? Medal : User" /></el-icon> {{ option.label }}
            </el-radio-button>
          </el-radio-group>
          <el-button :icon="Refresh" @click="refreshAll" :loading="loading || historyLoading">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-alert
      v-if="!userStore.user?.tags?.length"
      title="您还没有设置个人标签，匹配结果可能不够精准"
      type="warning"
      show-icon
      style="margin-bottom: 20px"
    >
      <template #default>
        <el-link type="primary" @click="$router.push('/profile')">去设置标签 →</el-link>
      </template>
    </el-alert>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="(match, index) in matches" :key="index">
        <el-card class="match-card">
          <div class="match-header">
            <el-avatar :size="60" :src="resolveAvatarUrl(match.user?.avatar, match.user?.id)">
              {{ match.user?.username?.[0] }}
            </el-avatar>
            <div class="match-info">
              <span class="match-name">
                {{ match.user?.username }}
                <el-tag v-if="match.user?.is_expert_verified" size="small" type="warning">达人</el-tag>
              </span>
              <span class="match-region">
                <el-icon><Location /></el-icon> {{ match.user?.region || '未设置' }}
              </span>
            </div>
            <div class="match-score">
              <span class="score">{{ Math.round(match.score * 100) }}%</span>
              <span class="label">匹配度</span>
            </div>
          </div>

          <p class="match-bio" v-if="match.user?.bio">{{ match.user.bio }}</p>

          <p class="match-specialty" v-if="match.user?.expert_specialty">
            <el-icon><Medal /></el-icon> 擅长：{{ match.user.expert_specialty }}
          </p>

          <div class="match-reason" v-if="match.match_reason">
            <el-icon><Star /></el-icon> {{ match.match_reason }}
          </div>

          <div class="match-tags" v-if="match.matched_tags?.length">
            <el-tag v-for="(tag, idx) in match.matched_tags.slice(0, 4)" :key="idx" size="small" type="success">
              {{ tag.value }}
            </el-tag>
          </div>

          <el-button
            :type="getContactStatus(match.user?.id).type"
            :disabled="getContactStatus(match.user?.id).disabled"
            style="width: 100%; margin-top: 15px"
            @click="getContactStatus(match.user?.id).status === 'accepted'
              ? openConsultation(getContactStatus(match.user?.id).consultationId)
              : handleContact(match.user)"
          >
            <el-icon><ChatDotRound /></el-icon> {{ getContactStatus(match.user?.id).label }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && matches.length === 0" description="暂无匹配结果，请完善您的个人标签" />

    <el-row :gutter="20" class="matching-secondary">
      <el-col :span="12">
        <el-card class="history-card" v-loading="historyLoading">
          <template #header>
            <div class="section-header">
              <span>近期匹配记录</span>
              <el-button text type="primary" @click="fetchMatchActivity">刷新</el-button>
            </div>
          </template>

          <el-empty v-if="matchRecords.length === 0" description="暂无匹配记录" />

          <div v-for="record in matchRecords" :key="record.id" class="record-item">
            <div class="record-main">
              <div>
                <div class="record-title">
                  {{ record.matched_user_info?.username || '未知用户' }}
                  <el-tag size="small" type="success">{{ record.match_type_display }}</el-tag>
                </div>
                <div class="record-desc">{{ record.match_reason || '系统已为你记录本次匹配结果。' }}</div>
              </div>
              <div class="record-score">{{ Math.round((record.similarity_score || 0) * 100) }}%</div>
            </div>
            <div class="record-footer">
              <span>{{ formatTime(record.created_at) }}</span>
              <el-tag size="small" :type="record.is_contacted ? 'success' : 'info'">
                {{ record.is_contacted ? '已建立联系' : '待联系' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="history-card" v-loading="historyLoading">
          <template #header>
            <div class="section-header">
              <span>联系请求</span>
              <span class="request-summary">收到 {{ receivedRequests.length }} / 发出 {{ sentRequests.length }}</span>
            </div>
          </template>

          <div class="request-group">
            <h4>收到的请求</h4>
            <el-empty v-if="receivedRequests.length === 0" description="暂无待处理请求" />
            <div v-for="request in receivedRequests" :key="`received-${request.id}`" class="request-item">
              <div class="request-main">
                <div class="request-title">{{ request.from_user_info?.username || '未知用户' }}</div>
                <div class="request-desc">{{ request.message || '希望与你建立联系' }}</div>
                <div class="request-time">{{ formatTime(request.created_at) }}</div>
              </div>
              <div class="request-actions">
                <el-button size="small" type="success" @click="handleAcceptRequest(request.id)">接受</el-button>
                <el-button size="small" @click="handleRejectRequest(request.id)">拒绝</el-button>
              </div>
            </div>
          </div>

          <div class="request-group">
            <h4>我发出的请求</h4>
            <el-empty v-if="sentRequests.length === 0" description="暂无已发送请求" />
            <div v-for="request in sentRequests" :key="`sent-${request.id}`" class="request-item compact">
              <div class="request-main">
                <div class="request-title">{{ request.to_user_info?.username || '未知用户' }}</div>
                <div class="request-desc">{{ request.message || '希望与你建立联系' }}</div>
                <div class="request-time">{{ formatTime(request.created_at) }}</div>
              </div>
              <div class="request-side">
                <el-tag size="small" :type="request.status === 'accepted' ? 'success' : request.status === 'rejected' ? 'danger' : 'warning'">
                  {{ request.status_display }}
                </el-tag>
                <el-button
                  v-if="request.consultation_id"
                  size="small"
                  text
                  type="primary"
                  @click="openConsultation(request.consultation_id)"
                >
                  进入咨询
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="consultation-card" v-loading="historyLoading">
      <template #header>
        <div class="section-header">
          <span>咨询会话</span>
          <span class="request-summary">进行中 {{ activeConsultationCount }} / 已完成 {{ completedConsultationCount }}</span>
        </div>
      </template>

      <el-empty v-if="consultations.length === 0" description="接受联系申请后，这里会自动建立咨询会话" />

      <div v-for="consultation in consultations" :key="consultation.id" class="consultation-item">
        <div class="consultation-user">
          <el-avatar :size="48" :src="resolveAvatarUrl(consultation.counterpart_info?.avatar, consultation.counterpart_info?.id)">
            {{ consultation.counterpart_info?.username?.[0] || 'U' }}
          </el-avatar>
          <div class="consultation-copy">
            <div class="consultation-title-row">
              <span class="consultation-name">{{ consultation.counterpart_info?.username }}</span>
              <el-tag size="small" :type="consultation.status === 'completed' ? 'info' : 'success'">
                {{ consultation.status_display }}
              </el-tag>
              <el-tag size="small" effect="plain">{{ consultation.match_type_display }}</el-tag>
            </div>
            <div class="consultation-preview">{{ consultation.last_message_preview || consultation.request_message || '暂无咨询消息' }}</div>
            <div class="consultation-meta">
              <span>建立时间 {{ formatTime(consultation.created_at) }}</span>
              <span>最近更新 {{ formatTime(consultation.last_message_at) }}</span>
            </div>
          </div>
        </div>

        <div class="consultation-actions">
          <el-button type="primary" @click="openConsultation(consultation.id)">
            {{ consultation.status === 'completed' ? '查看记录' : '继续咨询' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="showContactDialog" title="发送匹配请求" width="440px">
      <p>向 <strong>{{ selectedUser?.username }}</strong> 发送联系请求？</p>
      <template #footer>
        <el-button @click="showContactDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSendRequest" :loading="submitting">发送请求</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Medal, User, Refresh, Location, Star, ChatDotRound } from '@element-plus/icons-vue'

import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { useMetaStore } from '../stores/meta'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const router = useRouter()
const userStore = useUserStore()
const metaStore = useMetaStore()

const matches = ref([])
const matchRecords = ref([])
const receivedRequests = ref([])
const sentRequests = ref([])
const consultations = ref([])
const loading = ref(true)
const historyLoading = ref(false)
const matchType = ref('')
const showContactDialog = ref(false)
const selectedUser = ref(null)
const submitting = ref(false)

const matchModeOptions = computed(() => metaStore.matchModes)
const currentMatchMode = computed(() => {
  return matchModeOptions.value.find(option => option.value === matchType.value) || null
})
const activeConsultationCount = computed(() => consultations.value.filter(item => item.status === 'active').length)
const completedConsultationCount = computed(() => consultations.value.filter(item => item.status === 'completed').length)

// 已发送请求的用户ID -> 请求状态映射
const sentRequestMap = computed(() => {
  const map = {}
  for (const req of sentRequests.value) {
    map[req.to_user] = req
  }
  return map
})

// 获取匹配用户的联系状态
const getContactStatus = (userId) => {
  const req = sentRequestMap.value[userId]
  if (!req) return { status: 'none', label: '发起联系', type: 'primary', disabled: false }
  if (req.status === 'accepted') {
    return { status: 'accepted', label: '进入咨询', type: 'success', disabled: false, consultationId: req.consultation_id }
  }
  if (req.status === 'pending') {
    return { status: 'pending', label: '请求已发送', type: 'info', disabled: true }
  }
  if (req.status === 'rejected') {
    return { status: 'rejected', label: '已被拒绝', type: 'danger', disabled: true }
  }
  return { status: 'none', label: '发起联系', type: 'primary', disabled: false }
}

const formatTime = (time) => new Date(time).toLocaleString('zh-CN')
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])

const fetchMatches = async () => {
  if (!currentMatchMode.value?.api_value) {
    matches.value = []
    loading.value = false
    return
  }
  loading.value = true
  try {
    const res = await api.get('/api/matching/basic-results/', {
      params: {
        match_type: currentMatchMode.value.api_value
      }
    })
    matches.value = res.data.results || []
  } catch (error) {
ElMessage.error('获取匹配结果失败')
  } finally {
    loading.value = false
  }
}

const fetchMatchActivity = async () => {
  historyLoading.value = true
  try {
    const [recordsRes, receivedRes, sentRes, consultationsRes] = await Promise.all([
      api.get('/api/matching/records/'),
      api.get('/api/matching/requests/received/'),
      api.get('/api/matching/requests/sent/'),
      api.get('/api/matching/consultations/')
    ])
    matchRecords.value = normalizeList(recordsRes.data)
    receivedRequests.value = normalizeList(receivedRes.data)
    sentRequests.value = normalizeList(sentRes.data)
    consultations.value = normalizeList(consultationsRes.data)
  } catch (error) {
} finally {
    historyLoading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([fetchMatches(), fetchMatchActivity()])
}

const openConsultation = (consultationId) => {
  router.push(`/matching/consultations/${consultationId}`)
}

const handleContact = async (user) => {
  if (!currentMatchMode.value?.api_value) {
    ElMessage.error('匹配模式未初始化')
    return
  }
  selectedUser.value = user
  showContactDialog.value = true

  try {
    await api.post('/api/matching/find/save_match/', {
      matched_user_id: user.id,
      match_type: currentMatchMode.value.api_value
    })
    fetchMatchActivity()
  } catch (error) {
}
}

const handleSendRequest = async () => {
  submitting.value = true
  try {
    await api.post('/api/matching/requests/', {
      to_user: selectedUser.value.id,
      message: `你好，我是${userStore.user.username}，希望能向您请教植物养护问题。`
    })
    ElMessage.success('匹配请求已发送')
    showContactDialog.value = false
    fetchMatchActivity()
  } catch (error) {
    ElMessage.error('发送请求失败')
  } finally {
    submitting.value = false
  }
}

const handleAcceptRequest = async (requestId) => {
  try {
    const res = await api.post(`/api/matching/requests/${requestId}/accept/`)
    ElMessage.success('已接受请求')
    await fetchMatchActivity()
    if (res.data?.consultation_id) {
      openConsultation(res.data.consultation_id)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '操作失败')
  }
}

const handleRejectRequest = async (requestId) => {
  try {
    await api.post(`/api/matching/requests/${requestId}/reject/`)
    ElMessage.success('已拒绝请求')
    fetchMatchActivity()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '操作失败')
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
    if (!matchType.value && matchModeOptions.value.length > 0) {
      matchType.value = matchModeOptions.value[0].value
    }
  } catch (error) {
}
  refreshAll()
})
</script>

<style scoped>
.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0 0 5px;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.matching-secondary {
  margin-top: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.request-summary {
  color: #909399;
  font-size: 13px;
}

.match-card,
.history-card,
.consultation-card {
  margin-bottom: 20px;
}

.record-item,
.request-item,
.consultation-item {
  padding: 14px 0;
  border-bottom: 1px solid #ebeef5;
}

.record-item:last-child,
.request-item:last-child,
.consultation-item:last-child {
  border-bottom: none;
}

.record-main,
.request-item,
.consultation-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.request-main,
.consultation-copy {
  flex: 1;
  min-width: 0;
}

.record-title,
.request-title,
.consultation-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  flex-wrap: wrap;
}

.record-desc,
.request-desc,
.consultation-preview {
  margin-top: 6px;
  color: #606266;
  line-height: 1.6;
  font-size: 13px;
}

.record-score {
  font-size: 22px;
  font-weight: 700;
  color: #67c23a;
}

.record-footer,
.request-time,
.consultation-meta {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}

.record-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.request-group + .request-group {
  margin-top: 20px;
}

.request-group h4 {
  margin: 0 0 10px;
  color: #303133;
}

.request-actions,
.request-side,
.consultation-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.request-item.compact {
  align-items: center;
}

.consultation-user {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
}

.consultation-name {
  font-size: 15px;
}

.consultation-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.match-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.match-info {
  flex: 1;
  margin-left: 15px;
}

.match-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 16px;
}

.match-region {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
}

.match-score {
  text-align: center;
}

.match-score .score {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
}

.match-score .label {
  font-size: 12px;
  color: #909399;
}

.match-bio {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
}

.match-specialty {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #67c23a;
  font-size: 13px;
  margin-bottom: 10px;
}

.match-reason {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
}

.match-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

@media (max-width: 900px) {
  .header-content,
  .header-actions,
  .record-main,
  .request-item,
  .consultation-item {
    flex-direction: column;
  }

  .consultation-user {
    width: 100%;
  }
}
</style>

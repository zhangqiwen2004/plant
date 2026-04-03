<template>
  <div class="page-container consultation-page" v-loading="loading">
    <el-page-header @back="router.push('/matching')" title="返回匹配中心">
      <template #content><span>咨询会话</span></template>
    </el-page-header>

    <div v-if="consultation" class="consultation-layout">
      <section class="consultation-main">
        <el-card class="consultation-hero">
          <div class="hero-row">
            <div class="hero-user">
              <el-avatar :size="64" :src="resolveAvatarUrl(counterpartInfo?.avatar, counterpartInfo?.id)">
                {{ counterpartInfo?.username?.[0] || 'U' }}
              </el-avatar>
              <div class="hero-copy">
                <div class="hero-name-row">
                  <h2>{{ counterpartInfo?.username }}</h2>
                  <el-tag v-if="counterpartInfo?.is_expert_verified" size="small" type="warning">达人</el-tag>
                  <el-tag :type="isCompleted ? 'info' : 'success'">{{ consultation.status_display }}</el-tag>
                </div>
                <p class="hero-bio">{{ counterpartInfo?.bio || '对方暂时没有填写个人简介。' }}</p>
                <p v-if="counterpartInfo?.expert_specialty" class="hero-specialty">擅长：{{ counterpartInfo.expert_specialty }}</p>
              </div>
            </div>

            <div class="hero-actions">
              <el-button :icon="RefreshRight" @click="fetchConsultation(true)">刷新</el-button>
              <el-button v-if="consultation.can_complete && !isCompleted" type="danger" plain @click="handleComplete">
                结束咨询
              </el-button>
            </div>
          </div>

          <div class="hero-request">
            <span class="label">申请留言</span>
            <p>{{ consultation.request_message || '发起方没有填写额外说明。' }}</p>
          </div>
        </el-card>

        <el-card class="messages-card">
          <template #header>
            <div class="section-header">
              <span>咨询记录</span>
              <span class="section-subtitle">系统采用轮询刷新，消息会自动同步</span>
            </div>
          </template>

          <div ref="messagesContainer" class="messages-container">
            <div
              v-for="message in consultation.messages"
              :key="message.id"
              :class="[
                'message-row',
                message.message_type === 'system'
                  ? 'system'
                  : message.sender_info?.id === userStore.user?.id
                    ? 'mine'
                    : 'other'
              ]"
            >
              <template v-if="message.message_type === 'system'">
                <div class="system-badge">{{ message.content }}</div>
              </template>

              <template v-else>
                <el-avatar class="message-avatar" :size="38" :src="resolveAvatarUrl(message.sender_info?.avatar, message.sender_info?.id)">
                  {{ message.sender_info?.username?.[0] || 'U' }}
                </el-avatar>
                <div class="message-bubble-wrap">
                  <div class="message-meta">
                    <span>{{ message.sender_info?.username }}</span>
                    <span>{{ formatTime(message.created_at) }}</span>
                  </div>
                  <div class="message-bubble">{{ message.content }}</div>
                </div>
              </template>
            </div>
          </div>

          <div v-if="consultation.can_send_message" class="composer">
            <el-input
              v-model="messageForm.content"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="继续交流植物养护问题、场景和处理建议..."
              maxlength="1000"
              show-word-limit
            />
            <div class="composer-actions">
              <span class="composer-tip">请直接在站内继续交流，不需要额外交换联系方式。</span>
              <el-button type="primary" :loading="sending" @click="handleSendMessage">
                发送消息
              </el-button>
            </div>
          </div>

          <el-alert
            v-else
            title="咨询已结束，当前会话已转为只读。"
            type="info"
            show-icon
          />
        </el-card>
      </section>

      <aside class="consultation-side">
        <el-card class="summary-card">
          <template #header><span>会话信息</span></template>
          <div class="summary-item">
            <span class="label">咨询类型</span>
            <span class="value">{{ consultation.match_type_display }}</span>
          </div>
          <div class="summary-item">
            <span class="label">建立时间</span>
            <span class="value">{{ formatTime(consultation.created_at) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">最近更新</span>
            <span class="value">{{ formatTime(consultation.last_message_at) }}</span>
          </div>
          <div class="summary-item" v-if="consultation.completed_at">
            <span class="label">结束时间</span>
            <span class="value">{{ formatTime(consultation.completed_at) }}</span>
          </div>
        </el-card>

        <el-card class="feedback-card">
          <template #header><span>咨询反馈</span></template>

          <div v-if="canSubmitFeedback" class="feedback-form">
            <div class="feedback-label">请为本次咨询打分</div>
            <el-rate v-model="feedbackForm.feedback" />
            <el-input
              v-model="feedbackForm.comment"
              type="textarea"
              :rows="4"
              resize="none"
              maxlength="300"
              show-word-limit
              placeholder="补充一下这次沟通是否有帮助..."
            />
            <el-button type="primary" :loading="submittingFeedback" @click="handleSubmitFeedback">
              提交反馈
            </el-button>
          </div>

          <div v-else-if="existingFeedback" class="feedback-result">
            <div class="feedback-label">你已提交反馈</div>
            <el-rate :model-value="existingFeedback.feedback" disabled />
            <p>{{ existingFeedback.comment || '未填写额外说明。' }}</p>
          </div>

          <div v-else class="feedback-placeholder">
            <p v-if="isCompleted">当前没有可提交的反馈记录。</p>
            <p v-else>咨询结束后，可在这里提交本次沟通反馈。</p>
          </div>
        </el-card>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const consultation = ref(null)
const loading = ref(true)
const sending = ref(false)
const completing = ref(false)
const submittingFeedback = ref(false)
const messageForm = ref({ content: '' })
const feedbackForm = ref({ feedback: 0, comment: '' })
const messagesContainer = ref(null)

let pollTimer = null

const consultationId = computed(() => route.params.id)
const counterpartInfo = computed(() => consultation.value?.counterpart_info || null)
const isCompleted = computed(() => consultation.value?.status === 'completed')
const existingFeedback = computed(() => {
  if (!consultation.value?.current_feedback) return null
  return {
    feedback: consultation.value.current_feedback,
    comment: consultation.value.current_feedback_comment || ''
  }
})
const canSubmitFeedback = computed(() => {
  return Boolean(
    isCompleted.value &&
    consultation.value?.current_record_id &&
    !consultation.value?.current_feedback
  )
})

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const fetchConsultation = async (scrollAfter = false) => {
  loading.value = true
  try {
    const res = await api.get(`/api/matching/consultations/${consultationId.value}/`)
    consultation.value = res.data
    if (scrollAfter) {
      await scrollToBottom()
    }
  } catch (error) {
ElMessage.error('获取咨询会话失败')
    router.push('/matching')
  } finally {
    loading.value = false
  }
}

const handleSendMessage = async () => {
  const content = messageForm.value.content.trim()
  if (!content) {
    ElMessage.warning('请输入消息内容')
    return
  }

  sending.value = true
  try {
    await api.post(`/api/matching/consultations/${consultationId.value}/send_message/`, { content })
    messageForm.value.content = ''
    await fetchConsultation(true)
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.response?.data?.content?.[0] || '发送消息失败')
  } finally {
    sending.value = false
  }
}

const handleComplete = async () => {
  try {
    await ElMessageBox.confirm('结束后会话将变为只读，确认结束本次咨询吗？', '结束咨询', {
      confirmButtonText: '确认结束',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  completing.value = true
  try {
    const res = await api.post(`/api/matching/consultations/${consultationId.value}/complete/`)
    consultation.value = res.data
    ElMessage.success('咨询已结束')
    await scrollToBottom()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '结束咨询失败')
  } finally {
    completing.value = false
  }
}

const handleSubmitFeedback = async () => {
  if (!feedbackForm.value.feedback) {
    ElMessage.warning('请先给出评分')
    return
  }

  submittingFeedback.value = true
  try {
    await api.post(`/api/matching/records/${consultation.value.current_record_id}/feedback/`, {
      feedback: feedbackForm.value.feedback,
      comment: feedbackForm.value.comment.trim()
    })
    ElMessage.success('反馈已提交')
    await fetchConsultation(false)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交反馈失败')
  } finally {
    submittingFeedback.value = false
  }
}

onMounted(async () => {
  await fetchConsultation(true)
  pollTimer = setInterval(() => {
    fetchConsultation(false)
  }, 8000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})
</script>

<style scoped>
.consultation-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.consultation-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) 320px;
  gap: 18px;
  margin-top: 18px;
}

.consultation-main,
.consultation-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.consultation-hero {
  background: linear-gradient(135deg, rgba(246, 250, 247, 0.98), rgba(236, 244, 237, 0.92));
}

.hero-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.hero-user {
  display: flex;
  gap: 16px;
  min-width: 0;
}

.hero-copy {
  min-width: 0;
}

.hero-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-name-row h2 {
  margin: 0;
  color: #203226;
}

.hero-bio {
  margin-top: 10px;
  color: #637667;
  line-height: 1.7;
}

.hero-specialty {
  margin-top: 10px;
  color: #4d8b57;
  font-size: 14px;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.hero-request {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(56, 97, 64, 0.08);
}

.hero-request .label,
.summary-item .label,
.feedback-label {
  display: block;
  font-size: 12px;
  color: #86968a;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.hero-request p {
  margin-top: 10px;
  color: #445647;
  line-height: 1.7;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.section-subtitle {
  font-size: 12px;
  color: #909399;
}

.messages-container {
  max-height: 560px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-right: 6px;
}

.message-row {
  display: flex;
  gap: 10px;
}

.message-row.mine {
  flex-direction: row-reverse;
}

.message-row.system {
  justify-content: center;
}

.system-badge {
  padding: 8px 14px;
  border-radius: 999px;
  background: #f5f7fa;
  color: #7c8d80;
  font-size: 12px;
}

.message-bubble-wrap {
  max-width: min(76%, 620px);
}

.message-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.message-row.mine .message-meta {
  justify-content: flex-end;
}

.message-bubble {
  padding: 14px 16px;
  border-radius: 18px;
  background: #f5f7fa;
  color: #2f3b31;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.mine .message-bubble {
  background: linear-gradient(135deg, #4d8b57 0%, #2f6739 100%);
  color: #ffffff;
}

.composer {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.composer-actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.composer-tip {
  font-size: 12px;
  color: #909399;
}

.summary-card,
.feedback-card {
  position: sticky;
  top: 94px;
}

.feedback-card {
  top: 300px;
}

.summary-item + .summary-item {
  margin-top: 14px;
}

.summary-item .value {
  display: block;
  margin-top: 8px;
  color: #334236;
  line-height: 1.6;
}

.feedback-form,
.feedback-result,
.feedback-placeholder {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feedback-result p,
.feedback-placeholder p {
  color: #606266;
  line-height: 1.7;
  margin: 0;
}

@media (max-width: 1100px) {
  .consultation-layout {
    grid-template-columns: 1fr;
  }

  .summary-card,
  .feedback-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .hero-row,
  .hero-user,
  .composer-actions,
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .message-bubble-wrap {
    max-width: 100%;
  }
}
</style>

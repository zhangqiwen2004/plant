<template>
  <div class="page-container questions-page">
    <section class="questions-hero">
      <el-card class="hero-card">
        <div class="hero-layout">
          <div class="hero-copy">
            <div>
              <span class="hero-eyebrow">问答中心</span>
              <h1>植物养护问答</h1>
              <p>遇到养护难题？在这里提问，社区达人和热心花友会帮你解答。</p>
            </div>

            <div>
              <div class="hero-actions">
                <el-radio-group v-model="filter" @change="handleFilterChange" class="filter-group">
                  <el-radio-button v-for="option in questionStatusOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </el-radio-button>
                </el-radio-group>

                <el-button type="primary" :icon="Plus" @click="userStore.isLoggedIn ? showCreateDialog = true : $router.push('/login')">
                  {{ userStore.isLoggedIn ? '我要提问' : '登录后提问' }}
                </el-button>
              </div>

              <div class="hero-stats">
                <div v-for="item in questionStats" :key="item.label" class="hero-stat-item">
                  <span class="hero-stat-value">{{ item.value }}</span>
                  <span class="hero-stat-label">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </section>

    <div class="question-list" v-loading="loading">
      <article v-for="question in questions" :key="question.id" class="question-card" @click="$router.push(`/questions/${question.id}`)">
        <div class="question-status" :class="question.status === 'answered' ? 'answered' : 'pending'">
          <el-icon :size="22">
            <CircleCheckFilled v-if="question.status === 'answered'" />
            <QuestionFilled v-else />
          </el-icon>
        </div>

        <div class="question-content">
          <div class="question-header">
            <div class="question-tags">
              <el-tag v-if="question.is_urgent" type="danger" size="small">紧急</el-tag>
              <el-tag v-if="question.plant_type" size="small" effect="plain"># {{ question.plant_type }}</el-tag>
            </div>
            <el-tag :type="question.status === 'answered' ? 'success' : 'warning'">
              {{ question.status_display }}
            </el-tag>
          </div>

          <h3>{{ question.title }}</h3>
          <p class="question-desc">{{ getQuestionExcerpt(question.content) }}</p>

          <div class="question-meta">
            <span>{{ question.author_info?.username || '匿名用户' }}</span>
            <span>{{ formatTime(question.created_at) }}</span>
            <span><el-icon><View /></el-icon>{{ question.view_count }}</span>
            <span><el-icon><ChatDotRound /></el-icon>{{ question.answer_count }} 回答</span>
          </div>
        </div>
      </article>

      <el-empty v-if="!loading && questions.length === 0" description="暂无问题" />
    </div>

    <div class="pagination-wrap" v-if="questionsTotal > questionPageSize">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :total="questionsTotal"
        :page-size="questionPageSize"
        :current-page="questionPage"
        @current-change="handleQuestionPageChange"
      />
    </div>

    
    <el-dialog v-model="showCreateDialog" title="提出问题" width="620px" @closed="resetQuestionForm">
      <el-form :model="questionForm" :rules="questionRules" ref="questionFormRef">
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="questionForm.title" placeholder="简明扼要地描述你的问题" />
        </el-form-item>
        <el-form-item label="植物类型" prop="plant_type">
          <el-input v-model="questionForm.plant_type" placeholder="如：绿萝、多肉、月季等（可选）" />
        </el-form-item>
        <el-form-item label="问题描述" prop="content">
          <el-input v-model="questionForm.content" type="textarea" :rows="6" placeholder="详细描述你遇到的问题..." />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="questionForm.is_urgent">标记为紧急问题</el-checkbox>
        </el-form-item>
        <el-form-item label="问题图片">
          <el-upload
            v-model:file-list="questionImageFiles"
            :auto-upload="false"
            list-type="picture-card"
            multiple
            accept="image/*"
            :limit="6"
            :before-upload="beforeQuestionImageUpload"
            :on-exceed="handleQuestionFileExceed"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-helper">支持上传问题现场图片，单张不超过 5MB，最多 6 张。</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateQuestion" :loading="submitting">提交问题</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, CircleCheckFilled, QuestionFilled, View, ChatDotRound } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { useMetaStore } from '../stores/meta'
import dayjs from 'dayjs'

const userStore = useUserStore()
const metaStore = useMetaStore()
const questions = ref([])
const loading = ref(true)
const filter = ref('all')
const showCreateDialog = ref(false)
const submitting = ref(false)
const questionFormRef = ref(null)
const questionImageFiles = ref([])
const questionsTotal = ref(0)
const questionPage = ref(1)
const questionPageSize = 10

const questionForm = ref({ title: '', content: '', plant_type: '', is_urgent: false })
const questionRules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }],
  content: [{ required: true, message: '请描述你的问题', trigger: 'blur' }]
}

const questionStatusOptions = computed(() => [
  {
    value: 'all',
    label: '全部',
    title: '全部问题',
    description: '这里汇总所有公开问题，方便你浏览、提问和参与回答。'
  },
  ...metaStore.questionStatuses.map(option => ({
    ...option,
    title: `${option.label}问题`,
    description: `这里展示当前状态为“${option.label}”的问题列表。`
  }))
])

const activeQuestionFilter = computed(() => {
  return questionStatusOptions.value.find(option => option.value === filter.value) || questionStatusOptions.value[0]
})

const activeFilterLabel = computed(() => activeQuestionFilter.value?.title || '全部问题')
const activeFilterDescription = computed(() => {
  return activeQuestionFilter.value?.description || '这里汇总所有公开问题，方便你浏览、提问和参与回答。'
})

const questionStats = computed(() => [
  { label: '当前问题', value: questionsTotal.value || 0 },
  { label: '筛选状态', value: activeFilterLabel.value },
  { label: '互动方向', value: userStore.isLoggedIn ? '可参与' : '先登录' }
])

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD')
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : (data?.results?.length || 0))

const getQuestionExcerpt = (content = '', limit = 160) => {
  if (!content) return '提问者暂时没有补充更多问题背景。'
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

const beforeQuestionImageUpload = (file) => {
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

const handleQuestionFileExceed = () => {
  ElMessage.warning('最多上传 6 张图片')
}

const validateQuestionImages = () => {
  for (const file of questionImageFiles.value) {
    const rawFile = file.raw || file
    if (!beforeQuestionImageUpload(rawFile)) {
      return false
    }
  }
  return true
}

const resetQuestionForm = () => {
  questionForm.value = { title: '', content: '', plant_type: '', is_urgent: false }
  questionImageFiles.value = []
}

const buildQuestionPayload = () => {
  const formData = new FormData()
  formData.append('title', questionForm.value.title)
  formData.append('content', questionForm.value.content)
  if (questionForm.value.plant_type) {
    formData.append('plant_type', questionForm.value.plant_type)
  }
  formData.append('is_urgent', String(questionForm.value.is_urgent))
  questionImageFiles.value.forEach(file => {
    if (file.raw) {
      formData.append('uploaded_images', file.raw)
    }
  })
  return formData
}

const fetchQuestions = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', String(questionPage.value))
    params.append('page_size', String(questionPageSize))
    if (filter.value !== 'all') params.append('status', filter.value)
    
    const res = await api.get(`/api/community/questions/?${params.toString()}`)
    questions.value = normalizeList(res.data)
    questionsTotal.value = getListTotal(res.data)
  } catch (error) {
} finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  questionPage.value = 1
  fetchQuestions()
}

const handleQuestionPageChange = (page) => {
  questionPage.value = page
  fetchQuestions()
}

const handleCreateQuestion = async () => {
  const valid = await questionFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!validateQuestionImages()) return
  
  submitting.value = true
  try {
    await api.post('/api/community/questions/', buildQuestionPayload())
    ElMessage.success('提问成功')
    showCreateDialog.value = false
    resetQuestionForm()
    questionPage.value = 1
    fetchQuestions()
  } catch (error) {
    ElMessage.error(getRequestErrorMessage(error, '提问失败'))
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
  } catch (error) {
}
  fetchQuestions()
})
</script>

<style scoped>
.questions-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.hero-card :deep(.el-card__body) {
  padding: 0;
}

.hero-layout {
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

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #708174;
}

.hero-copy h1 {
  margin-top: 12px;
  font-size: 28px;
  line-height: 1.3;
  color: #1d2d23;
}

.hero-copy p {
  margin-top: 8px;
  color: #67786b;
  font-size: 15px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.filter-group :deep(.el-radio-button__inner) {
  border-radius: 999px !important;
  padding-left: 16px;
  padding-right: 16px;
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
  line-height: 1.1;
  font-weight: 700;
  color: #203226;
}

.hero-stat-label {
  display: block;
  margin-top: 8px;
  color: #758679;
  font-size: 13px;
}

.upload-helper {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
}

.question-card {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(56, 97, 64, 0.08);
  box-shadow: 0 18px 34px rgba(31, 49, 38, 0.08);
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.question-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 42px rgba(31, 49, 38, 0.11);
}

.question-status {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.question-status.answered {
  background: rgba(103, 194, 58, 0.16);
  color: #3b7e2c;
}

.question-status.pending {
  background: rgba(230, 162, 60, 0.16);
  color: #ae6d18;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.question-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.question-content h3 {
  margin-top: 14px;
  font-size: 22px;
  line-height: 1.35;
  color: #1d2d23;
}

.question-desc {
  margin-top: 12px;
  color: #67786b;
  font-size: 15px;
  line-height: 1.8;
}

.question-meta {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  color: #7f8f82;
  font-size: 13px;
}

.question-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
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
  .question-card {
    padding: 20px;
  }

  .hero-actions,
  .question-card,
  .question-header,
  .hero-stats {
    flex-direction: column;
  }

  .hero-stats {
    display: grid;
    grid-template-columns: 1fr;
  }

  .hero-actions {
    align-items: stretch;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }

  .question-content h3 {
    font-size: 19px;
  }
}
</style>

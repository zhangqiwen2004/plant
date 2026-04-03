<template>
  <div class="page-container" v-loading="loading">
    <el-page-header @back="$router.push('/questions')" title="返回问答" />
    
    <el-card v-if="question" class="question-card">
      <div class="question-badges">
        <el-tag v-if="question.is_urgent" type="danger">紧急</el-tag>
        <el-tag :type="question.status === 'answered' ? 'success' : 'warning'">
          {{ question.status_display }}
        </el-tag>
      </div>
      
      <h1 class="question-title">{{ question.title }}</h1>
      
      <div class="question-meta">
        <span>{{ question.author_info?.username }}</span>
        <span>{{ formatTime(question.created_at) }}</span>
        <el-tag v-if="question.plant_type" size="small" type="info"># {{ question.plant_type }}</el-tag>
      </div>
      
      <div class="question-content">{{ question.content }}</div>

      <div v-if="question.images?.length" class="question-gallery">
        <img v-for="(image, index) in question.images" :key="`${question.id}-image-${index}`" :src="image" :alt="question.title" />
      </div>
    </el-card>

    <el-card v-if="question" class="answers-card">
      <template #header>
        <span>回答 ({{ question.answer_count || answersTotal }})</span>
      </template>
      
      <div v-if="userStore.isLoggedIn && question.status !== 'closed'" class="answer-input">
        <el-input v-model="newAnswer" type="textarea" :rows="4" placeholder="分享你的养护经验，帮助提问者解决问题..." />
        <el-button type="primary" @click="handleAnswer" :loading="submitting" style="margin-top: 10px">
          提交回答
        </el-button>
      </div>
      
      <el-divider v-if="userStore.isLoggedIn && question.status !== 'closed'" />
      
      <el-empty v-if="answers.length === 0" description="暂无回答，快来分享你的经验吧~" />
      
      <div v-for="answer in answers" :key="answer.id" class="answer-item" :class="{ accepted: answer.is_accepted }">
        <div v-if="answer.is_accepted" class="accepted-badge">
          <el-icon><CircleCheckFilled /></el-icon> 最佳答案
        </div>
        
        <div class="answer-header">
          <el-avatar :size="45" :src="resolveAvatarUrl(answer.author_info?.avatar, answer.author_info?.id)">
            {{ answer.author_info?.username?.[0] }}
          </el-avatar>
          <div class="answer-author">
            <span class="author-name">
              {{ answer.author_info?.username }}
              <el-tag v-if="answer.author_info?.is_expert" size="small" type="warning">达人</el-tag>
            </span>
            <span class="answer-time">{{ formatTime(answer.created_at) }}</span>
          </div>
        </div>
        
        <div class="answer-content">{{ answer.content }}</div>
        
        <div class="answer-actions">
          <el-button :icon="Star" text :type="answer.is_liked ? 'warning' : 'default'" @click="handleLikeAnswer(answer)">
            {{ answer.like_count }} 赞同
          </el-button>
          <el-button 
            v-if="isAuthor && !answer.is_accepted && question.status !== 'answered'" 
            :icon="CircleCheckFilled" 
            text 
            type="success"
            @click="handleAccept(answer.id)"
          >
            采纳为最佳答案
          </el-button>
        </div>
      </div>

      <div class="pagination-wrap" v-if="answersTotal > answerPageSize">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="answersTotal"
          :page-size="answerPageSize"
          :current-page="answerPage"
          @current-change="handleAnswerPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, CircleCheckFilled } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import dayjs from 'dayjs'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const route = useRoute()
const userStore = useUserStore()
const question = ref(null)
const answers = ref([])
const loading = ref(true)
const newAnswer = ref('')
const submitting = ref(false)
const answersTotal = ref(0)
const answerPage = ref(1)
const answerPageSize = 10

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const isAuthor = computed(() => userStore.user?.id === question.value?.author_info?.id)
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : (data?.results?.length || 0))

const fetchAnswers = async () => {
  const res = await api.get(`/api/community/answers/?question=${route.params.id}&page=${answerPage.value}&page_size=${answerPageSize}`)
  answers.value = normalizeList(res.data)
  answersTotal.value = getListTotal(res.data)
}

const handleAnswerPageChange = (page) => {
  answerPage.value = page
  fetchAnswers()
}

const handleAnswer = async () => {
  if (!newAnswer.value.trim()) {
    ElMessage.warning('请输入回答内容')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/api/community/answers/', {
      question: route.params.id,
      content: newAnswer.value
    })
    ElMessage.success('回答成功')
    newAnswer.value = ''

    answerPage.value = 1
    await fetchAnswers()
    question.value.answer_count++
  } catch (error) {
    ElMessage.error('回答失败')
  } finally {
    submitting.value = false
  }
}

const handleLikeAnswer = async (answer) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    await api.post(`/api/community/answers/${answer.id}/like/`)
    answer.like_count++
    answer.is_liked = true
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleAccept = async (answerId) => {
  try {
    await api.post(`/api/community/answers/${answerId}/accept/`)
    ElMessage.success('已采纳该回答')
    
    answers.value = answers.value.map(a => ({ ...a, is_accepted: a.id === answerId }))
    question.value.status = 'answered'
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '操作失败')
  }
}

onMounted(async () => {
  try {
    const [questionRes, answersRes] = await Promise.all([
      api.get(`/api/community/questions/${route.params.id}/`),
      api.get(`/api/community/answers/?question=${route.params.id}&page=${answerPage.value}&page_size=${answerPageSize}`)
    ])
    question.value = questionRes.data
    answers.value = normalizeList(answersRes.data)
    answersTotal.value = getListTotal(answersRes.data)
  } catch (error) {
    ElMessage.error('获取问题失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.question-card {
  margin: 20px 0;
}

.question-badges {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.question-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 15px;
}

.question-meta {
  display: flex;
  gap: 15px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.question-content {
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap;
}

.question-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.question-gallery img {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 14px;
  object-fit: cover;
  display: block;
}

.answers-card {
  margin-bottom: 20px;
}

.answer-input {
  margin-bottom: 20px;
}

.answer-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 15px;
}

.answer-item.accepted {
  border-color: #67c23a;
  background: #f0f9eb;
}

.accepted-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #67c23a;
  font-weight: 500;
  margin-bottom: 15px;
}

.answer-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.answer-author {
  margin-left: 12px;
}

.author-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.answer-time {
  display: block;
  color: #909399;
  font-size: 13px;
  margin-top: 3px;
}

.answer-content {
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  margin-bottom: 15px;
}

.answer-actions {
  display: flex;
  gap: 15px;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>

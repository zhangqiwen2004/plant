<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>问答评论管理</span></template>
    </el-page-header>

    <el-row :gutter="16" class="summary-row">
      <el-col :span="8"><el-card class="summary-card"><div class="summary-value">{{ questionTotal }}</div><div class="summary-label">问题总数</div></el-card></el-col>
      <el-col :span="8"><el-card class="summary-card"><div class="summary-value">{{ answerTotal }}</div><div class="summary-label">回答总数</div></el-card></el-col>
      <el-col :span="8"><el-card class="summary-card"><div class="summary-value">{{ commentTotal }}</div><div class="summary-label">评论总数</div></el-card></el-col>
    </el-row>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="问题管理" name="questions">
          <div class="tab-toolbar">
            <div class="tab-toolbar-left">
              <el-input v-model="questionKeyword" placeholder="搜索问题标题、内容或植物类型" clearable class="search-input" @keyup.enter="handleQuestionFilterChange" @clear="handleQuestionFilterChange" />
              <el-select v-model="questionStatusFilter" class="filter-select" @change="handleQuestionFilterChange">
                <el-option label="全部状态" value="all" />
                <el-option v-for="option in questionStatusOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </div>
            <el-button @click="fetchQuestions" :loading="questionLoading">刷新</el-button>
          </div>

          <el-table :data="questions" v-loading="questionLoading" style="width: 100%">
            <el-table-column label="问题标题" min-width="260">
              <template #default="{ row }">
                <div class="primary-cell">
                  <span class="primary-title">{{ row.title }}</span>
                  <span class="primary-sub">{{ row.plant_type || '未填写植物类型' }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="提问者" width="140"><template #default="{ row }">{{ row.author_info?.username || '-' }}</template></el-table-column>
            <el-table-column label="状态" width="110"><template #default="{ row }"><el-tag :type="getQuestionStatusType(row.status)">{{ row.status_display }}</el-tag></template></el-table-column>
            <el-table-column label="紧急" width="90"><template #default="{ row }">{{ row.is_urgent ? '是' : '否' }}</template></el-table-column>
            <el-table-column label="回答数" width="90"><template #default="{ row }">{{ row.answer_count || 0 }}</template></el-table-column>
            <el-table-column label="创建时间" width="150"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
            <el-table-column label="操作" width="360" fixed="right">
              <template #default="{ row }">
                <div class="action-row wrap">
                  <el-button text @click="$router.push(`/questions/${row.id}`)">查看</el-button>
                  <el-button v-if="row.status !== 'open'" text type="primary" @click="updateQuestionStatus(row, 'open')">重新打开</el-button>
                  <el-button v-if="row.status !== 'answered'" text type="success" @click="updateQuestionStatus(row, 'answered')">标记已答</el-button>
                  <el-button v-if="row.status !== 'closed'" text type="warning" @click="updateQuestionStatus(row, 'closed')">关闭</el-button>
                  <el-button text type="danger" @click="handleDeleteQuestion(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!questionLoading && questions.length === 0" description="暂无问题" />
          <div class="pagination-wrap" v-if="questionTotal > pageSize">
            <el-pagination background layout="total, prev, pager, next" :total="questionTotal" :page-size="pageSize" :current-page="questionPage" @current-change="handleQuestionPageChange" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="回答管理" name="answers">
          <div class="tab-toolbar">
            <div class="tab-toolbar-left">
              <el-input v-model="answerKeyword" placeholder="搜索回答内容、问题标题或作者" clearable class="search-input" @keyup.enter="handleAnswerFilterChange" @clear="handleAnswerFilterChange" />
            </div>
            <el-button @click="fetchAnswers" :loading="answerLoading">刷新</el-button>
          </div>

          <el-table :data="answers" v-loading="answerLoading" style="width: 100%">
            <el-table-column label="问题" min-width="220">
              <template #default="{ row }">
                <div class="primary-cell">
                  <span class="primary-title">{{ row.question_title || `问题 #${row.question}` }}</span>
                  <span class="primary-sub">{{ getExcerpt(row.content, 70) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="回答者" width="140"><template #default="{ row }">{{ row.author_info?.username || '-' }}</template></el-table-column>
            <el-table-column label="采纳" width="90"><template #default="{ row }"><el-tag :type="row.is_accepted ? 'success' : 'info'">{{ row.is_accepted ? '已采纳' : '未采纳' }}</el-tag></template></el-table-column>
            <el-table-column label="点赞" width="80"><template #default="{ row }">{{ row.like_count || 0 }}</template></el-table-column>
            <el-table-column label="时间" width="150"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <div class="action-row">
                  <el-button text @click="$router.push(`/questions/${row.question}`)">查看问题</el-button>
                  <el-button text type="danger" @click="handleDeleteAnswer(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!answerLoading && answers.length === 0" description="暂无回答" />
          <div class="pagination-wrap" v-if="answerTotal > pageSize">
            <el-pagination background layout="total, prev, pager, next" :total="answerTotal" :page-size="pageSize" :current-page="answerPage" @current-change="handleAnswerPageChange" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="评论管理" name="comments">
          <div class="tab-toolbar">
            <div class="tab-toolbar-left">
              <el-input v-model="commentKeyword" placeholder="搜索评论内容、帖子标题或作者" clearable class="search-input" @keyup.enter="handleCommentFilterChange" @clear="handleCommentFilterChange" />
            </div>
            <el-button @click="fetchComments" :loading="commentLoading">刷新</el-button>
          </div>

          <el-table :data="comments" v-loading="commentLoading" style="width: 100%">
            <el-table-column label="所属帖子" min-width="220">
              <template #default="{ row }">
                <div class="primary-cell">
                  <span class="primary-title">{{ row.post_title || `帖子 #${row.post}` }}</span>
                  <span class="primary-sub">{{ getExcerpt(row.content, 70) }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="评论者" width="140"><template #default="{ row }">{{ row.author_info?.username || '-' }}</template></el-table-column>
            <el-table-column label="类型" width="90"><template #default="{ row }">{{ row.parent ? '回复' : '评论' }}</template></el-table-column>
            <el-table-column label="点赞" width="80"><template #default="{ row }">{{ row.like_count || 0 }}</template></el-table-column>
            <el-table-column label="时间" width="150"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <div class="action-row">
                  <el-button text @click="$router.push(`/posts/${row.post}`)">查看帖子</el-button>
                  <el-button text type="danger" @click="handleDeleteComment(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!commentLoading && comments.length === 0" description="暂无评论" />
          <div class="pagination-wrap" v-if="commentTotal > pageSize">
            <el-pagination background layout="total, prev, pager, next" :total="commentTotal" :page-size="pageSize" :current-page="commentPage" @current-change="handleCommentPageChange" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'

const metaStore = useMetaStore()
const activeTab = ref('questions')
const pageSize = 10
const questions = ref([])
const answers = ref([])
const comments = ref([])
const questionLoading = ref(false)
const answerLoading = ref(false)
const commentLoading = ref(false)
const questionPage = ref(1)
const answerPage = ref(1)
const commentPage = ref(1)
const questionTotal = ref(0)
const answerTotal = ref(0)
const commentTotal = ref(0)
const questionKeyword = ref('')
const answerKeyword = ref('')
const commentKeyword = ref('')
const questionStatusFilter = ref('all')

const questionStatusOptions = computed(() => metaStore.questionStatuses)
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : 0)
const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')
const getExcerpt = (value = '', limit = 70) => !value ? '暂无内容' : (value.length > limit ? `${value.slice(0, limit)}...` : value)
const getQuestionStatusType = (status) => ({ open: 'warning', answered: 'success', closed: 'info' }[status] || 'info')

const fetchQuestions = async () => {
  questionLoading.value = true
  try {
    const params = { page: questionPage.value, page_size: pageSize }
    if (questionKeyword.value.trim()) params.search = questionKeyword.value.trim()
    if (questionStatusFilter.value !== 'all') params.status = questionStatusFilter.value
    const res = await api.get('/api/community/questions/', { params })
    questions.value = normalizeList(res.data)
    questionTotal.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取问题列表失败')
  } finally {
    questionLoading.value = false
  }
}

const fetchAnswers = async () => {
  answerLoading.value = true
  try {
    const params = { page: answerPage.value, page_size: pageSize }
    if (answerKeyword.value.trim()) params.search = answerKeyword.value.trim()
    const res = await api.get('/api/community/answers/', { params })
    answers.value = normalizeList(res.data)
    answerTotal.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取回答列表失败')
  } finally {
    answerLoading.value = false
  }
}

const fetchComments = async () => {
  commentLoading.value = true
  try {
    const params = { page: commentPage.value, page_size: pageSize, flat: 1 }
    if (commentKeyword.value.trim()) params.search = commentKeyword.value.trim()
    const res = await api.get('/api/community/comments/', { params })
    comments.value = normalizeList(res.data)
    commentTotal.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取评论列表失败')
  } finally {
    commentLoading.value = false
  }
}

const handleQuestionFilterChange = () => { questionPage.value = 1; fetchQuestions() }
const handleAnswerFilterChange = () => { answerPage.value = 1; fetchAnswers() }
const handleCommentFilterChange = () => { commentPage.value = 1; fetchComments() }
const handleQuestionPageChange = (nextPage) => { questionPage.value = nextPage; fetchQuestions() }
const handleAnswerPageChange = (nextPage) => { answerPage.value = nextPage; fetchAnswers() }
const handleCommentPageChange = (nextPage) => { commentPage.value = nextPage; fetchComments() }

const updateQuestionStatus = async (question, status) => {
  try {
    await api.post(`/api/community/questions/${question.id}/set_status/`, { status })
    ElMessage.success('问题状态已更新')
    fetchQuestions()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '更新问题状态失败')
  }
}

const confirmDelete = async (title, action) => {
  try {
    await ElMessageBox.confirm(title, '删除确认', { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' })
  } catch {
    return false
  }
  await action()
  return true
}

const handleDeleteQuestion = async (question) => {
  try {
    const confirmed = await confirmDelete(`确认删除问题“${question.title}”吗？`, async () => api.delete(`/api/community/questions/${question.id}/`))
    if (!confirmed) return
    ElMessage.success('问题已删除')
    fetchQuestions()
  } catch {
    ElMessage.error('删除问题失败')
  }
}

const handleDeleteAnswer = async (answer) => {
  try {
    const confirmed = await confirmDelete('确认删除这条回答吗？', async () => api.delete(`/api/community/answers/${answer.id}/`))
    if (!confirmed) return
    ElMessage.success('回答已删除')
    fetchAnswers()
    fetchQuestions()
  } catch {
    ElMessage.error('删除回答失败')
  }
}

const handleDeleteComment = async (comment) => {
  try {
    const confirmed = await confirmDelete('确认删除这条评论吗？', async () => api.delete(`/api/community/comments/${comment.id}/`))
    if (!confirmed) return
    ElMessage.success('评论已删除')
    fetchComments()
  } catch {
    ElMessage.error('删除评论失败')
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
  } catch (error) {
}
  fetchQuestions()
  fetchAnswers()
  fetchComments()
})
</script>

<style scoped>
.summary-row { margin-top: 20px; margin-bottom: 16px; }
.summary-card { text-align: center; }
.summary-value { font-size: 28px; font-weight: 700; color: #203226; }
.summary-label { margin-top: 6px; color: #909399; }
.tab-toolbar, .tab-toolbar-left, .action-row { display: flex; align-items: center; gap: 12px; }
.tab-toolbar { justify-content: space-between; margin-bottom: 16px; }
.action-row.wrap { flex-wrap: wrap; }
.search-input { width: 320px; }
.filter-select { width: 140px; }
.primary-cell { display: flex; flex-direction: column; gap: 4px; }
.primary-title { font-weight: 700; color: #303133; }
.primary-sub { color: #909399; font-size: 13px; line-height: 1.5; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: center; }
@media (max-width: 1000px) {
  .tab-toolbar, .tab-toolbar-left { flex-direction: column; align-items: stretch; }
  .search-input, .filter-select { width: 100%; }
}
</style>

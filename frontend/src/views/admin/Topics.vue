<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>话题管理</span></template>
    </el-page-header>

    <el-row :gutter="16" class="summary-row">
      <el-col :span="8">
        <el-card class="summary-card">
          <div class="summary-value">{{ total }}</div>
          <div class="summary-label">话题总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card">
          <div class="summary-value">{{ activeTopicCount }}</div>
          <div class="summary-label">启用话题</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card">
          <div class="summary-value">{{ hottestTopicFollowers }}</div>
          <div class="summary-label">最高关注数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="keyword"
            placeholder="搜索话题名称或描述"
            clearable
            class="search-input"
            @keyup.enter="handleFilterChange"
            @clear="handleFilterChange"
          />
          <el-select v-model="statusFilter" class="filter-select" @change="handleFilterChange">
            <el-option label="全部状态" value="all" />
            <el-option label="启用中" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </div>
        <div class="toolbar-actions">
          <el-button @click="fetchTopics" :loading="loading">刷新</el-button>
          <el-button type="primary" @click="openTopicDialog()">新增话题</el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-table :data="topics" v-loading="loading" style="width: 100%">
        <el-table-column label="话题" min-width="240">
          <template #default="{ row }">
            <div class="topic-cell">
              <el-avatar :size="42" :src="resolveMediaUrl(row.icon)">
                {{ row.name?.[0] || '题' }}
              </el-avatar>
              <div class="topic-copy">
                <span class="topic-name">{{ row.name }}</span>
                <span class="topic-desc">{{ row.description || '暂无描述' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="帖子数" width="100">
          <template #default="{ row }">{{ row.post_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="关注数" width="100">
          <template #default="{ row }">{{ row.follower_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button text type="primary" @click="openTopicDialog(row)">编辑</el-button>
              <el-button text :type="row.is_active ? 'warning' : 'success'" @click="handleToggleStatus(row)">
                {{ row.is_active ? '停用' : '启用' }}
              </el-button>
              <el-button text type="danger" @click="handleDeleteTopic(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && topics.length === 0" description="暂无话题" />
    </el-card>

    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="editingTopicId ? '编辑话题' : '新增话题'" width="560px">
      <el-form :model="topicForm" label-width="90px">
        <el-form-item label="话题名称" required>
          <el-input v-model="topicForm.name" maxlength="100" />
        </el-form-item>
        <el-form-item label="话题描述">
          <el-input v-model="topicForm.description" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="topicForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveTopic">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import api from '../../utils/api'
import { resolveMediaUrl } from '../../utils/media'

const topics = ref([])
const loading = ref(false)
const submitting = ref(false)
const keyword = ref('')
const statusFilter = ref('all')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const dialogVisible = ref(false)
const editingTopicId = ref(null)
const topicForm = ref(createTopicForm())

function createTopicForm() {
  return {
    name: '',
    description: '',
    is_active: true,
  }
}

const activeTopicCount = computed(() => topics.value.filter(item => item.is_active).length)
const hottestTopicFollowers = computed(() => {
  return topics.value.reduce((max, item) => Math.max(max, item.follower_count || 0), 0)
})

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : 0)

const fetchTopics = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
    }
    if (keyword.value.trim()) params.search = keyword.value.trim()
    if (statusFilter.value !== 'all') params.is_active = statusFilter.value === 'active'

    const res = await api.get('/api/community/topics/', { params })
    topics.value = normalizeList(res.data)
    total.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取话题列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  page.value = 1
  fetchTopics()
}

const handlePageChange = (nextPage) => {
  page.value = nextPage
  fetchTopics()
}

const openTopicDialog = (topic = null) => {
  editingTopicId.value = topic?.id || null
  topicForm.value = topic ? {
    name: topic.name || '',
    description: topic.description || '',
    is_active: Boolean(topic.is_active),
  } : createTopicForm()
  dialogVisible.value = true
}

const handleSaveTopic = async () => {
  if (!topicForm.value.name.trim()) {
    ElMessage.warning('请输入话题名称')
    return
  }

  submitting.value = true
  try {
    if (editingTopicId.value) {
      await api.patch(`/api/community/topics/${editingTopicId.value}/`, topicForm.value)
      ElMessage.success('话题已更新')
    } else {
      await api.post('/api/community/topics/', topicForm.value)
      ElMessage.success('话题已创建')
    }
    dialogVisible.value = false
    fetchTopics()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存话题失败')
  } finally {
    submitting.value = false
  }
}

const handleToggleStatus = async (topic) => {
  try {
    await api.patch(`/api/community/topics/${topic.id}/`, { is_active: !topic.is_active })
    ElMessage.success(topic.is_active ? '话题已停用' : '话题已启用')
    fetchTopics()
  } catch (error) {
    ElMessage.error('更新话题状态失败')
  }
}

const handleDeleteTopic = async (topic) => {
  try {
    await ElMessageBox.confirm(`确认删除话题“${topic.name}”吗？`, '删除话题', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    await api.delete(`/api/community/topics/${topic.id}/`)
    ElMessage.success('话题已删除')
    if (topics.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    fetchTopics()
  } catch (error) {
    ElMessage.error('删除话题失败')
  }
}

onMounted(fetchTopics)
</script>

<style scoped>
.summary-row {
  margin-top: 20px;
  margin-bottom: 16px;
}

.summary-card {
  text-align: center;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #203226;
}

.summary-label {
  margin-top: 6px;
  color: #909399;
}

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.toolbar-left,
.toolbar-actions,
.action-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 140px;
}

.topic-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topic-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 4px;
}

.topic-name {
  font-weight: 700;
  color: #303133;
}

.topic-desc {
  color: #909399;
  font-size: 13px;
  line-height: 1.5;
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .toolbar,
  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }
}
</style>

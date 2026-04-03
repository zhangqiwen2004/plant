<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>匹配管理</span></template>
    </el-page-header>

    <el-alert
      title="此处仅展示匹配概览、请求状态和规则配置，不展示咨询正文与私聊消息。"
      type="info"
      show-icon
      class="page-alert"
    />

    <el-row :gutter="16" class="summary-row">
      <el-col :span="6" v-for="item in summaryCards" :key="item.label">
        <el-card class="summary-card">
          <div class="summary-value">{{ item.value }}</div>
          <div class="summary-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card class="table-card">
          <template #header>
            <div class="section-header">
              <span>匹配请求概览</span>
              <div class="section-actions">
                <el-select v-model="requestStatusFilter" class="filter-select" @change="handleRequestFilterChange">
                  <el-option label="全部状态" value="all" />
                  <el-option v-for="option in requestStatusOptions" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
                <el-button @click="fetchRequests" :loading="requestLoading">刷新</el-button>
              </div>
            </div>
          </template>

          <el-table :data="requests" v-loading="requestLoading" style="width: 100%">
            <el-table-column label="发起用户" min-width="150">
              <template #default="{ row }">{{ row.from_user_info?.username || '-' }}</template>
            </el-table-column>
            <el-table-column label="目标用户" min-width="150">
              <template #default="{ row }">{{ row.to_user_info?.username || '-' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="getRequestStatusType(row.status)">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="建立咨询" width="100">
              <template #default="{ row }">{{ row.consultation_id ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column label="创建时间" width="160">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!requestLoading && requests.length === 0" description="暂无匹配请求" />

          <div class="pagination-wrap" v-if="requestTotal > requestPageSize">
            <el-pagination
              background
              layout="total, prev, pager, next"
              :total="requestTotal"
              :page-size="requestPageSize"
              :current-page="requestPage"
              @current-change="handleRequestPageChange"
            />
          </div>
        </el-card>

        <el-card class="table-card">
          <template #header>
            <div class="section-header">
              <span>匹配记录概览</span>
              <div class="section-actions compact">
                <el-select v-model="recordTypeFilter" class="filter-select" @change="handleRecordFilterChange">
                  <el-option label="全部类型" value="all" />
                  <el-option v-for="option in recordTypeOptions" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
                <el-select v-model="recordContactFilter" class="filter-select" @change="handleRecordFilterChange">
                  <el-option label="全部联系状态" value="all" />
                  <el-option label="已联系" value="contacted" />
                  <el-option label="未联系" value="pending" />
                </el-select>
                <el-button @click="fetchRecords" :loading="recordLoading">刷新</el-button>
              </div>
            </div>
          </template>

          <el-table :data="records" v-loading="recordLoading" style="width: 100%">
            <el-table-column label="用户" min-width="140">
              <template #default="{ row }">{{ row.user_info?.username || '-' }}</template>
            </el-table-column>
            <el-table-column label="匹配对象" min-width="140">
              <template #default="{ row }">{{ row.matched_user_info?.username || '-' }}</template>
            </el-table-column>
            <el-table-column label="匹配类型" width="120">
              <template #default="{ row }">{{ row.match_type_display }}</template>
            </el-table-column>
            <el-table-column label="相似度" width="100">
              <template #default="{ row }">{{ Math.round((row.similarity_score || 0) * 100) }}%</template>
            </el-table-column>
            <el-table-column label="已联系" width="90">
              <template #default="{ row }">
                <el-tag :type="row.is_contacted ? 'success' : 'info'">
                  {{ row.is_contacted ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="反馈" width="80">
              <template #default="{ row }">{{ row.feedback || '-' }}</template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!recordLoading && records.length === 0" description="暂无匹配记录" />

          <div class="pagination-wrap" v-if="recordTotal > recordPageSize">
            <el-pagination
              background
              layout="total, prev, pager, next"
              :total="recordTotal"
              :page-size="recordPageSize"
              :current-page="recordPage"
              @current-change="handleRecordPageChange"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="table-card">
          <template #header>
            <div class="section-header">
              <span>标签权重配置</span>
              <div class="section-actions">
                <el-button @click="fetchWeights" :loading="weightLoading">刷新</el-button>
                <el-button type="primary" @click="openWeightDialog()">新增</el-button>
              </div>
            </div>
          </template>

          <div v-loading="weightLoading">
            <el-empty v-if="weights.length === 0" description="暂无标签权重配置" />
            <div v-for="weight in weights" :key="weight.id" class="weight-item">
              <div class="weight-copy">
                <div class="weight-title-row">
                  <span class="weight-title">{{ weight.tag_type }}</span>
                  <el-tag effect="plain">权重 {{ weight.weight }}</el-tag>
                </div>
                <div class="weight-desc">{{ weight.description || '暂无说明' }}</div>
              </div>
              <div class="weight-actions">
                <el-button text type="primary" @click="openWeightDialog(weight)">编辑</el-button>
                <el-button text type="danger" @click="handleDeleteWeight(weight)">删除</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="weightDialogVisible" :title="editingWeightId ? '编辑标签权重' : '新增标签权重'" width="500px">
      <el-form :model="weightForm" label-width="90px">
        <el-form-item label="标签类型" required>
          <el-input v-model="weightForm.tag_type" maxlength="30" />
        </el-form-item>
        <el-form-item label="权重值" required>
          <el-input-number v-model="weightForm.weight" :min="0" :step="0.1" :precision="1" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="weightForm.description" type="textarea" :rows="4" maxlength="300" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="weightDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="weightSubmitting" @click="handleSaveWeight">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'

const metaStore = useMetaStore()

const summary = ref({})
const requests = ref([])
const records = ref([])
const weights = ref([])

const requestLoading = ref(false)
const recordLoading = ref(false)
const weightLoading = ref(false)
const weightSubmitting = ref(false)

const requestPage = ref(1)
const recordPage = ref(1)
const requestPageSize = 20
const recordPageSize = 20
const requestTotal = ref(0)
const recordTotal = ref(0)

const requestStatusFilter = ref('all')
const recordTypeFilter = ref('all')
const recordContactFilter = ref('all')

const weightDialogVisible = ref(false)
const editingWeightId = ref(null)
const weightForm = ref(createWeightForm())

function createWeightForm() {
  return {
    tag_type: '',
    weight: 1.0,
    description: '',
  }
}

const requestStatusOptions = computed(() => metaStore.matchRequestStatuses)
const recordTypeOptions = computed(() => metaStore.matchRecordTypes)

const summaryCards = computed(() => [
  { label: '匹配请求总数', value: summary.value.total_requests || 0 },
  { label: '待处理请求', value: summary.value.pending_requests || 0 },
  { label: '匹配记录总数', value: summary.value.total_records || 0 },
  { label: '已建立联系', value: summary.value.contacted_records || 0 },
  { label: '专家匹配', value: summary.value.expert_records || 0 },
  { label: '平均相似度', value: `${Math.round((summary.value.average_score || 0) * 100)}%` },
])

const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : 0)
const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const getRequestStatusType = (status) => {
  const map = { pending: 'warning', accepted: 'success', rejected: 'danger', expired: 'info' }
  return map[status] || 'info'
}

const fetchSummary = async () => {
  const res = await api.get('/api/matching/records/admin_summary/')
  summary.value = res.data
}

const fetchRequests = async () => {
  requestLoading.value = true
  try {
    const params = { page: requestPage.value }
    if (requestStatusFilter.value !== 'all') params.status = requestStatusFilter.value
    const res = await api.get('/api/matching/requests/', { params })
    requests.value = normalizeList(res.data)
    requestTotal.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取匹配请求失败')
  } finally {
    requestLoading.value = false
  }
}

const fetchRecords = async () => {
  recordLoading.value = true
  try {
    const params = { page: recordPage.value }
    if (recordTypeFilter.value !== 'all') params.match_type = recordTypeFilter.value
    if (recordContactFilter.value === 'contacted') params.is_contacted = true
    if (recordContactFilter.value === 'pending') params.is_contacted = false
    const res = await api.get('/api/matching/records/', { params })
    records.value = normalizeList(res.data)
    recordTotal.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取匹配记录失败')
  } finally {
    recordLoading.value = false
  }
}

const fetchWeights = async () => {
  weightLoading.value = true
  try {
    const res = await api.get('/api/matching/tag-weights/')
    weights.value = normalizeList(res.data)
  } catch (error) {
ElMessage.error('获取标签权重失败')
  } finally {
    weightLoading.value = false
  }
}

const fetchAllData = async () => {
  await Promise.all([fetchSummary(), fetchRequests(), fetchRecords(), fetchWeights()])
}

const handleRequestFilterChange = () => {
  requestPage.value = 1
  fetchRequests()
}

const handleRecordFilterChange = () => {
  recordPage.value = 1
  fetchRecords()
}

const handleRequestPageChange = (nextPage) => {
  requestPage.value = nextPage
  fetchRequests()
}

const handleRecordPageChange = (nextPage) => {
  recordPage.value = nextPage
  fetchRecords()
}

const openWeightDialog = (weight = null) => {
  editingWeightId.value = weight?.id || null
  weightForm.value = weight ? {
    tag_type: weight.tag_type || '',
    weight: Number(weight.weight || 0),
    description: weight.description || '',
  } : createWeightForm()
  weightDialogVisible.value = true
}

const handleSaveWeight = async () => {
  if (!weightForm.value.tag_type.trim()) {
    ElMessage.warning('请输入标签类型')
    return
  }

  weightSubmitting.value = true
  try {
    if (editingWeightId.value) {
      await api.patch(`/api/matching/tag-weights/${editingWeightId.value}/`, weightForm.value)
      ElMessage.success('标签权重已更新')
    } else {
      await api.post('/api/matching/tag-weights/', weightForm.value)
      ElMessage.success('标签权重已创建')
    }
    weightDialogVisible.value = false
    fetchWeights()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存标签权重失败')
  } finally {
    weightSubmitting.value = false
  }
}

const handleDeleteWeight = async (weight) => {
  try {
    await ElMessageBox.confirm(`确认删除标签权重“${weight.tag_type}”吗？`, '删除标签权重', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    await api.delete(`/api/matching/tag-weights/${weight.id}/`)
    ElMessage.success('标签权重已删除')
    fetchWeights()
  } catch (error) {
    ElMessage.error('删除标签权重失败')
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
  } catch (error) {
}
  fetchAllData()
})
</script>

<style scoped>
.page-alert {
  margin-top: 20px;
  margin-bottom: 16px;
}

.summary-row {
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

.table-card {
  margin-bottom: 16px;
}

.section-header,
.section-actions,
.weight-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-actions.compact {
  justify-content: flex-end;
}

.filter-select {
  width: 140px;
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.weight-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #ebeef5;
}

.weight-item:last-child {
  border-bottom: none;
}

.weight-copy {
  flex: 1;
  min-width: 0;
}

.weight-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.weight-title {
  font-weight: 700;
  color: #303133;
}

.weight-desc {
  margin-top: 6px;
  color: #909399;
  line-height: 1.6;
  font-size: 13px;
}

@media (max-width: 1100px) {
  .section-header,
  .section-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>

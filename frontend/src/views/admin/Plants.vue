<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>植物百科管理</span></template>
    </el-page-header>

    <el-row :gutter="16" class="summary-row">
      <el-col :span="6"><el-card class="summary-card"><div class="summary-value">{{ total }}</div><div class="summary-label">当前筛选植物数</div></el-card></el-col>
      <el-col :span="6"><el-card class="summary-card"><div class="summary-value">{{ plants.filter(item => item.is_active).length }}</div><div class="summary-label">当前页启用中</div></el-card></el-col>
      <el-col :span="6"><el-card class="summary-card"><div class="summary-value">{{ categories.length }}</div><div class="summary-label">分类总数</div></el-card></el-col>
      <el-col :span="6"><el-card class="summary-card"><div class="summary-value">{{ tags.length }}</div><div class="summary-label">植物标签数</div></el-card></el-col>
    </el-row>

    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="keyword" placeholder="搜索植物名称、学名或别名" clearable class="search-input" @keyup.enter="handlePlantFilterChange" @clear="handlePlantFilterChange" />
          <el-select v-model="categoryFilter" class="filter-select" @change="handlePlantFilterChange">
            <el-option label="全部分类" value="all" />
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
          <el-select v-model="statusFilter" class="filter-select" @change="handlePlantFilterChange">
            <el-option label="全部状态" value="all" />
            <el-option label="启用中" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </div>
        <div class="toolbar-actions">
          <el-button @click="fetchAllData" :loading="plantLoading || sideLoading">刷新</el-button>
          <el-button type="primary" @click="openPlantDialog()">新增植物</el-button>
          <el-button plain @click="openCategoryDialog()">新增分类</el-button>
          <el-button plain @click="openTagDialog()">新增标签</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="16">
        <el-card class="section-card">
          <template #header><span>植物百科列表</span></template>
          <el-table :data="plants" v-loading="plantLoading" style="width: 100%">
            <el-table-column label="植物" min-width="260">
              <template #default="{ row }">
                <div class="plant-cell">
                  <el-avatar shape="square" :size="48" :src="resolveMediaUrl(row.image)">{{ row.name?.[0] || '植' }}</el-avatar>
                  <div class="plant-copy">
                    <span class="plant-name">{{ row.name }}</span>
                    <span class="plant-sub">{{ row.scientific_name || '暂无学名' }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="分类" width="120"><template #default="{ row }">{{ row.category_name || '-' }}</template></el-table-column>
            <el-table-column label="难度/光照/浇水" width="220">
              <template #default="{ row }">
                <div class="plant-meta-stack">
                  <span>{{ row.difficulty_display }}</span>
                  <span>{{ row.light_display }}</span>
                  <span>{{ row.water_display }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="标签" min-width="170">
              <template #default="{ row }">
                <div class="tag-wrap">
                  <el-tag v-for="tag in (row.tags || []).slice(0, 3)" :key="tag.id" size="small">{{ tag.name }}</el-tag>
                  <span v-if="!row.tags?.length" class="empty-copy">无标签</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用中' : '已停用' }}</el-tag></template></el-table-column>
            <el-table-column label="浏览" width="90"><template #default="{ row }">{{ row.view_count || 0 }}</template></el-table-column>
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <div class="action-row">
                  <el-button text type="primary" @click="openPlantDialog(row.id)">编辑</el-button>
                  <el-button text @click="$router.push(`/plants/${row.id}`)">查看</el-button>
                  <el-button text :type="row.is_active ? 'warning' : 'success'" @click="handleTogglePlantStatus(row)">{{ row.is_active ? '停用' : '启用' }}</el-button>
                  <el-button text type="danger" @click="handleDeletePlant(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!plantLoading && plants.length === 0" description="暂无植物数据" />

          <div class="pagination-wrap" v-if="total > pageSize">
            <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="pageSize" :current-page="page" @current-change="handlePageChange" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="section-card" v-loading="sideLoading">
          <template #header><span>分类管理</span></template>
          <div v-if="categories.length === 0" class="empty-panel">暂无分类</div>
          <div v-for="category in categories" :key="category.id" class="side-item">
            <div class="side-copy">
              <div class="side-title-row">
                <span class="side-title">{{ category.name }}</span>
                <el-tag size="small" effect="plain">{{ category.plant_count || 0 }} 株</el-tag>
              </div>
              <div class="side-desc">{{ category.parent_name ? `父级：${category.parent_name}` : '顶级分类' }}</div>
            </div>
            <div class="side-actions">
              <el-button text type="primary" @click="openCategoryDialog(category)">编辑</el-button>
              <el-button text type="danger" @click="handleDeleteCategory(category)">删除</el-button>
            </div>
          </div>
        </el-card>

        <el-card class="section-card" v-loading="sideLoading">
          <template #header><span>植物标签管理</span></template>
          <div v-if="tags.length === 0" class="empty-panel">暂无植物标签</div>
          <div v-for="tag in tags" :key="tag.id" class="side-item">
            <div class="side-copy">
              <div class="side-title-row">
                <span class="side-title">{{ tag.name }}</span>
                <span class="tag-dot" :style="{ backgroundColor: tag.color || '#4CAF50' }"></span>
              </div>
              <div class="side-desc">{{ tag.color || '#4CAF50' }}</div>
            </div>
            <div class="side-actions">
              <el-button text type="primary" @click="openTagDialog(tag)">编辑</el-button>
              <el-button text type="danger" @click="handleDeleteTag(tag)">删除</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="plantDialogVisible" :title="editingPlantId ? '编辑植物' : '新增植物'" width="880px">
      <el-form :model="plantForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="植物名称" required><el-input v-model="plantForm.name" maxlength="100" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="分类"><el-select v-model="plantForm.category" style="width: 100%"><el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" /></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="学名"><el-input v-model="plantForm.scientific_name" maxlength="200" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="别名"><el-input v-model="plantForm.alias" maxlength="200" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="养护难度"><el-select v-model="plantForm.difficulty" style="width: 100%"><el-option v-for="option in difficultyOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="光照需求"><el-select v-model="plantForm.light_requirement" style="width: 100%"><el-option v-for="option in lightOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="浇水需求"><el-select v-model="plantForm.water_requirement" style="width: 100%"><el-option v-for="option in waterOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="最低温度"><el-input-number v-model="plantForm.temperature_min" :step="1" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="最高温度"><el-input-number v-model="plantForm.temperature_max" :step="1" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="启用状态"><el-switch v-model="plantForm.is_active" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="植物标签"><el-select v-model="plantForm.selected_tag_ids" multiple collapse-tags collapse-tags-tooltip style="width: 100%"><el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" /></el-select></el-form-item>
        <el-form-item label="简介" required><el-input v-model="plantForm.description" type="textarea" :rows="4" maxlength="1500" show-word-limit /></el-form-item>
        <el-form-item label="湿度要求"><el-input v-model="plantForm.humidity" maxlength="100" /></el-form-item>
        <el-form-item label="土壤要求"><el-input v-model="plantForm.soil_requirement" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="施肥建议"><el-input v-model="plantForm.fertilizer_tips" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="修剪建议"><el-input v-model="plantForm.pruning_tips" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="繁殖方式"><el-input v-model="plantForm.propagation" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="常见问题"><el-input v-model="plantForm.common_problems" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="养护要点"><el-input v-model="plantForm.care_tips" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="plantDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="plantSubmitting" @click="handleSavePlant">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="categoryDialogVisible" :title="editingCategoryId ? '编辑分类' : '新增分类'" width="520px">
      <el-form :model="categoryForm" label-width="90px">
        <el-form-item label="分类名称" required><el-input v-model="categoryForm.name" maxlength="50" /></el-form-item>
        <el-form-item label="父级分类"><el-select v-model="categoryForm.parent" clearable style="width: 100%"><el-option v-for="category in parentCategoryOptions" :key="category.id" :label="category.name" :value="category.id" /></el-select></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="categoryForm.order" :step="1" style="width: 100%" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="categoryForm.description" type="textarea" :rows="4" maxlength="500" show-word-limit /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="sideSubmitting" @click="handleSaveCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tagDialogVisible" :title="editingTagId ? '编辑标签' : '新增标签'" width="460px">
      <el-form :model="tagForm" label-width="90px">
        <el-form-item label="标签名称" required><el-input v-model="tagForm.name" maxlength="50" /></el-form-item>
        <el-form-item label="颜色值"><el-input v-model="tagForm.color" maxlength="20" placeholder="#4CAF50" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="sideSubmitting" @click="handleSaveTag">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'
import { resolveMediaUrl } from '../../utils/media'

const metaStore = useMetaStore()
const plants = ref([])
const categories = ref([])
const tags = ref([])
const plantLoading = ref(false)
const sideLoading = ref(false)
const plantSubmitting = ref(false)
const sideSubmitting = ref(false)
const keyword = ref('')
const categoryFilter = ref('all')
const statusFilter = ref('all')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const plantDialogVisible = ref(false)
const categoryDialogVisible = ref(false)
const tagDialogVisible = ref(false)
const editingPlantId = ref(null)
const editingCategoryId = ref(null)
const editingTagId = ref(null)
const plantForm = ref(createPlantForm())
const categoryForm = ref(createCategoryForm())
const tagForm = ref(createTagForm())

function createPlantForm() {
  return { name: '', scientific_name: '', alias: '', category: null, description: '', difficulty: 'medium', light_requirement: 'indirect', water_requirement: 'medium', temperature_min: 10, temperature_max: 30, humidity: '', soil_requirement: '', fertilizer_tips: '', pruning_tips: '', propagation: '', common_problems: '', care_tips: '', is_active: true, selected_tag_ids: [] }
}
function createCategoryForm() {
  return { name: '', parent: null, order: 0, description: '' }
}
function createTagForm() {
  return { name: '', color: '#4CAF50' }
}

const difficultyOptions = computed(() => metaStore.plantDifficulties)
const lightOptions = computed(() => metaStore.plantLightRequirements)
const waterOptions = computed(() => metaStore.plantWaterRequirements)
const parentCategoryOptions = computed(() => categories.value.filter(category => category.id !== editingCategoryId.value))
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results || [])
const getListTotal = (data) => Array.isArray(data) ? data.length : (typeof data?.count === 'number' ? data.count : 0)

const fetchPlants = async () => {
  plantLoading.value = true
  try {
    const params = { page: page.value }
    if (keyword.value.trim()) params.search = keyword.value.trim()
    if (categoryFilter.value !== 'all') params.category = categoryFilter.value
    if (statusFilter.value === 'active') params.is_active = true
    if (statusFilter.value === 'inactive') params.is_active = false
    const res = await api.get('/api/plants/', { params })
    plants.value = normalizeList(res.data)
    total.value = getListTotal(res.data)
  } catch (error) {
ElMessage.error('获取植物百科失败')
  } finally {
    plantLoading.value = false
  }
}

const fetchSideData = async () => {
  sideLoading.value = true
  try {
    const [categoryRes, tagRes] = await Promise.all([api.get('/api/plants/categories/all/'), api.get('/api/plants/tags/')])
    categories.value = normalizeList(categoryRes.data)
    tags.value = normalizeList(tagRes.data)
  } catch (error) {
ElMessage.error('获取分类或标签失败')
  } finally {
    sideLoading.value = false
  }
}

const fetchAllData = async () => {
  await Promise.all([fetchPlants(), fetchSideData()])
}

const handlePlantFilterChange = () => {
  page.value = 1
  fetchPlants()
}

const handlePageChange = (nextPage) => {
  page.value = nextPage
  fetchPlants()
}

const openPlantDialog = async (plantId = null) => {
  editingPlantId.value = plantId
  if (!plantId) {
    plantForm.value = createPlantForm()
    plantDialogVisible.value = true
    return
  }
  plantSubmitting.value = true
  try {
    const { data } = await api.get(`/api/plants/${plantId}/`)
    plantForm.value = { name: data.name || '', scientific_name: data.scientific_name || '', alias: data.alias || '', category: data.category || null, description: data.description || '', difficulty: data.difficulty || 'medium', light_requirement: data.light_requirement || 'indirect', water_requirement: data.water_requirement || 'medium', temperature_min: data.temperature_min ?? 10, temperature_max: data.temperature_max ?? 30, humidity: data.humidity || '', soil_requirement: data.soil_requirement || '', fertilizer_tips: data.fertilizer_tips || '', pruning_tips: data.pruning_tips || '', propagation: data.propagation || '', common_problems: data.common_problems || '', care_tips: data.care_tips || '', is_active: data.is_active ?? true, selected_tag_ids: data.tag_ids || [] }
    plantDialogVisible.value = true
  } catch {
    ElMessage.error('获取植物详情失败')
  } finally {
    plantSubmitting.value = false
  }
}

const handleSavePlant = async () => {
  if (!plantForm.value.name.trim() || !plantForm.value.description.trim()) {
    ElMessage.warning('请填写植物名称和简介')
    return
  }
  plantSubmitting.value = true
  try {
    if (editingPlantId.value) {
      await api.patch(`/api/plants/${editingPlantId.value}/`, plantForm.value)
      ElMessage.success('植物资料已更新')
    } else {
      await api.post('/api/plants/', plantForm.value)
      ElMessage.success('植物资料已创建')
    }
    plantDialogVisible.value = false
    fetchPlants()
    fetchSideData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存植物资料失败')
  } finally {
    plantSubmitting.value = false
  }
}

const handleTogglePlantStatus = async (plant) => {
  try {
    await api.patch(`/api/plants/${plant.id}/`, { is_active: !plant.is_active })
    ElMessage.success(plant.is_active ? '植物已停用' : '植物已启用')
    fetchPlants()
  } catch {
    ElMessage.error('更新植物状态失败')
  }
}

const handleDeletePlant = async (plant) => {
  try {
    await ElMessageBox.confirm(`确认删除植物“${plant.name}”吗？`, '删除植物', { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' })
  } catch {
    return
  }
  try {
    await api.delete(`/api/plants/${plant.id}/`)
    ElMessage.success('植物资料已删除')
    if (plants.value.length === 1 && page.value > 1) page.value -= 1
    fetchPlants()
    fetchSideData()
  } catch {
    ElMessage.error('删除植物失败')
  }
}

const openCategoryDialog = (category = null) => {
  editingCategoryId.value = category?.id || null
  categoryForm.value = category ? { name: category.name || '', parent: category.parent || null, order: category.order ?? 0, description: category.description || '' } : createCategoryForm()
  categoryDialogVisible.value = true
}

const handleSaveCategory = async () => {
  if (!categoryForm.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  sideSubmitting.value = true
  try {
    if (editingCategoryId.value) {
      await api.patch(`/api/plants/categories/${editingCategoryId.value}/`, categoryForm.value)
      ElMessage.success('分类已更新')
    } else {
      await api.post('/api/plants/categories/', categoryForm.value)
      ElMessage.success('分类已创建')
    }
    categoryDialogVisible.value = false
    fetchSideData()
  } catch {
    ElMessage.error('保存分类失败')
  } finally {
    sideSubmitting.value = false
  }
}

const handleDeleteCategory = async (category) => {
  try {
    await ElMessageBox.confirm(`确认删除分类“${category.name}”吗？`, '删除分类', { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' })
  } catch {
    return
  }
  try {
    await api.delete(`/api/plants/categories/${category.id}/`)
    ElMessage.success('分类已删除')
    fetchSideData()
    fetchPlants()
  } catch {
    ElMessage.error('删除分类失败')
  }
}

const openTagDialog = (tag = null) => {
  editingTagId.value = tag?.id || null
  tagForm.value = tag ? { name: tag.name || '', color: tag.color || '#4CAF50' } : createTagForm()
  tagDialogVisible.value = true
}

const handleSaveTag = async () => {
  if (!tagForm.value.name.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  sideSubmitting.value = true
  try {
    if (editingTagId.value) {
      await api.patch(`/api/plants/tags/${editingTagId.value}/`, tagForm.value)
      ElMessage.success('标签已更新')
    } else {
      await api.post('/api/plants/tags/', tagForm.value)
      ElMessage.success('标签已创建')
    }
    tagDialogVisible.value = false
    fetchSideData()
  } catch {
    ElMessage.error('保存标签失败')
  } finally {
    sideSubmitting.value = false
  }
}

const handleDeleteTag = async (tag) => {
  try {
    await ElMessageBox.confirm(`确认删除标签“${tag.name}”吗？`, '删除标签', { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' })
  } catch {
    return
  }
  try {
    await api.delete(`/api/plants/tags/${tag.id}/`)
    ElMessage.success('标签已删除')
    fetchSideData()
    fetchPlants()
  } catch {
    ElMessage.error('删除标签失败')
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
.summary-row { margin-top: 20px; margin-bottom: 16px; }
.summary-card { text-align: center; }
.summary-value { font-size: 28px; font-weight: 700; color: #203226; }
.summary-label { margin-top: 6px; color: #909399; }
.toolbar-card { margin-bottom: 16px; }
.toolbar, .toolbar-left, .toolbar-actions, .action-row, .side-actions, .side-title-row { display: flex; align-items: center; gap: 12px; }
.toolbar { justify-content: space-between; }
.search-input { width: 320px; }
.filter-select { width: 140px; }
.section-card { margin-bottom: 16px; }
.plant-cell { display: flex; align-items: center; gap: 12px; }
.plant-copy { display: flex; flex-direction: column; gap: 4px; }
.plant-name { font-weight: 700; color: #303133; }
.plant-sub, .empty-copy { color: #909399; font-size: 13px; }
.plant-meta-stack { display: flex; flex-direction: column; gap: 4px; color: #606266; font-size: 13px; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; }
.side-item { display: flex; justify-content: space-between; gap: 12px; padding: 14px 0; border-bottom: 1px solid #ebeef5; }
.side-item:last-child { border-bottom: none; }
.side-copy { flex: 1; min-width: 0; }
.side-title { font-weight: 700; color: #303133; }
.side-desc { margin-top: 6px; color: #909399; font-size: 13px; line-height: 1.6; }
.tag-dot { width: 12px; height: 12px; border-radius: 999px; display: inline-flex; }
.empty-panel { color: #909399; font-size: 13px; padding: 6px 0; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: center; }
@media (max-width: 1100px) {
  .toolbar, .toolbar-left { flex-direction: column; align-items: stretch; }
  .search-input, .filter-select { width: 100%; }
}
</style>

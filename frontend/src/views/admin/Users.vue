<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/admin')" title="返回管理后台">
      <template #content><span>用户管理</span></template>
    </el-page-header>

    <el-card class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索用户名或邮箱" clearable class="search-input" />
        <el-radio-group v-model="roleFilter">
          <el-radio-button v-for="option in roleOptions" :key="option.value" :value="option.value">
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
      <el-table :data="filteredUsers" v-loading="loading" style="width: 100%">
        <el-table-column label="用户" min-width="220">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="42" :src="resolveAvatarUrl(row.avatar, row.id)">
                {{ row.username?.[0] || 'U' }}
              </el-avatar>
              <div class="user-copy">
                <span class="user-name">{{ row.username }}</span>
                <span class="user-email">{{ row.email || '未设置邮箱' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ row.role_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="经验" width="120">
          <template #default="{ row }">{{ row.experience_display || '-' }}</template>
        </el-table-column>
        <el-table-column label="地区" width="120">
          <template #default="{ row }">{{ row.region_display || '-' }}</template>
        </el-table-column>
        <el-table-column label="标签数" width="90">
          <template #default="{ row }">{{ row.tags?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="认证状态" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_expert_verified ? 'success' : 'info'">
              {{ row.is_expert_verified ? '已认证' : '未认证' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredUsers.length === 0" description="暂无匹配用户" />

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalUsers"
          layout="total, prev, pager, next"
          @current-change="fetchUsers"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import api from '../../utils/api'
import { useMetaStore } from '../../stores/meta'
import { resolveMediaUrl, resolveAvatarUrl } from '../../utils/media'

const metaStore = useMetaStore()
const users = ref([])
const loading = ref(true)
const keyword = ref('')
const roleFilter = ref('all')
const currentPage = ref(1)
const pageSize = 20
const totalUsers = ref(0)
const userStats = ref({ total: 0, by_role: {}, verified_experts: 0 })
const roleOptions = computed(() => [
  { value: 'all', label: '全部' },
  ...metaStore.roles
])
const summaryCards = computed(() => ([
  { label: '用户总数', value: userStats.value.total },
  ...metaStore.roles.map(option => ({
    label: option.label,
    value: userStats.value.by_role?.[option.value] || 0
  })),
  { label: '认证达人', value: userStats.value.verified_experts }
]))

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm')

const getRoleType = (role) => {
  const types = { admin: 'danger', expert: 'warning', user: 'success' }
  return types[role] || 'info'
}

const filteredUsers = computed(() => {
  const currentKeyword = keyword.value.trim().toLowerCase()
  return users.value.filter(item => {
    const matchedRole = roleFilter.value === 'all' || item.role === roleFilter.value
    const matchedKeyword = !currentKeyword ||
      item.username?.toLowerCase().includes(currentKeyword) ||
      item.email?.toLowerCase().includes(currentKeyword)
    return matchedRole && matchedKeyword
  })
})

const fetchUsers = async (page) => {
  loading.value = true
  try {
    const res = await api.get('/api/users/', { params: { page: page || currentPage.value } })
    if (res.data.results) {
      users.value = res.data.results
      totalUsers.value = res.data.count
    } else {
      users.value = res.data
      totalUsers.value = res.data.length
    }
  } catch (error) {
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await api.get('/api/users/stats/')
    userStats.value = res.data
  } catch (error) {
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
    await Promise.all([fetchUsers(1), fetchStats()])
  } catch (error) {
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.toolbar-card {
  margin-top: 20px;
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.search-input {
  max-width: 320px;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.user-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: #303133;
}

.user-email {
  color: #909399;
  font-size: 13px;
}

@media (max-width: 900px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    max-width: none;
  }
}
</style>

<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input v-model="search" placeholder="搜索植物名称..." :prefix-icon="Search" clearable @input="handleSearch" />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.category" placeholder="全部分类" clearable @change="fetchPlants">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.difficulty" placeholder="全部难度" clearable @change="fetchPlants">
            <el-option v-for="option in difficultyOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="4" v-for="plant in plants" :key="plant.id">
        <el-card class="plant-card" @click="$router.push(`/plants/${plant.id}`)">
          <div class="plant-image">
            <img :src="plant.image_url" :alt="plant.name" class="plant-photo" loading="lazy" @error="handleImageError" />
          </div>
          <div class="plant-info">
            <h4>{{ plant.name }}</h4>
            <p class="category">{{ plant.category_name }}</p>
            <div class="plant-meta">
              <el-tag size="small" :type="getDifficultyType(plant.difficulty)">
                {{ plant.difficulty_display }}
              </el-tag>
              <span class="views"><el-icon><View /></el-icon> {{ plant.view_count }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && plants.length === 0" description="暂无植物数据" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Search, View } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useMetaStore } from '../stores/meta'
import { PLACEHOLDER_PLANT_IMAGE, withPlantImage } from '../utils/plantImages'

const metaStore = useMetaStore()
const search = ref('')
const filters = ref({ category: '', difficulty: '' })
const categories = ref([])
const plants = ref([])
const loading = ref(true)
const difficultyOptions = computed(() => metaStore.plantDifficulties)

const getDifficultyType = (difficulty) => {
  const types = { easy: 'success', medium: 'warning', hard: 'danger' }
  return types[difficulty] || 'info'
}

const handleImageError = (event) => {
  if (event?.target && event.target.src !== window.location.origin + PLACEHOLDER_PLANT_IMAGE) {
    event.target.src = PLACEHOLDER_PLANT_IMAGE
  }
}

const fetchPlants = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.append('search', search.value)
    if (filters.value.category) params.append('category', filters.value.category)
    if (filters.value.difficulty) params.append('difficulty', filters.value.difficulty)
    
    const res = await api.get(`/api/plants/?${params.toString()}`)
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    plants.value = list.map(withPlantImage)
  } catch (error) {
} finally {
    loading.value = false
  }
}

let searchTimer = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchPlants, 300)
}

onMounted(async () => {
  try {
    const [, categoriesRes] = await Promise.all([
      metaStore.fetchMetadata(),
      api.get('/api/plants/categories/all/')
    ])
    categories.value = categoriesRes.data
  } catch (error) {
}
  fetchPlants()
})
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}

.plant-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.plant-card:hover {
  transform: translateY(-5px);
}

.plant-image {
  height: 120px;
  background: #f0f9eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.plant-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: inherit;
}

.plant-info h4 {
  font-size: 15px;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.plant-info .category {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.plant-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.views {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 3px;
}
</style>

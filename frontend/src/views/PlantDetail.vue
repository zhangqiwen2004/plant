<template>
  <div class="page-container" v-loading="loading">
    <el-page-header @back="$router.push('/plants')" title="返回植物百科" />
    
    <el-card v-if="plant" class="plant-detail-card">
      <el-row :gutter="30">
        <el-col :span="8">
          <div class="plant-image">
            <img :src="plant.image_url" :alt="plant.name" class="plant-photo" loading="lazy" @error="handleImageError" />
          </div>
        </el-col>
        <el-col :span="16">
          <div class="plant-header">
            <h1>{{ plant.name }}</h1>
            <el-button :icon="Star" :type="plant.is_collected ? 'warning' : 'default'" @click="handleCollect">
              {{ plant.is_collected ? '已收藏' : '收藏' }}
            </el-button>
          </div>
          <p class="scientific-name" v-if="plant.scientific_name">{{ plant.scientific_name }}</p>
          <p class="alias" v-if="plant.alias">别名：{{ plant.alias }}</p>
          <p class="description">{{ plant.description }}</p>
          
          <el-row :gutter="15" class="info-cards">
            <el-col :span="6">
              <div class="info-card">
                <el-icon color="#f56c6c"><Sunny /></el-icon>
                <span class="label">光照需求</span>
                <span class="value">{{ plant.light_display }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card">
                <el-icon color="#409eff"><Drizzling /></el-icon>
                <span class="label">浇水需求</span>
                <span class="value">{{ plant.water_display }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card">
                <el-icon color="#e6a23c"><Odometer /></el-icon>
                <span class="label">适宜温度</span>
                <span class="value">{{ plant.temperature_min }}~{{ plant.temperature_max }}℃</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card">
                <el-icon color="#67c23a"><Medal /></el-icon>
                <span class="label">养护难度</span>
                <span class="value">{{ plant.difficulty_display }}</span>
              </div>
            </el-col>
          </el-row>
          
          <div class="tags" v-if="plant.tags?.length">
            <el-tag v-for="tag in plant.tags" :key="tag.id" :color="tag.color + '20'" :style="{color: tag.color, borderColor: tag.color}">
              {{ tag.name }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" v-if="plant">
      <el-col :span="12" v-if="plant.soil_requirement">
        <el-card class="care-card">
          <template #header><span>🌱 土壤要求</span></template>
          <p>{{ plant.soil_requirement }}</p>
        </el-card>
      </el-col>
      <el-col :span="12" v-if="plant.fertilizer_tips">
        <el-card class="care-card">
          <template #header><span>💧 施肥建议</span></template>
          <p>{{ plant.fertilizer_tips }}</p>
        </el-card>
      </el-col>
      <el-col :span="12" v-if="plant.pruning_tips">
        <el-card class="care-card">
          <template #header><span>✂️ 修剪建议</span></template>
          <p>{{ plant.pruning_tips }}</p>
        </el-card>
      </el-col>
      <el-col :span="12" v-if="plant.propagation">
        <el-card class="care-card">
          <template #header><span>🌿 繁殖方式</span></template>
          <p>{{ plant.propagation }}</p>
        </el-card>
      </el-col>
      <el-col :span="12" v-if="plant.common_problems">
        <el-card class="care-card">
          <template #header><span>⚠️ 常见问题</span></template>
          <p>{{ plant.common_problems }}</p>
        </el-card>
      </el-col>
      <el-col :span="12" v-if="plant.care_tips">
        <el-card class="care-card">
          <template #header><span>💡 养护要点</span></template>
          <p>{{ plant.care_tips }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Sunny, Star, Drizzling, Odometer, Medal } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { PLACEHOLDER_PLANT_IMAGE, withPlantImage } from '../utils/plantImages'

const route = useRoute()
const userStore = useUserStore()
const plant = ref(null)
const loading = ref(true)

const handleImageError = (event) => {
  if (event?.target && event.target.src !== window.location.origin + PLACEHOLDER_PLANT_IMAGE) {
    event.target.src = PLACEHOLDER_PLANT_IMAGE
  }
}

const handleCollect = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    if (plant.value.is_collected) {
      await api.delete(`/api/plants/${route.params.id}/uncollect/`)
      plant.value.is_collected = false
      ElMessage.success('取消收藏成功')
    } else {
      await api.post(`/api/plants/${route.params.id}/collect/`)
      plant.value.is_collected = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(async () => {
  try {
    const res = await api.get(`/api/plants/${route.params.id}/`)
    plant.value = withPlantImage(res.data)
  } catch (error) {
    ElMessage.error('获取植物信息失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.plant-detail-card {
  margin: 20px 0;
}

.plant-image {
  height: 280px;
  background: #f0f9eb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plant-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: inherit;
}

.plant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.plant-header h1 {
  font-size: 26px;
  color: #303133;
}

.scientific-name {
  font-style: italic;
  color: #606266;
  margin-bottom: 5px;
}

.alias {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.description {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 20px;
}

.info-cards {
  margin-bottom: 20px;
}

.info-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
}

.info-card .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.info-card .label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.info-card .value {
  display: block;
  font-weight: 500;
  color: #303133;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.care-card {
  margin-bottom: 20px;
}

.care-card p {
  color: #606266;
  line-height: 1.8;
}
</style>

<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="profile-sidebar">
          <div class="user-avatar">
            <div class="avatar-wrapper" @click="showAvatarDialog = true">
              <el-avatar :size="80" :src="resolveAvatarUrl(userStore.user?.avatar, userStore.user?.id)">
                {{ userStore.user?.username?.[0] }}
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
              </div>
            </div>
            <h3>{{ userStore.user?.username }}</h3>
            <el-tag>{{ userStore.user?.role_display }}</el-tag>
          </div>
          
          <el-menu :default-active="activeTab" @select="activeTab = $event">
            <el-menu-item index="profile"><el-icon><User /></el-icon>个人资料</el-menu-item>
            <el-menu-item index="tags"><el-icon><PriceTag /></el-icon>我的标签</el-menu-item>
            <el-menu-item index="notifications"><el-icon><Bell /></el-icon>消息通知</el-menu-item>
            <el-menu-item index="expert"><el-icon><Medal /></el-icon>达人认证</el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      
      <el-col :span="18">
        
        <el-card v-if="activeTab === 'profile'">
          <template #header><span>个人资料</span></template>
          <el-form :model="profileForm" label-width="100px">
            <el-form-item label="个人简介">
              <el-input v-model="profileForm.bio" type="textarea" :rows="4" placeholder="介绍一下自己..." />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="养护经验">
                  <el-select v-model="profileForm.experience_level" style="width: 100%">
                    <el-option v-for="option in experienceOptions" :key="option.value" :label="option.label" :value="option.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="所在地区">
                  <el-select v-model="profileForm.region" style="width: 100%">
                    <el-option v-for="option in regionOptions" :key="option.value" :label="option.label" :value="option.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="saving">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        
        <el-card v-if="activeTab === 'tags'">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>我的标签</span>
              <span style="color: #909399; font-size: 13px">标签用于智能匹配推荐</span>
            </div>
          </template>
          
          <div class="current-tags">
            <el-tag v-for="tag in tags" :key="tag.id" closable @close="handleRemoveTag(tag.id)" class="tag-item">
              {{ tag.tag_value }}
            </el-tag>
            <span v-if="tags.length === 0" style="color: #909399">暂无标签，请从下方选择添加</span>
          </div>
          
          <el-divider />
          
          <div v-for="type in tagTypes" :key="type.value" class="tag-section">
            <h4>{{ type.label }}</h4>
            <div class="tag-options">
              <el-tag 
                v-for="value in type.options" 
                :key="value"
                :class="{ disabled: hasTag(type.value, value) }"
                @click="!hasTag(type.value, value) && handleAddTag(type.value, value)"
              >
                + {{ value }}
              </el-tag>
            </div>
          </div>
        </el-card>

        
        <el-card v-if="activeTab === 'notifications'">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>消息通知</span>
              <el-button text type="primary" @click="handleMarkAllRead">全部标为已读</el-button>
            </div>
          </template>

          <div class="notification-preferences-card">
            <el-form label-width="110px">
              <el-form-item label="站内通知">
                <el-switch v-model="notificationPreferences.in_app_enabled" />
              </el-form-item>
              <el-form-item label="邮件通知">
                <div class="preference-inline">
                  <el-switch v-model="notificationPreferences.email_enabled" />
                  <span class="preference-tip">需要完成后端邮箱配置后才会实际发送邮件</span>
                </div>
              </el-form-item>
              <el-form-item label="通知分类">
                <div class="preference-switch-grid">
                  <el-switch v-model="notificationPreferences.receive_match" active-text="匹配提醒" />
                  <el-switch v-model="notificationPreferences.receive_answer" active-text="答疑回复" />
                  <el-switch v-model="notificationPreferences.receive_system" active-text="系统通知" />
                  <el-switch v-model="notificationPreferences.receive_interaction" active-text="互动通知" />
                </div>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSaveNotificationPreferences" :loading="savingPreferences">保存通知设置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-divider />

          <div class="notification-filter-row">
            <el-radio-group v-model="notificationFilter" size="small">
              <el-radio-button v-for="option in notificationTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </el-radio-button>
            </el-radio-group>
          </div>
          
          <el-empty v-if="filteredNotifications.length === 0" description="暂无通知" />
          
          <div v-for="notification in filteredNotifications" :key="notification.id" class="notification-item" :class="{ unread: !notification.is_read, clickable: !!notification.related_url }" @click="handleOpenNotification(notification)">
            <el-tag size="small" :type="getNotificationType(notification.notification_type)">
              {{ notification.type_display }}
            </el-tag>
            <div class="notification-content">
              <h4>{{ notification.title }}</h4>
              <p>{{ notification.content }}</p>
            </div>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
        </el-card>

        
        <el-card v-if="activeTab === 'expert'">
          <template #header><span>达人认证</span></template>
          
          <div v-if="userStore.user?.is_expert_verified" class="expert-verified">
            <el-icon :size="60" color="#67c23a"><CircleCheckFilled /></el-icon>
            <h3>您已是认证达人</h3>
            <p>擅长领域：{{ userStore.user?.expert_specialty }}</p>
          </div>
          
          <div v-else-if="pendingApplication" class="expert-pending">
            <el-icon :size="60" color="#e6a23c"><Clock /></el-icon>
            <h3>申请审核中</h3>
            <p>您的达人认证申请正在审核，请耐心等待</p>
          </div>
          
          <el-form v-else :model="expertForm" :rules="expertRules" ref="expertFormRef" label-width="100px">
            <el-alert title="成为达人后，您可以帮助更多用户解决养护问题" type="info" show-icon style="margin-bottom: 20px" />
            <el-form-item label="擅长领域" prop="specialty">
              <el-input v-model="expertForm.specialty" placeholder="如：多肉植物、观叶植物、病虫害防治等" />
            </el-form-item>
            <el-form-item label="经验描述" prop="experience_desc">
              <el-input v-model="expertForm.experience_desc" type="textarea" :rows="6" placeholder="请详细描述您的植物养护经验、成就等..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleApplyExpert" :loading="applying">提交申请</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 头像切换对话框 -->
    <el-dialog v-model="showAvatarDialog" title="更换头像" width="520px">
      <div class="avatar-dialog-section">
        <h4>上传自定义头像</h4>
        <el-upload
          :show-file-list="false"
          :before-upload="handleAvatarUpload"
          accept="image/*"
        >
          <el-button type="primary">选择图片上传</el-button>
        </el-upload>
      </div>
      <el-divider>或选择预设头像</el-divider>
      <div class="preset-avatar-grid">
        <div
          v-for="img in presetAvatars"
          :key="img"
          class="preset-avatar-item"
          @click="handleSelectPresetAvatar(img)"
        >
          <el-avatar :size="60" :src="`/images/plants/${img}`" shape="square" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, PriceTag, Bell, Medal, CircleCheckFilled, Clock, Camera } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { useMetaStore } from '../stores/meta'
import dayjs from 'dayjs'
import { resolveMediaUrl, resolveAvatarUrl } from '../utils/media'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const metaStore = useMetaStore()
const activeTab = ref(route.query.tab || 'profile')
const saving = ref(false)
const applying = ref(false)
const savingPreferences = ref(false)
const expertFormRef = ref(null)
const showAvatarDialog = ref(false)

const presetAvatars = [
  'ai_zhi_man.png', 'bai_zhang.jpg', 'bo_xue_wan_nian_cao.png',
  'chang_chun_teng.png', 'diao_zhu_mei.png', 'dou_ban_lan.png',
  'dou_ban_lv.png', 'fu_gui_zhu.jpg', 'he_guo_yu.png',
  'hong_zhang.png', 'hu_die_lan.png', 'jun_zi_lan.png',
  'kong_qi_feng_li.png', 'luo_le.png', 'lu_hui.png',
  'lu_jiao_jue.png', 'mi_die_xiang.png', 'mo_li.png',
  'qin_ye_rong.png', 'tong_qian_cao.png', 'wen_zhu.png',
  'xiang_pi_shu.png', 'xiong_tong_zi.jpeg', 'xiu_qiu.png',
  'xiu_zhen_ye_zi.png', 'yue_ji.png', 'yu_shu.jpeg', 'zhi_zi_hua.png'
]

const profileForm = ref({
  bio: userStore.user?.bio || '',
  experience_level: userStore.user?.experience_level || '',
  region: userStore.user?.region || ''
})

const tags = ref([])
const notifications = ref([])
const applications = ref([])
const notificationFilter = ref('all')
const notificationPreferences = ref({
  in_app_enabled: true,
  email_enabled: false,
  receive_match: true,
  receive_answer: true,
  receive_system: true,
  receive_interaction: true,
})

const expertForm = ref({ specialty: '', experience_desc: '' })
const expertRules = {
  specialty: [{ required: true, message: '请输入擅长领域', trigger: 'blur' }],
  experience_desc: [{ required: true, message: '请描述您的养护经验', trigger: 'blur' }]
}

const experienceOptions = computed(() => metaStore.experienceLevels)
const regionOptions = computed(() => metaStore.regions)
const tagTypes = computed(() => metaStore.tagOptionGroups)
const notificationTypeOptions = computed(() => [
  { value: 'all', label: '全部' },
  ...metaStore.notificationTypes,
])

const pendingApplication = computed(() => applications.value.find(a => a.status === 'pending'))
const filteredNotifications = computed(() => {
  if (notificationFilter.value === 'all') return notifications.value
  return notifications.value.filter(notification => notification.notification_type === notificationFilter.value)
})

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD')

const hasTag = (type, value) => tags.value.some(t => t.tag_type === type && t.tag_value === value)

const getNotificationType = (type) => {
  const types = { match: 'primary', answer: 'success', interaction: 'warning', system: 'info' }
  return types[type] || 'info'
}

const submitTags = async (nextTags) => {
  const res = await api.post('/api/users/tags/submit/', {
    experience_level: profileForm.value.experience_level,
    region: profileForm.value.region,
    tags: nextTags.map(tag => ({
      tag_type: tag.tag_type,
      tag_value: tag.tag_value,
      weight: tag.weight || 1
    }))
  })
  tags.value = res.data.tags || []
  userStore.updateUser({ ...(res.data.user || {}), tags: res.data.tags || [] })
}

const handleUpdateProfile = async () => {
  saving.value = true
  try {
    const res = await api.patch(`/api/users/${userStore.user.id}/`, profileForm.value)
    userStore.updateUser(res.data)
    ElMessage.success('资料更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const handleAddTag = async (tagType, tagValue) => {
  try {
    if (hasTag(tagType, tagValue)) {
      ElMessage.error('标签已存在')
      return
    }
    await submitTags([...tags.value, { tag_type: tagType, tag_value: tagValue, weight: 1 }])
    ElMessage.success('标签添加成功')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const handleRemoveTag = async (tagId) => {
  try {
    await submitTags(tags.value.filter(t => t.id !== tagId))
    ElMessage.success('标签已删除')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleMarkAllRead = async () => {
  try {
    await api.post('/api/users/notifications/mark_all_read/')
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleSaveNotificationPreferences = async () => {
  savingPreferences.value = true
  try {
    const res = await api.patch('/api/users/notifications/preferences/', notificationPreferences.value)
    notificationPreferences.value = res.data
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存通知设置失败')
  } finally {
    savingPreferences.value = false
  }
}

const handleOpenNotification = async (notification) => {
  if (!notification.is_read) {
    try {
      await api.post(`/api/users/notifications/${notification.id}/mark_read/`)
      notification.is_read = true
    } catch (error) {
}
  }

  if (notification.related_url) {
    router.push(notification.related_url)
  }
}

const handleApplyExpert = async () => {
  const valid = await expertFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  applying.value = true
  try {
    await api.post('/api/users/expert-applications/', expertForm.value)
    ElMessage.success('申请已提交，请等待审核')
    const res = await api.get('/api/users/expert-applications/')
    applications.value = res.data.results || res.data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    applying.value = false
  }
}

const handleAvatarUpload = async (file) => {
  const formData = new FormData()
  formData.append('avatar', file)
  try {
    const res = await api.patch(`/api/users/${userStore.user.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    userStore.updateUser(res.data)
    showAvatarDialog.value = false
    ElMessage.success('头像更新成功')
  } catch (error) {
    ElMessage.error('头像上传失败')
  }
  return false
}

const handleSelectPresetAvatar = async (imgName) => {
  try {
    const response = await fetch(`/images/plants/${imgName}`)
    const blob = await response.blob()
    const file = new File([blob], imgName, { type: blob.type })
    const formData = new FormData()
    formData.append('avatar', file)
    const res = await api.patch(`/api/users/${userStore.user.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    userStore.updateUser(res.data)
    showAvatarDialog.value = false
    ElMessage.success('头像更新成功')
  } catch (error) {
    ElMessage.error('头像设置失败')
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
    profileForm.value.experience_level = profileForm.value.experience_level || metaStore.userDefaults?.experience_level || ''
    profileForm.value.region = profileForm.value.region || metaStore.userDefaults?.region || ''

    const [tagsRes, notificationsRes, applicationsRes, preferencesRes] = await Promise.all([
      api.get('/api/users/tags/'),
      api.get('/api/users/notifications/'),
      api.get('/api/users/expert-applications/'),
      api.get('/api/users/notifications/preferences/')
    ])
    tags.value = tagsRes.data.results || tagsRes.data
    userStore.updateUser({ tags: tags.value })
    notifications.value = notificationsRes.data.results || notificationsRes.data
    applications.value = applicationsRes.data.results || applicationsRes.data
    notificationPreferences.value = preferencesRes.data
  } catch (error) {
}
})
</script>

<style scoped>
.profile-sidebar {
  position: sticky;
  top: 80px;
}

.user-avatar {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 10px;
}

.user-avatar h3 {
  margin: 15px 0 10px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
  font-size: 22px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-dialog-section {
  margin-bottom: 10px;
}

.avatar-dialog-section h4 {
  margin: 0 0 10px;
  color: #606266;
}

.preset-avatar-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.preset-avatar-item {
  cursor: pointer;
  border-radius: 8px;
  padding: 4px;
  transition: background 0.2s;
  display: flex;
  justify-content: center;
}

.preset-avatar-item:hover {
  background: #ecf5ff;
}

.current-tags {
  min-height: 40px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
}

.tag-item {
  margin: 5px;
}

.tag-section {
  margin-bottom: 20px;
}

.tag-section h4 {
  margin-bottom: 10px;
  color: #606266;
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-options .el-tag {
  cursor: pointer;
}

.tag-options .el-tag.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notification-preferences-card {
  padding: 16px 18px;
  border-radius: 10px;
  background: #f7faf7;
}

.preference-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.preference-tip {
  font-size: 12px;
  color: #909399;
}

.preference-switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
  width: 100%;
}

.notification-filter-row {
  margin-bottom: 12px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.notification-item.clickable {
  cursor: pointer;
}

.notification-item.unread {
  background: #f0f9eb;
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 5px;
  font-size: 15px;
}

.notification-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.notification-time {
  color: #909399;
  font-size: 13px;
}

.expert-verified, .expert-pending {
  text-align: center;
  padding: 40px;
}

.expert-verified h3, .expert-pending h3 {
  margin: 20px 0 10px;
}

.expert-verified p, .expert-pending p {
  color: #909399;
}
</style>

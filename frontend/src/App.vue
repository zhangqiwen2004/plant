<template>
  <div id="app">
    <el-container v-if="isAdminShell" class="admin-shell">
      <el-aside width="260px" class="admin-sidebar">
        <div class="admin-brand" @click="router.push('/admin')">
          <div class="brand-mark">
            <el-icon :size="24" color="#ffffff"><Sunny /></el-icon>
          </div>
          <div class="admin-brand-copy">
            <span class="brand-title">植物养护社群</span>
            <span class="admin-brand-subtitle">后台管理中心</span>
          </div>
        </div>

        <div class="admin-nav-list">
          <button
            v-for="item in adminNavItems"
            :key="item.path"
            type="button"
            class="admin-nav-item"
            :class="{ active: activeAdminPath === item.path }"
            @click="router.push(item.path)"
          >
            <el-icon class="admin-nav-icon"><component :is="item.icon" /></el-icon>
            <div class="admin-nav-copy">
              <span class="admin-nav-label">{{ item.label }}</span>
              <span class="admin-nav-desc">{{ item.desc }}</span>
            </div>
          </button>
        </div>

        <div class="admin-sidebar-footer">
          <span class="sidebar-footer-label">内容预览</span>
          <el-button class="sidebar-footer-button" plain @click="router.push('/community')">
            查看前台社区
          </el-button>
        </div>
      </el-aside>

      <el-container class="admin-main-shell">
        <el-header class="admin-topbar">
          <div class="admin-topbar-copy">
            <span class="admin-topbar-kicker">Admin Workspace</span>
            <h1>{{ currentAdminTitle }}</h1>
            <p>集中处理审核、用户、统计和系统管理入口，不再混在普通用户前台里。</p>
          </div>

          <div class="admin-topbar-actions">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="notification-bell">
              <el-button :icon="Bell" circle @click="router.push('/profile?tab=notifications')" />
            </el-badge>

            <el-dropdown @command="handleCommand" placement="bottom-end">
              <div class="admin-user-card">
                <el-avatar :size="38" :src="resolveAvatarUrl(userStore.user?.avatar, userStore.user?.id)">
                  {{ userStore.user?.username?.[0] || 'A' }}
                </el-avatar>
                <div class="admin-user-meta">
                  <span class="username">{{ userStore.user?.username }}</span>
                  <span class="role-label">管理员</span>
                </div>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="community">
                    <el-icon><ChatDotRound /></el-icon>查看前台社区
                  </el-dropdown-item>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main class="admin-main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <el-container v-else class="app-shell">
      <el-header class="header">
        <div class="header-content">
          <div class="brand-block" @click="goToBrandHome">
            <div class="brand-mark">
              <el-icon :size="24" color="#ffffff"><Sunny /></el-icon>
            </div>
            <div class="brand-copy">
              <span class="brand-title">植物养护社群</span>
              <span class="brand-subtitle">发现植物 · 分享经验 · 连接同好</span>
            </div>
          </div>

          <nav class="nav-panel">
            <button
              v-for="item in navItems"
              :key="item.path"
              type="button"
              class="nav-link"
              :class="{ active: activeNavPath === item.path }"
              @click="router.push(item.path)"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </button>
          </nav>

          <div class="user-area">
            <div class="status-pill">
              {{ userStore.isLoggedIn ? `你好，${userStore.user?.username}` : '游客浏览中' }}
            </div>

            <template v-if="userStore.isLoggedIn">
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="notification-bell">
                <el-button :icon="Bell" circle @click="router.push('/profile?tab=notifications')" />
              </el-badge>
              <el-dropdown @command="handleCommand" placement="bottom-end">
                <div class="user-info">
                  <el-avatar :size="36" :src="resolveAvatarUrl(userStore.user?.avatar, userStore.user?.id)">
                    {{ userStore.user?.username?.[0] || 'U' }}
                  </el-avatar>
                  <div class="user-meta">
                    <span class="username">{{ userStore.user?.username }}</span>
                    <span class="role-label">{{ userStore.user?.role === 'admin' ? '管理员' : '社区成员' }}</span>
                  </div>
                  <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>个人中心
                    </el-dropdown-item>
                    <el-dropdown-item v-if="userStore.user?.role === 'admin'" command="admin">
                      <el-icon><Setting /></el-icon>管理后台
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>

            <template v-else>
              <el-button type="primary" @click="router.push('/login')">登录</el-button>
              <el-button plain @click="router.push('/register')">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>

      <el-footer class="footer">
        <div class="footer-content">
          <div class="footer-brand">
            <p class="footer-title">植物养护社群平台</p>
            <p class="footer-text">把知识、经验与社区互动组合成更顺手的养护体验。</p>
          </div>

          <div class="footer-links">
            <button
              v-for="item in navItems.slice(1)"
              :key="item.path"
              type="button"
              class="footer-link"
              @click="router.push(item.path)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  ArrowDown,
  Setting,
  SwitchButton,
  Sunny,
  Reading,
  ChatDotRound,
  QuestionFilled,
  Connection,
  Bell,
  Document,
  Medal,
  DataLine,
  CollectionTag
} from '@element-plus/icons-vue'
import { useUserStore } from './stores/user'
import { useMetaStore } from './stores/meta'
import api from './utils/api'
import { resolveMediaUrl, resolveAvatarUrl } from './utils/media'

const userStore = useUserStore()
const metaStore = useMetaStore()
const router = useRouter()
const route = useRoute()

const navItems = [
  { label: '首页', path: '/', icon: Sunny },
  { label: '植物百科', path: '/plants', icon: Reading },
  { label: '社区交流', path: '/community', icon: ChatDotRound },
  { label: '问答中心', path: '/questions', icon: QuestionFilled },
  { label: '达人匹配', path: '/matching', icon: Connection }
]

const adminNavItems = [
  { label: '总控台', path: '/admin', icon: Setting, desc: '概览数据、待办事项、系统入口' },
  { label: '植物百科', path: '/admin/plants', icon: Reading, desc: '管理植物资料、分类与标签' },
  { label: '话题管理', path: '/admin/topics', icon: CollectionTag, desc: '维护社区话题与启用状态' },
  { label: '帖子管理', path: '/admin/posts', icon: Document, desc: '审核帖子、置顶、精华管理' },
  { label: '问答评论', path: '/admin/moderation', icon: QuestionFilled, desc: '处理问题、回答与评论内容' },
  { label: '达人审核', path: '/admin/experts', icon: Medal, desc: '处理认证申请和审核意见' },
  { label: '用户管理', path: '/admin/users', icon: User, desc: '查看角色、标签和认证状态' },
  { label: '匹配管理', path: '/admin/matching', icon: Connection, desc: '查看匹配概览并配置标签权重' },
  { label: '运营统计', path: '/admin/analytics', icon: DataLine, desc: '查看趋势、活动和运营指标' }
]

const isAdminShell = computed(() => route.path.startsWith('/admin') && userStore.user?.role === 'admin')

const activeNavPath = computed(() => {
  if (route.path.startsWith('/plants')) return '/plants'
  if (route.path.startsWith('/community') || route.path.startsWith('/posts')) return '/community'
  if (route.path.startsWith('/questions')) return '/questions'
  if (route.path.startsWith('/matching')) return '/matching'
  return '/'
})

const activeAdminPath = computed(() => {
  if (route.path.startsWith('/admin/plants')) return '/admin/plants'
  if (route.path.startsWith('/admin/topics')) return '/admin/topics'
  if (route.path.startsWith('/admin/posts')) return '/admin/posts'
  if (route.path.startsWith('/admin/moderation')) return '/admin/moderation'
  if (route.path.startsWith('/admin/experts')) return '/admin/experts'
  if (route.path.startsWith('/admin/users')) return '/admin/users'
  if (route.path.startsWith('/admin/matching')) return '/admin/matching'
  if (route.path.startsWith('/admin/analytics')) return '/admin/analytics'
  return '/admin'
})

const currentAdminTitle = computed(() => {
  return adminNavItems.find(item => item.path === activeAdminPath.value)?.label || '管理后台'
})

const goToBrandHome = () => {
  if (userStore.user?.role === 'admin') {
    router.push('/admin')
    return
  }
  router.push('/')
}

const unreadCount = ref(0)
const authReady = ref(false)
let pollTimer = null

onMounted(async () => {
  await userStore.initAuth()
  authReady.value = true
  metaStore.fetchMetadata().catch(() => {
  })
})

const fetchUnreadCount = async () => {
  if (!userStore.isLoggedIn) {
    unreadCount.value = 0
    return
  }
  try {
    const res = await api.get('/api/users/notifications/unread_count/')
    unreadCount.value = res.data.count || 0
  } catch {
  }
}

const startPolling = () => {
  stopPolling()
  fetchUnreadCount()
  pollTimer = setInterval(fetchUnreadCount, 30000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

watch([() => userStore.isLoggedIn, authReady], ([loggedIn, ready]) => {
  if (ready && loggedIn) {
    startPolling()
  } else {
    stopPolling()
    unreadCount.value = 0
  }
}, { immediate: true })

onUnmounted(() => {
  stopPolling()
})

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'admin') {
    router.push('/admin')
  } else if (command === 'community') {
    router.push('/community')
  } else if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }
}
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(90, 162, 104, 0.14), transparent 24%),
    linear-gradient(180deg, #f4f7f3 0%, #edf2ee 100%);
}

.admin-sidebar {
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  background: linear-gradient(180deg, #203227 0%, #17261d 100%);
  color: #ffffff;
}

.admin-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.admin-brand-copy {
  display: flex;
  flex-direction: column;
}

.admin-brand .brand-title {
  color: #ffffff;
}

.admin-brand-subtitle {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
}

.admin-nav-list {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.admin-nav-item {
  border: none;
  border-radius: 18px;
  padding: 14px;
  background: transparent;
  color: rgba(233, 241, 235, 0.88);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, color 0.2s ease;
}

.admin-nav-item:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.08);
}

.admin-nav-item.active {
  background: linear-gradient(135deg, rgba(95, 164, 109, 0.34), rgba(61, 113, 72, 0.28));
  color: #ffffff;
  box-shadow: 0 16px 28px rgba(5, 17, 10, 0.22);
}

.admin-nav-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.admin-nav-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.admin-nav-label {
  font-weight: 700;
}

.admin-nav-desc {
  color: rgba(233, 241, 235, 0.7);
  font-size: 12px;
  line-height: 1.5;
}

.admin-sidebar-footer {
  margin-top: auto;
  padding-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.sidebar-footer-label {
  color: rgba(233, 241, 235, 0.7);
  font-size: 12px;
}

.sidebar-footer-button {
  width: 100%;
}

.admin-main-shell {
  min-width: 0;
}

.admin-topbar {
  height: auto;
  padding: 26px 30px 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.admin-topbar-copy h1 {
  margin: 10px 0 0;
  color: #203226;
  font-size: 30px;
}

.admin-topbar-copy p {
  margin-top: 12px;
  color: #6d7e71;
  line-height: 1.7;
}

.admin-topbar-kicker {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(77, 139, 87, 0.12);
  color: #355b3d;
  font-size: 12px;
  font-weight: 700;
}

.admin-topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(56, 97, 64, 0.08);
  cursor: pointer;
}

.admin-user-meta {
  display: flex;
  flex-direction: column;
}

.admin-main-content {
  padding: 10px 30px 30px;
}

.admin-main-content :deep(.page-container) {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.header {
  background: rgba(247, 250, 246, 0.74);
  backdrop-filter: blur(22px);
  border-bottom: 1px solid rgba(56, 97, 64, 0.08);
  padding: 0;
  height: 88px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-content {
  max-width: 1320px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
  cursor: pointer;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5aa268 0%, #2f6b3a 100%);
  box-shadow: 0 12px 24px rgba(77, 139, 87, 0.28);
}

.brand-copy {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 18px;
  line-height: 1.1;
  font-weight: 700;
  color: #1f3126;
}

.brand-subtitle {
  font-size: 12px;
  color: #7b8a7e;
  margin-top: 4px;
  white-space: nowrap;
}

.nav-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(56, 97, 64, 0.08);
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-panel::-webkit-scrollbar {
  display: none;
}

.nav-link {
  border: none;
  background: transparent;
  color: #526555;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 16px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.nav-link:hover {
  background: rgba(238, 247, 239, 0.9);
  color: #355b3d;
}

.nav-link.active {
  background: linear-gradient(135deg, #4d8b57 0%, #30663a 100%);
  color: #ffffff;
  box-shadow: 0 12px 22px rgba(77, 139, 87, 0.24);
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.notification-bell {
  cursor: pointer;
}

.status-pill {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(56, 97, 64, 0.08);
  color: #607265;
  font-size: 13px;
  white-space: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(56, 97, 64, 0.08);
  cursor: pointer;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.username {
  color: #1f3126;
  font-weight: 700;
  line-height: 1.1;
}

.role-label {
  color: #7b8a7e;
  font-size: 12px;
  margin-top: 4px;
}

.dropdown-icon {
  color: #7b8a7e;
}

.main-content {
  margin-top: 96px;
  min-height: calc(100vh - 188px);
  padding: 0;
  background: transparent;
}

.footer {
  background: transparent;
  padding: 0 24px 28px;
  height: auto;
}

.footer-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(56, 97, 64, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.footer-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f3126;
}

.footer-text {
  margin-top: 8px;
  font-size: 13px;
  color: #6b7c6f;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.footer-link {
  border: none;
  background: rgba(238, 247, 239, 0.9);
  color: #355b3d;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.footer-link:hover {
  transform: translateY(-1px);
  background: #e4f0e5;
}

@media (max-width: 1200px) {
  .status-pill {
    display: none;
  }
}

@media (max-width: 1100px) {
  .admin-shell {
    flex-direction: column;
  }

  .admin-sidebar {
    width: 100% !important;
  }

  .admin-nav-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .admin-topbar {
    padding: 24px 22px 0;
    flex-direction: column;
  }

  .admin-main-content {
    padding: 10px 22px 24px;
  }
}

@media (max-width: 1024px) {
  .header-content {
    padding: 0 18px;
    gap: 12px;
  }

  .brand-subtitle {
    display: none;
  }

  .footer-content {
    padding: 22px 24px;
  }
}

@media (max-width: 768px) {
  .admin-nav-list {
    grid-template-columns: 1fr;
  }

  .admin-user-meta,
  .admin-user-card .dropdown-icon {
    display: none;
  }

  .header {
    height: 84px;
  }

  .header-content {
    padding: 0 14px;
  }

  .nav-panel {
    padding: 6px;
    gap: 6px;
  }

  .nav-link {
    padding: 10px 12px;
    font-size: 13px;
  }

  .nav-link span {
    display: none;
  }

  .user-meta,
  .dropdown-icon {
    display: none;
  }

  .user-info {
    padding: 6px;
    border-radius: 14px;
  }

  .main-content {
    margin-top: 90px;
  }

  .footer {
    padding: 0 14px 20px;
  }

  .footer-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .footer-links {
    justify-content: flex-start;
  }
}
</style>

<template>
  <div class="login-container">
    <div class="auth-shell">
      <section class="auth-hero">
        <div class="auth-badge">
          <el-icon><Sunny /></el-icon>
          <span>植物养护社群</span>
        </div>

        <div class="hero-copy">
          <h1>欢迎回来，继续你的养护记录与社区互动。</h1>
          <p>登录后你可以查看个性化推荐、继续浏览社区讨论，并与达人保持交流。</p>
        </div>

        <div class="hero-points">
          <div class="hero-point">
            <strong>知识</strong>
            <span>快速回到植物百科与收藏内容</span>
          </div>
          <div class="hero-point">
            <strong>交流</strong>
            <span>继续参与社区动态和评论互动</span>
          </div>
          <div class="hero-point">
            <strong>支持</strong>
            <span>向达人发问并管理你的个人资料</span>
          </div>
        </div>
      </section>

      <el-card class="login-card">
        <div class="login-header">
          <div class="header-icon">
            <el-icon :size="24" color="#ffffff"><Sunny /></el-icon>
          </div>
          <h2>登录账号</h2>
          <p>输入你的账号信息，继续浏览更完整的植物社区体验。</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              autocomplete="current-password"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="submit-button"
              native-type="submit"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <span>还没有账号？</span>
          <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Sunny } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const user = await userStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push(user?.role === 'admin' ? '/admin' : '/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 150px);
  display: flex;
  align-items: center;
}

.auth-shell {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) 430px;
  gap: 22px;
}

.auth-hero,
.login-card {
  border-radius: 28px;
}

.auth-hero {
  padding: 34px;
  background:
    linear-gradient(135deg, rgba(244, 250, 245, 0.98), rgba(236, 244, 237, 0.92)),
    radial-gradient(circle at top right, rgba(87, 151, 98, 0.16), transparent 28%);
  border: 1px solid rgba(56, 97, 64, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 560px;
}

.auth-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: #355b3d;
  font-weight: 700;
}

.hero-copy h1 {
  margin-top: 24px;
  font-size: 42px;
  line-height: 1.15;
  color: #1d2d23;
  max-width: 540px;
}

.hero-copy p {
  margin-top: 16px;
  max-width: 560px;
  color: #67786b;
  line-height: 1.8;
  font-size: 16px;
}

.hero-points {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.hero-point {
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(56, 97, 64, 0.08);
}

.hero-point strong {
  display: block;
  color: #203226;
  font-size: 15px;
}

.hero-point span {
  display: block;
  margin-top: 10px;
  color: #6d7e71;
  line-height: 1.7;
  font-size: 14px;
}

.login-card :deep(.el-card__body) {
  padding: 30px;
}

.login-header {
  text-align: center;
  margin-bottom: 26px;
}

.header-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4d8b57 0%, #2f6739 100%);
  box-shadow: 0 14px 28px rgba(77, 139, 87, 0.25);
}

.login-header h2 {
  margin-top: 18px;
  color: #203226;
  font-size: 30px;
}

.login-header p {
  margin-top: 12px;
  color: #77887b;
  line-height: 1.7;
}

.submit-button {
  width: 100%;
}

.login-footer {
  margin-top: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  color: #86968a;
}

@media (max-width: 1024px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-hero {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .auth-shell {
    padding: 8px 0;
  }

  .auth-hero {
    padding: 24px;
  }

  .hero-copy h1 {
    font-size: 30px;
  }

  .hero-points {
    grid-template-columns: 1fr;
    margin-top: 20px;
  }

  .login-card :deep(.el-card__body) {
    padding: 22px;
  }
}
</style>

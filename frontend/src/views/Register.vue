<template>
  <div class="register-container">
    <div class="auth-shell">
      <section class="auth-hero">
        <div class="auth-badge">
          <el-icon><Sunny /></el-icon>
          <span>植物养护社群</span>
        </div>

        <div class="hero-copy">
          <h1>创建你的植物社区账号，开始记录与分享养护经验。</h1>
          <p>注册后你可以收藏植物资料、发布社区动态、提问互动，并获得更贴近自己的内容体验。</p>
        </div>

        <div class="hero-points">
          <div class="hero-point">
            <strong>新手友好</strong>
            <span>按经验等级初始化你的使用体验</span>
          </div>
          <div class="hero-point">
            <strong>地区适配</strong>
            <span>结合地区差异理解更贴近环境的建议</span>
          </div>
          <div class="hero-point">
            <strong>持续成长</strong>
            <span>在社区中沉淀问题、经验和养护记录</span>
          </div>
        </div>
      </section>

      <el-card class="register-card">
        <div class="register-header">
          <div class="header-icon">
            <el-icon :size="24" color="#ffffff"><Sunny /></el-icon>
          </div>
          <h2>创建账号</h2>
          <p>补充基本信息后就可以加入社区，开始你的植物养护旅程。</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
          </el-form-item>

          <el-form-item prop="email">
            <el-input v-model="form.email" placeholder="邮箱" :prefix-icon="Message" size="large" />
          </el-form-item>

          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码（至少8位）" :prefix-icon="Lock" size="large" autocomplete="new-password" />
          </el-form-item>

          <el-form-item prop="password_confirm">
            <el-input v-model="form.password_confirm" type="password" placeholder="确认密码" :prefix-icon="Lock" size="large" autocomplete="new-password" />
          </el-form-item>

          <el-row :gutter="15">
            <el-col :span="12">
              <el-form-item prop="experience_level">
                <el-select v-model="form.experience_level" placeholder="养护经验" size="large" style="width: 100%">
                  <el-option v-for="option in experienceOptions" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="region">
                <el-select v-model="form.region" placeholder="所在地区" size="large" style="width: 100%">
                  <el-option v-for="option in regionOptions" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="submit-button" native-type="submit">
              注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="register-footer">
          <span>已有账号？</span>
          <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Sunny } from '@element-plus/icons-vue'
import api from '../utils/api'
import { useMetaStore } from '../stores/meta'

const router = useRouter()
const metaStore = useMetaStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  experience_level: '',
  region: ''
})

const experienceOptions = computed(() => metaStore.experienceLevels)
const regionOptions = computed(() => metaStore.regions)

const validatePass = (rule, value, callback) => {
  if (value !== form.value.password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await api.post('/api/users/', form.value)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    const errors = error.response?.data
    if (errors) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await metaStore.fetchMetadata()
    form.value.experience_level = form.value.experience_level || metaStore.userDefaults?.experience_level || ''
    form.value.region = form.value.region || metaStore.userDefaults?.region || ''
  } catch {
  }
})
</script>

<style scoped>
.register-container {
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
  grid-template-columns: minmax(0, 1.15fr) 460px;
  gap: 22px;
}

.auth-hero,
.register-card {
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
  min-height: 640px;
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
  font-size: 40px;
  line-height: 1.15;
  color: #1d2d23;
  max-width: 560px;
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

.register-card :deep(.el-card__body) {
  padding: 28px;
}

.register-header {
  text-align: center;
  margin-bottom: 24px;
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

.register-header h2 {
  margin-top: 18px;
  color: #203226;
  font-size: 30px;
}

.register-header p {
  margin-top: 12px;
  color: #77887b;
  line-height: 1.7;
}

.submit-button {
  width: 100%;
}

.register-footer {
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

  .register-card :deep(.el-card__body) {
    padding: 22px;
  }
}
</style>

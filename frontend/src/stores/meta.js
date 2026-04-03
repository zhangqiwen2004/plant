import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import api from '../utils/api'


export const useMetaStore = defineStore('meta', () => {
  const metadata = ref({})
  const loading = ref(false)
  const loaded = ref(false)
  let pendingPromise = null

  async function fetchMetadata(force = false) {
    if (loaded.value && !force) return metadata.value
    if (pendingPromise && !force) return pendingPromise

    loading.value = true
    pendingPromise = api.get('/api/meta/')
      .then((response) => {
        metadata.value = response.data || {}
        loaded.value = true
        return metadata.value
      })
      .finally(() => {
        loading.value = false
        pendingPromise = null
      })

    return pendingPromise
  }

  const userMeta = computed(() => metadata.value.users || {})
  const communityMeta = computed(() => metadata.value.community || {})
  const plantMeta = computed(() => metadata.value.plants || {})
  const matchingMeta = computed(() => metadata.value.matching || {})
  const analyticsMeta = computed(() => metadata.value.analytics || {})

  const roles = computed(() => userMeta.value.roles || [])
  const experienceLevels = computed(() => userMeta.value.experience_levels || [])
  const regions = computed(() => userMeta.value.regions || [])
  const tagOptionGroups = computed(() => userMeta.value.tag_option_groups || [])
  const notificationTypes = computed(() => userMeta.value.notification_types || [])
  const expertApplicationStatuses = computed(() => userMeta.value.expert_application_statuses || [])
  const userDefaults = computed(() => userMeta.value.defaults || {})

  const postStatuses = computed(() => communityMeta.value.post_statuses || [])
  const questionStatuses = computed(() => communityMeta.value.question_statuses || [])

  const plantDifficulties = computed(() => plantMeta.value.difficulties || [])
  const plantLightRequirements = computed(() => plantMeta.value.light_requirements || [])
  const plantWaterRequirements = computed(() => plantMeta.value.water_requirements || [])

  const matchModes = computed(() => matchingMeta.value.match_modes || [])
  const matchRecordTypes = computed(() => matchingMeta.value.match_record_types || [])
  const matchRequestStatuses = computed(() => matchingMeta.value.request_statuses || [])
  const trendPresets = computed(() => analyticsMeta.value.trend_presets || [])

  return {
    metadata,
    loading,
    loaded,
    fetchMetadata,
    roles,
    experienceLevels,
    regions,
    tagOptionGroups,
    notificationTypes,
    expertApplicationStatuses,
    userDefaults,
    postStatuses,
    questionStatuses,
    plantDifficulties,
    plantLightRequirements,
    plantWaterRequirements,
    matchModes,
    matchRecordTypes,
    matchRequestStatuses,
    trendPresets,
  }
})

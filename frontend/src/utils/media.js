export const resolveMediaUrl = (value) => {
  if (!value) return ''

  if (/^(https?:)?\/\//.test(value) || value.startsWith('data:')) {
    return value
  }

  if (value.startsWith('/media/') || value.startsWith('/images/') || value.startsWith('/static/')) {
    return value
  }

  if (value.startsWith('media/')) {
    return `/${value}`
  }

  if (value.startsWith('avatars/')) {
    return `/media/${value}`
  }

  return `/${value.replace(/^\/+/, '')}`
}

// 默认头像列表（来自 public/images/plants/）
const DEFAULT_AVATARS = [
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

// 根据用户ID确定性地选择一个默认头像
export const resolveAvatarUrl = (avatar, userId) => {
  if (avatar) return resolveMediaUrl(avatar)
  if (!userId) return ''
  const index = userId % DEFAULT_AVATARS.length
  return `/images/plants/${DEFAULT_AVATARS[index]}`
}

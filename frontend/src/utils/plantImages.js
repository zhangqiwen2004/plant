const PLANT_IMAGE_BASE = '/images/plants'

export const PLACEHOLDER_PLANT_IMAGE = `${PLANT_IMAGE_BASE}/placeholder.svg`

export const PLANT_IMAGE_MAP = {
  '白掌': 'bai_zhang.jpg',
  '红掌': 'hong_zhang.png',
  '文竹': 'wen_zhu.png',
  '富贵竹': 'fu_gui_zhu.jpg',
  '铜钱草': 'tong_qian_cao.png',
  '罗勒': 'luo_le.png',
  '迷迭香': 'mi_die_xiang.png',
  '茉莉': 'mo_li.png',
  '栀子花': 'zhi_zi_hua.png',
  '蝴蝶兰': 'hu_die_lan.png',
  '君子兰': 'jun_zi_lan.png',
  '月季': 'yue_ji.png',
  '绣球': 'xiu_qiu.png',
  '橡皮树': 'xiang_pi_shu.png',
  '琴叶榕': 'qin_ye_rong.png',
  '豆瓣绿': 'dou_ban_lv.png',
  '常春藤': 'chang_chun_teng.png',
  '合果芋': 'he_guo_yu.png',
  '爱之蔓': 'ai_zhi_man.png',
  '吊竹梅': 'diao_zhu_mei.png',
  '鹿角蕨': 'lu_jiao_jue.png',
  '袖珍椰子': 'xiu_zhen_ye_zi.png',
  '芦荟': 'lu_hui.png',
  '玉树': 'yu_shu.jpeg',
  '熊童子': 'xiong_tong_zi.jpeg',
  '豆瓣兰': 'dou_ban_lan.png',
  '薄雪万年草': 'bo_xue_wan_nian_cao.png',
  '空气凤梨': 'kong_qi_feng_li.png',
}

export const getPlantImageFileName = (name) => PLANT_IMAGE_MAP[name] || 'placeholder.svg'

export const getPlantImageUrl = (plantOrName) => {
  const name = typeof plantOrName === 'string' ? plantOrName : plantOrName?.name
  const fileName = getPlantImageFileName(name)
  return `${PLANT_IMAGE_BASE}/${fileName}`
}

export const withPlantImage = (plant) => ({
  ...plant,
  image_url: getPlantImageUrl(plant),
})

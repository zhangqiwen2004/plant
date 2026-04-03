import re
import time

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parents[4]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

from django.core.management.base import BaseCommand

from apps.plants.models import Plant, PlantCategory, PlantTag, PlantTagRelation
from apps.plants.seed_data import CATEGORY_DEFS, PLANT_CATALOG, TAG_DEFS


class Command(BaseCommand):
    help = '在线抓取并扩充植物数据'

    CATEGORY_DEFS = [
        {'name': '多肉植物', 'description': '肉质茎叶植物，耐旱且适合家庭栽培', 'order': 1},
        {'name': '观叶植物', 'description': '以叶片观赏为主的室内植物', 'order': 2},
        {'name': '开花植物', 'description': '以花朵观赏为主的植物', 'order': 3},
        {'name': '藤蔓植物', 'description': '适合攀援或垂吊养护的植物', 'order': 4},
        {'name': '水培植物', 'description': '适合水培或半水培环境的植物', 'order': 5},
        {'name': '香草植物', 'description': '兼具香气与食用价值的草本植物', 'order': 6},
        {'name': '仙人掌', 'description': '仙人掌科及近似耐旱观赏植物', 'order': 7},
        {'name': '蕨类植物', 'description': '偏爱高湿与散射光环境的观赏蕨类', 'order': 8},
    ]

    TAG_DEFS = {
        '新手友好': '#4CAF50',
        '耐旱': '#FF9800',
        '喜阴': '#607D8B',
        '喜光': '#FFEB3B',
        '净化空气': '#00BCD4',
        '观花': '#E91E63',
        '观叶': '#8BC34A',
        '香气': '#FF5722',
        '可食用': '#795548',
        '耐寒': '#2196F3',
        '室内友好': '#26A69A',
        '垂吊': '#AB47BC',
        '水培': '#42A5F5',
        '攀援': '#5C6BC0',
        '高湿': '#009688',
        '驱蚊': '#7CB342',
    }

    PLANT_CATALOG = [
        {
            'name': '白掌',
            'scientific_name': 'Spathiphyllum wallisii',
            'alias': '白鹤芋、一帆风顺',
            'wiki_title': '白鶴芋',
            'category': '观叶植物',
            'summary': '白掌又名白鹤芋、一帆风顺，为天南星科多年生常绿草本，原产中南美洲热带雨林，叶片翠绿、佛焰苞洁白，兼具观花与观叶价值，也常用于室内盆栽和水培观赏。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '喜欢温暖湿润环境，空气湿度50%-75%更稳定。',
            'soil_requirement': '疏松透气的腐殖土，保持排水和保水的平衡。',
            'fertilizer_tips': '生长期每2到3周施一次稀薄液肥，花期前可增加磷钾肥。',
            'pruning_tips': '及时剪掉残花和黄叶，维持株型整洁。',
            'propagation': '可通过分株繁殖。',
            'common_problems': '叶片下垂多为缺水，叶尖发黄常与低湿或肥害有关。',
            'care_tips': '避免暴晒，土壤微湿即可，夏季可适当喷水增湿。',
            'tags': ['新手友好', '观花', '观叶', '净化空气', '室内友好'],
        },
        {
            'name': '红掌',
            'scientific_name': 'Anthurium andraeanum',
            'alias': '花烛、火鹤花',
            'wiki_title': '花燭',
            'category': '开花植物',
            'summary': '红掌又名花烛、火鹤花，为天南星科多年生草本，原产热带美洲雨林，佛焰苞鲜亮、肉穗花序直立，花期长，适合盆栽、切花和室内观赏。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 15,
            'temperature_max': 32,
            'humidity': '喜欢高湿环境，湿度60%-80%表现最好。',
            'soil_requirement': '宜用疏松透气、富含有机质的基质。',
            'fertilizer_tips': '生长期每2周补一次薄肥，花期重视磷钾元素。',
            'pruning_tips': '花败后及时从花梗基部剪除。',
            'propagation': '分株繁殖为主。',
            'common_problems': '不开花多因光线不足，叶片焦边常与空气干燥相关。',
            'care_tips': '适合明亮散射光环境，避免冷风和强光直射。',
            'tags': ['观花', '室内友好', '高湿'],
        },
        {
            'name': '文竹',
            'scientific_name': 'Asparagus setaceus',
            'alias': '云片松、云竹',
            'wiki_title': '文竹',
            'category': '观叶植物',
            'summary': '文竹属天门冬科天门冬属，原产非洲南部，枝叶纤细秀丽、姿态轻盈文雅，是常见的室内观叶盆栽，也常作为小型盆景和插花陪衬材料。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 10,
            'temperature_max': 28,
            'humidity': '喜湿润，空气湿度50%-70%较适宜。',
            'soil_requirement': '偏疏松的腐叶土或泥炭土基质。',
            'fertilizer_tips': '生长期每月施一次稀薄液肥即可。',
            'pruning_tips': '及时修去黄枝、徒长枝，保持通风。',
            'propagation': '可播种或分株繁殖。',
            'common_problems': '黄叶常与干燥、暴晒或积水有关。',
            'care_tips': '放在通风良好的明亮处，避免反复移动位置。',
            'tags': ['观叶', '喜阴', '室内友好'],
        },
        {
            'name': '富贵竹',
            'scientific_name': 'Dracaena sanderiana',
            'alias': '开运竹、万年竹',
            'wiki_title': '富貴竹',
            'category': '水培植物',
            'summary': '富贵竹又名开运竹、万年竹，为龙血树属常绿观叶植物，原产非洲，茎节似竹而非真正竹类，叶色翠绿，常用于室内盆栽和水培造型，寓意富贵平安。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'high',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '普通室内湿度即可，保持水质清洁更重要。',
            'soil_requirement': '可水培，也可用疏松土壤盆栽。',
            'fertilizer_tips': '水培时少量营养液即可，过量易烧根。',
            'pruning_tips': '顶部过高时可截短重新扦插。',
            'propagation': '茎段扦插成活率高。',
            'common_problems': '黄叶多与水质差、温度低或强光照射有关。',
            'care_tips': '水培需勤换水，避免长期阳光暴晒。',
            'tags': ['新手友好', '水培', '室内友好', '观叶'],
        },
        {
            'name': '铜钱草',
            'scientific_name': 'Hydrocotyle verticillata',
            'alias': '香菇草',
            'wiki_title': '天胡荽',
            'category': '水培植物',
            'summary': '铜钱草通常指天胡荽属观赏植物，叶片圆润如钱币，茎匍匐生长，适合水培、半水培和浅盆栽培，是常见的小型桌面观叶植物。',
            'difficulty': 'easy',
            'light_requirement': 'partial_sun',
            'water_requirement': 'high',
            'temperature_min': 8,
            'temperature_max': 32,
            'humidity': '喜湿环境，基质不能长期干透。',
            'soil_requirement': '适合水培、浅水盆栽或保水性较强的混合土。',
            'fertilizer_tips': '生长期少量多次补肥即可。',
            'pruning_tips': '定期修剪老叶和过密叶柄。',
            'propagation': '分株和匍匐茎繁殖都很容易。',
            'common_problems': '叶片变小或发黄通常与缺光、缺肥有关。',
            'care_tips': '给予充足散射光或柔和日照，保持水分稳定。',
            'tags': ['新手友好', '水培', '喜光', '观叶'],
        },
        {
            'name': '罗勒',
            'scientific_name': 'Ocimum basilicum',
            'alias': '九层塔',
            'wiki_title': '羅勒',
            'category': '香草植物',
            'summary': '罗勒又名九层塔、金不换，为唇形科一年生或短命多年生香草植物，叶、茎和花序含芳香油，常用于烹饪调味、香草茶和家庭阳台种植。',
            'difficulty': 'easy',
            'light_requirement': 'full_sun',
            'water_requirement': 'medium',
            'temperature_min': 12,
            'temperature_max': 35,
            'humidity': '温暖通风环境最适宜，避免长期闷湿。',
            'soil_requirement': '肥沃疏松、排水良好的栽培土。',
            'fertilizer_tips': '生长期每2周补充一次薄肥。',
            'pruning_tips': '常摘心和采叶有助于分枝。',
            'propagation': '播种和扦插均可。',
            'common_problems': '徒长多因缺光，烂根多因积水和闷热。',
            'care_tips': '保持充足光照，及时摘除花序可延长采收期。',
            'tags': ['可食用', '香气', '喜光', '新手友好'],
        },
        {
            'name': '迷迭香',
            'scientific_name': 'Salvia rosmarinus',
            'alias': '罗斯玛丽',
            'wiki_title': '迷迭香',
            'category': '香草植物',
            'summary': '迷迭香为唇形科常绿亚灌木，原产地中海沿岸，枝叶狭长并带浓郁芳香，可作香草调料、观赏植物和芳香植物，喜光、耐旱但不耐涝。',
            'difficulty': 'medium',
            'light_requirement': 'full_sun',
            'water_requirement': 'low',
            'temperature_min': 5,
            'temperature_max': 32,
            'humidity': '偏干燥通风的环境更适合生长。',
            'soil_requirement': '排水良好的砂质土壤。',
            'fertilizer_tips': '薄肥即可，忌浓肥。',
            'pruning_tips': '花后或生长旺季轻剪，促进侧枝萌发。',
            'propagation': '可扦插繁殖。',
            'common_problems': '黄叶多与积水和通风差有关。',
            'care_tips': '尽量放在光照充足的位置，浇水遵循见干见湿。',
            'tags': ['香气', '可食用', '喜光', '耐旱', '驱蚊'],
        },
        {
            'name': '茉莉',
            'scientific_name': 'Jasminum sambac',
            'alias': '茉莉花',
            'wiki_title': '茉莉花',
            'category': '开花植物',
            'summary': '茉莉花为木犀科素馨属灌木，原产印度及周边热带地区，花朵洁白芬芳，常用于观赏、窨制花茶以及提取香精，是中国南方常见香花植物。',
            'difficulty': 'medium',
            'light_requirement': 'full_sun',
            'water_requirement': 'medium',
            'temperature_min': 8,
            'temperature_max': 34,
            'humidity': '温暖湿润并保持通风更利于开花。',
            'soil_requirement': '微酸性、肥沃透气的栽培土。',
            'fertilizer_tips': '花前增施磷钾肥，生长期薄肥勤施。',
            'pruning_tips': '花后及时短截，促进新枝和二次开花。',
            'propagation': '扦插繁殖较常见。',
            'common_problems': '不开花常因缺光或枝条过老。',
            'care_tips': '日照越足花越香，花期注意补肥和通风。',
            'tags': ['观花', '香气', '喜光'],
        },
        {
            'name': '栀子花',
            'scientific_name': 'Gardenia jasminoides',
            'alias': '栀子',
            'wiki_title': '梔子',
            'category': '开花植物',
            'summary': '栀子花为茜草科栀子属常绿灌木，花色洁白、香气清雅，是典型的香花植物之一，兼具庭院观赏、盆栽应用以及花果利用价值。',
            'difficulty': 'hard',
            'light_requirement': 'partial_sun',
            'water_requirement': 'medium',
            'temperature_min': 10,
            'temperature_max': 32,
            'humidity': '喜湿润和通风的环境。',
            'soil_requirement': '偏酸性、透气保水的培养土。',
            'fertilizer_tips': '生长期补充酸性肥和磷钾肥。',
            'pruning_tips': '花后修剪残花和过密枝。',
            'propagation': '扦插和压条繁殖均可。',
            'common_problems': '黄叶常与缺铁、碱化或浇水不当有关。',
            'care_tips': '养护重点在于酸性环境、通风与稳定光照。',
            'tags': ['观花', '香气'],
        },
        {
            'name': '蝴蝶兰',
            'scientific_name': 'Phalaenopsis spp.',
            'alias': '蝶兰',
            'wiki_title': '蝴蝶蘭',
            'category': '开花植物',
            'summary': '蝴蝶兰属兰科附生性植物，多生于热带和亚热带雨林树干上，花形似蝶、花期较长，因观赏价值高而被誉为“洋兰王后”，常见于年宵花和室内盆栽。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 15,
            'temperature_max': 30,
            'humidity': '喜欢空气湿度60%以上的环境。',
            'soil_requirement': '常用树皮、水苔等透气基质栽培。',
            'fertilizer_tips': '薄肥勤施，花期适度减少施肥。',
            'pruning_tips': '花谢后可根据花梗状态决定短截位置。',
            'propagation': '组培为主，家庭中偶见高芽繁殖。',
            'common_problems': '烂根常与积水和闷湿有关。',
            'care_tips': '重点是通风、散射光和根系透气。',
            'tags': ['观花', '高湿', '室内友好'],
        },
        {
            'name': '君子兰',
            'scientific_name': 'Clivia miniata',
            'alias': '大花君子兰',
            'wiki_title': '君子蘭',
            'category': '开花植物',
            'summary': '君子兰为石蒜科多年生常绿草本，原产非洲南部亚热带森林，叶片厚实整齐、花序端庄，适合温室和室内盆栽观赏，喜半阴凉爽环境。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'low',
            'temperature_min': 8,
            'temperature_max': 28,
            'humidity': '普通室内湿度即可，忌盆土长期潮湿。',
            'soil_requirement': '疏松肥沃且排水良好的腐殖土。',
            'fertilizer_tips': '生长期薄肥勤施，孕蕾期补磷钾。',
            'pruning_tips': '及时去除残花和老叶。',
            'propagation': '分株繁殖较常见。',
            'common_problems': '夹箭、不开花通常与温差不足或养分失衡有关。',
            'care_tips': '重视秋冬养护节奏和昼夜温差。',
            'tags': ['观花', '室内友好'],
        },
        {
            'name': '月季',
            'scientific_name': 'Rosa chinensis',
            'alias': '月月红',
            'wiki_title': '月季',
            'category': '开花植物',
            'summary': '月季为蔷薇科蔷薇属观赏灌木，花色与花型丰富、开花周期长，是庭院、阳台和城市绿化中最常见的观花植物之一。',
            'difficulty': 'medium',
            'light_requirement': 'full_sun',
            'water_requirement': 'medium',
            'temperature_min': -10,
            'temperature_max': 35,
            'humidity': '通风良好比高湿更重要。',
            'soil_requirement': '疏松肥沃、排水良好的微酸性土壤。',
            'fertilizer_tips': '花前花后及时追肥，重视有机肥和磷钾肥。',
            'pruning_tips': '花后回剪和冬季修剪都很关键。',
            'propagation': '扦插和嫁接均可。',
            'common_problems': '白粉病、黑斑病和虫害是常见难题。',
            'care_tips': '想开好花必须保证日照、通风和持续补肥。',
            'tags': ['观花', '喜光', '耐寒'],
        },
        {
            'name': '绣球',
            'scientific_name': 'Hydrangea macrophylla',
            'alias': '八仙花',
            'wiki_title': '繡球花',
            'category': '开花植物',
            'summary': '绣球又名八仙花、紫阳花，为绣球花科落叶灌木，伞房状花序近球形，花量大且花色会受土壤酸碱度影响，是经典的园艺观赏花木。',
            'difficulty': 'medium',
            'light_requirement': 'partial_sun',
            'water_requirement': 'high',
            'temperature_min': -5,
            'temperature_max': 30,
            'humidity': '喜湿润，炎热季节尤其不能缺水。',
            'soil_requirement': '肥沃疏松并具有一定保水性的土壤。',
            'fertilizer_tips': '春季和花前补肥，注意控制氮肥比例。',
            'pruning_tips': '修剪需结合品种和花芽着生习性。',
            'propagation': '扦插繁殖较常见。',
            'common_problems': '焦边、萎蔫常与暴晒或缺水有关。',
            'care_tips': '夏季半阴最稳妥，保持水分和通风很关键。',
            'tags': ['观花', '高湿'],
        },
        {
            'name': '橡皮树',
            'scientific_name': 'Ficus elastica',
            'alias': '印度榕',
            'wiki_title': '印度橡膠榕',
            'category': '观叶植物',
            'summary': '橡皮树又名印度榕，为桑科榕属常绿乔木，叶片厚革质且富有光泽，含白色乳汁，既可作盆栽观叶植物，也常用于室内空间绿化布置。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'low',
            'temperature_min': 10,
            'temperature_max': 32,
            'humidity': '普通室内环境即可。',
            'soil_requirement': '疏松透气、排水良好的培养土。',
            'fertilizer_tips': '生长期每月施一次复合肥。',
            'pruning_tips': '春季可打顶促发侧枝。',
            'propagation': '扦插和高压繁殖均可。',
            'common_problems': '掉叶常与低温、缺光或浇水不当有关。',
            'care_tips': '适当控水并保持明亮散射光，叶片会更有光泽。',
            'tags': ['观叶', '室内友好', '净化空气'],
        },
        {
            'name': '琴叶榕',
            'scientific_name': 'Ficus lyrata',
            'alias': '琴叶橡皮树',
            'wiki_title': '琴葉榕',
            'category': '观叶植物',
            'summary': '琴叶榕为桑科榕属木本植物，因叶片形似提琴而得名，株形挺拔、叶片厚大，常作为现代家居与商业空间中的大型观叶植物。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'low',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '喜欢稳定环境，湿度40%-70%较适宜。',
            'soil_requirement': '透气排水良好的营养土。',
            'fertilizer_tips': '春夏每月补一次均衡肥。',
            'pruning_tips': '打顶可控制高度并促进分枝。',
            'propagation': '扦插和高压繁殖。',
            'common_problems': '黑斑和落叶常与浇水过多及环境变化大有关。',
            'care_tips': '不宜频繁挪动位置，养护节奏要稳定。',
            'tags': ['观叶', '室内友好'],
        },
        {
            'name': '豆瓣绿',
            'scientific_name': 'Peperomia obtusifolia',
            'alias': '圆叶椒草',
            'wiki_title': '椒草',
            'category': '观叶植物',
            'summary': '豆瓣绿为胡椒科多年生常绿草本，植株小巧、茎叶肉质、叶色浓绿有光泽，常作为桌面和书架上的小型盆栽观叶植物。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'low',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '适应普通室内湿度。',
            'soil_requirement': '疏松透气的颗粒型营养土。',
            'fertilizer_tips': '薄肥勤施即可，避免浓肥。',
            'pruning_tips': '可摘心促使株型更丰满。',
            'propagation': '叶插和枝插都较容易。',
            'common_problems': '烂根常由浇水过勤造成。',
            'care_tips': '宁可略干也不要过湿，适合新手练手。',
            'tags': ['新手友好', '观叶', '室内友好'],
        },
        {
            'name': '常春藤',
            'scientific_name': 'Hedera helix',
            'alias': '洋常春藤',
            'wiki_title': '常春藤',
            'category': '藤蔓植物',
            'summary': '常春藤为五加科常绿攀援植物，枝蔓柔韧、叶形变化丰富，既可垂吊也可攀附支架生长，是经典的室内外立体绿化植物。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 5,
            'temperature_max': 28,
            'humidity': '喜较高空气湿度，但也需良好通风。',
            'soil_requirement': '疏松透气的腐殖土更利于生长。',
            'fertilizer_tips': '生长期每月施一次薄肥。',
            'pruning_tips': '常修剪可促进分枝和更密的垂吊效果。',
            'propagation': '枝条扦插极易成活。',
            'common_problems': '红蜘蛛和叶片干尖多与闷热干燥有关。',
            'care_tips': '适合明亮散射光环境，夏季注意降温通风。',
            'tags': ['攀援', '垂吊', '净化空气', '观叶'],
        },
        {
            'name': '合果芋',
            'scientific_name': 'Syngonium podophyllum',
            'alias': '箭叶芋',
            'wiki_title': '合果芋',
            'category': '藤蔓植物',
            'summary': '合果芋为天南星科多年生蔓性常绿草本，茎节具气生根，幼叶多呈箭形，成熟后叶形可分裂变化，常用于垂吊、立柱和室内热带造景。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '喜欢湿润环境，湿度50%以上更佳。',
            'soil_requirement': '疏松肥沃的基质，保持透气。',
            'fertilizer_tips': '春夏每月施1到2次薄肥。',
            'pruning_tips': '适当修剪长蔓，促进株型丰满。',
            'propagation': '茎段扦插容易生根。',
            'common_problems': '叶色发淡通常与缺光或缺肥有关。',
            'care_tips': '适合明亮室内环境，可搭配支柱引导攀爬。',
            'tags': ['攀援', '垂吊', '观叶', '室内友好'],
        },
        {
            'name': '爱之蔓',
            'scientific_name': 'Ceropegia woodii',
            'alias': '心叶吊灯花',
            'wiki_title': '愛之蔓',
            'category': '藤蔓植物',
            'summary': '爱之蔓为萝藦科吊灯花属多年生多肉植物，原产南非，叶片呈心形、藤蔓细长下垂，根部具块茎，耐旱性强，是人气很高的垂吊型多肉。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'low',
            'temperature_min': 10,
            'temperature_max': 30,
            'humidity': '偏干燥环境更稳妥。',
            'soil_requirement': '排水透气好的多肉颗粒土。',
            'fertilizer_tips': '生长期少量补肥即可。',
            'pruning_tips': '藤蔓过长时可回剪并再扦插。',
            'propagation': '扦插和珠芽繁殖都较容易。',
            'common_problems': '黑腐和徒长常因积水、缺光造成。',
            'care_tips': '保持光线明亮和盆土偏干，可长得更紧凑。',
            'tags': ['垂吊', '耐旱', '观叶'],
        },
        {
            'name': '吊竹梅',
            'scientific_name': 'Tradescantia zebrina',
            'alias': '紫露草',
            'wiki_title': '吊竹梅',
            'category': '藤蔓植物',
            'summary': '吊竹梅为鸭跖草科多年生常绿蔓生草本，原产墨西哥，叶面具银白与紫绿色条纹，茎蔓匍匐或悬垂，生命力强，适合吊盆和地被栽培。',
            'difficulty': 'easy',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 10,
            'temperature_max': 32,
            'humidity': '普通室内湿度即可。',
            'soil_requirement': '疏松排水的常规栽培土。',
            'fertilizer_tips': '生长期每月施一次薄肥。',
            'pruning_tips': '多摘心可促进爆盆。',
            'propagation': '枝条扦插极易成活。',
            'common_problems': '茎节拉长多因光照不足。',
            'care_tips': '光线明亮时叶色更鲜艳，但要避免正午暴晒。',
            'tags': ['垂吊', '观叶', '新手友好'],
        },
        {
            'name': '鹿角蕨',
            'scientific_name': 'Platycerium bifurcatum',
            'alias': '麋角羊齿',
            'wiki_title': '鹿角蕨',
            'category': '蕨类植物',
            'summary': '鹿角蕨造型奇特，叶片像鹿角一样分叉，是近年来特别受欢迎的板植植物。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 12,
            'temperature_max': 30,
            'humidity': '偏爱高湿和空气流通的环境。',
            'soil_requirement': '常附生在板材、水苔或树皮基质上。',
            'fertilizer_tips': '生长期低浓度补肥即可。',
            'pruning_tips': '一般不修剪功能叶，保持基质清洁即可。',
            'propagation': '分株繁殖为主。',
            'common_problems': '叶片干尖和生长停滞常与湿度不足有关。',
            'care_tips': '重视空气湿度和通风，不宜暴晒。',
            'tags': ['高湿', '观叶', '喜阴'],
        },
        {
            'name': '袖珍椰子',
            'scientific_name': 'Chamaedorea elegans',
            'alias': '客厅椰子',
            'wiki_title': '袖珍椰子',
            'category': '观叶植物',
            'summary': '袖珍椰子株型轻盈优雅，耐阴性好，是办公室和客厅的常见小型棕榈植物。',
            'difficulty': 'easy',
            'light_requirement': 'shade',
            'water_requirement': 'medium',
            'temperature_min': 10,
            'temperature_max': 30,
            'humidity': '喜欢温暖湿润环境，注意空气流通。',
            'soil_requirement': '疏松透气、含腐殖质的培养土。',
            'fertilizer_tips': '生长期每月施一次薄肥。',
            'pruning_tips': '剪掉老黄叶即可。',
            'propagation': '播种为主，家庭中以购买成株为主。',
            'common_problems': '干尖常与空气干燥或强光有关。',
            'care_tips': '适合北向窗和办公环境，但不能长期积水。',
            'tags': ['喜阴', '室内友好', '观叶', '净化空气'],
        },
        {
            'name': '芦荟',
            'scientific_name': 'Aloe vera',
            'alias': '库拉索芦荟',
            'wiki_title': '蘆薈',
            'category': '多肉植物',
            'summary': '芦荟叶片肉质饱满，适合阳台窗台栽培，兼具观赏性和较高的日常认知度。',
            'difficulty': 'easy',
            'light_requirement': 'full_sun',
            'water_requirement': 'low',
            'temperature_min': 5,
            'temperature_max': 35,
            'humidity': '偏干燥环境更适合。',
            'soil_requirement': '适合颗粒较多、排水快的多肉土。',
            'fertilizer_tips': '生长期少量补肥即可。',
            'pruning_tips': '剪除老叶和侧芽，便于通风。',
            'propagation': '分株繁殖非常常见。',
            'common_problems': '叶片软烂通常与积水和低温有关。',
            'care_tips': '充足日照和少浇水是养好芦荟的关键。',
            'tags': ['新手友好', '耐旱', '喜光'],
        },
        {
            'name': '玉树',
            'scientific_name': 'Crassula ovata',
            'alias': '燕子掌',
            'wiki_title': '燕子掌',
            'category': '多肉植物',
            'summary': '玉树枝干木质化明显，叶片圆厚，养成老桩后观赏性很强。',
            'difficulty': 'easy',
            'light_requirement': 'full_sun',
            'water_requirement': 'low',
            'temperature_min': 5,
            'temperature_max': 32,
            'humidity': '偏干燥环境较好。',
            'soil_requirement': '疏松透气的多肉土或砂质土。',
            'fertilizer_tips': '生长期每月少量施肥一次。',
            'pruning_tips': '可通过修剪塑造树状造型。',
            'propagation': '叶插和枝插都容易。',
            'common_problems': '黑腐和掉叶常因积水或寒冷。',
            'care_tips': '给足光照并适当控水，枝叶会更紧凑。',
            'tags': ['耐旱', '喜光', '新手友好'],
        },
        {
            'name': '熊童子',
            'scientific_name': 'Cotyledon tomentosa',
            'alias': '绿熊',
            'wiki_title': '熊童子',
            'category': '多肉植物',
            'summary': '熊童子叶片顶端像小熊爪，绒毛感明显，是多肉爱好者很喜欢的萌系品种。',
            'difficulty': 'medium',
            'light_requirement': 'full_sun',
            'water_requirement': 'low',
            'temperature_min': 5,
            'temperature_max': 30,
            'humidity': '喜欢凉爽干燥、通风良好的环境。',
            'soil_requirement': '颗粒比例较高的多肉专用土。',
            'fertilizer_tips': '薄肥少量即可。',
            'pruning_tips': '去掉徒长枝，保持株型。',
            'propagation': '扦插繁殖为主。',
            'common_problems': '夏季黑腐和掉叶是常见风险。',
            'care_tips': '重点避免高温闷湿，保持充足光照。',
            'tags': ['耐旱', '喜光', '观叶'],
        },
        {
            'name': '豆瓣兰',
            'scientific_name': 'Cymbidium goeringii',
            'alias': '春兰',
            'wiki_title': '春蘭',
            'category': '开花植物',
            'summary': '豆瓣兰叶姿雅致、花香清幽，适合喜欢传统东方花卉气质的养花人。',
            'difficulty': 'hard',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 5,
            'temperature_max': 28,
            'humidity': '偏爱通风和较高空气湿度。',
            'soil_requirement': '兰花专用透气颗粒基质。',
            'fertilizer_tips': '薄肥勤施，忌浓肥和高盐分。',
            'pruning_tips': '花谢后及时剪除花梗。',
            'propagation': '分株繁殖。',
            'common_problems': '烂根多由通风差和浇水不当导致。',
            'care_tips': '兰科植物养护的关键是透气、洁净和稳定。',
            'tags': ['观花', '香气', '高湿'],
        },
        {
            'name': '薄雪万年草',
            'scientific_name': 'Sedum hispanicum',
            'alias': '姬星美人近缘种',
            'wiki_title': '景天屬',
            'category': '多肉植物',
            'summary': '薄雪万年草叶片细小，容易群生和铺面，常被用于多肉拼盆与造景。',
            'difficulty': 'easy',
            'light_requirement': 'full_sun',
            'water_requirement': 'low',
            'temperature_min': -5,
            'temperature_max': 32,
            'humidity': '通风干燥更利于状态稳定。',
            'soil_requirement': '排水快的颗粒型多肉土。',
            'fertilizer_tips': '一般少量补肥即可。',
            'pruning_tips': '可修剪徒长枝进行补栽。',
            'propagation': '扦插极其容易。',
            'common_problems': '徒长和黑腐是常见问题。',
            'care_tips': '多晒太阳、少浇水，能更快形成紧密群生。',
            'tags': ['新手友好', '耐旱', '喜光'],
        },
        {
            'name': '空气凤梨',
            'scientific_name': 'Tillandsia',
            'alias': '铁兰',
            'wiki_title': '鐵蘭屬',
            'category': '观叶植物',
            'summary': '空气凤梨无需土壤即可附生生长，造型自由，适合做现代感十足的悬挂装饰。',
            'difficulty': 'medium',
            'light_requirement': 'indirect',
            'water_requirement': 'medium',
            'temperature_min': 10,
            'temperature_max': 30,
            'humidity': '喜欢通风和较高空气湿度。',
            'soil_requirement': '无需土壤，可附着在木板、石头或铁艺架上。',
            'fertilizer_tips': '偶尔用极低浓度叶面肥喷施即可。',
            'pruning_tips': '清理干枯叶片即可。',
            'propagation': '通过侧芽分株繁殖。',
            'common_problems': '叶尖发干多因湿度不足或浸泡后不通风。',
            'care_tips': '喷水或短时浸泡后务必倒置晾干。',
            'tags': ['观叶', '室内友好', '高湿'],
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0)
        parser.add_argument('--refresh', action='store_true')
        parser.add_argument('--pause', type=float, default=0.15)

    def handle(self, *args, **options):
        self.user_agent = 'plant-community-data-bot/1.0'

        self.ensure_categories()
        self.ensure_tags()

        limit = options['limit']
        refresh = options['refresh']
        pause = options['pause']
        catalog = self.PLANT_CATALOG[:limit] if limit and limit > 0 else self.PLANT_CATALOG

        created_count = 0
        updated_count = 0
        skipped_count = 0
        api_hit_count = 0

        self.stdout.write(f'开始在线扩充植物数据，共 {len(catalog)} 条...')

        for index, item in enumerate(catalog, start=1):
            wiki_data = self.fetch_wiki_data(item)
            if wiki_data.get('extract'):
                api_hit_count += 1

            _, action = self.save_plant(item, wiki_data, refresh=refresh)

            if action == 'created':
                created_count += 1
            elif action == 'updated':
                updated_count += 1
            else:
                skipped_count += 1

            source = wiki_data.get('title', 'fallback') if wiki_data else 'fallback'
            self.stdout.write(f'[{index}/{len(catalog)}] {item["name"]} -> {action} ({source})')

            if pause and index < len(catalog):
                time.sleep(pause)

        self.stdout.write(
            self.style.SUCCESS(
                f'扩充完成：created={created_count}, updated={updated_count}, skipped={skipped_count}, api_hit={api_hit_count}'
            )
        )

    def ensure_categories(self):
        for category_data in self.CATEGORY_DEFS:
            PlantCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data,
            )

    def ensure_tags(self):
        for name, color in self.TAG_DEFS.items():
            PlantTag.objects.get_or_create(
                name=name,
                defaults={'color': color},
            )

    def request_json(self, params):
        url = f"https://zh.wikipedia.org/w/api.php?{urlencode(params)}"
        request = Request(url, headers={'User-Agent': self.user_agent})
        try:
            with urlopen(request, timeout=12) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            return {}

    def fetch_wiki_data(self, item):
        candidates = [
            item.get('wiki_title'),
            item.get('name'),
            item.get('scientific_name'),
            item.get('alias', '').split('、')[0] if item.get('alias') else None,
        ]

        visited = set()
        for candidate in candidates:
            title = (candidate or '').strip()
            if not title or title in visited:
                continue
            visited.add(title)
            result = self.fetch_extract_by_title(title)
            if result:
                return result

        return self.search_and_fetch(item.get('name', ''), item.get('scientific_name', ''))

    def fetch_extract_by_title(self, title):
        params = {
            'action': 'query',
            'prop': 'extracts',
            'titles': title,
            'exintro': 1,
            'explaintext': 1,
            'redirects': 1,
            'format': 'json',
            'utf8': 1,
        }

        data = self.request_json(params)
        if not data:
            return {}

        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            if page.get('missing') is not None:
                continue
            extract = self.normalize_text(page.get('extract', ''))
            if extract:
                return {
                    'title': page.get('title', title),
                    'extract': self.trim_text(extract, 220),
                }
        return {}

    def search_and_fetch(self, chinese_name, scientific_name):
        keywords = [keyword for keyword in [chinese_name, scientific_name] if keyword]

        for keyword in keywords:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': keyword,
                'srlimit': 5,
                'format': 'json',
                'utf8': 1,
            }

            data = self.request_json(params)
            if not data:
                continue

            titles = [item.get('title', '') for item in data.get('query', {}).get('search', []) if item.get('title')]
            for title in self.rank_titles(chinese_name or keyword, titles):
                result = self.fetch_extract_by_title(title)
                if result:
                    return result

        return {}

    def rank_titles(self, keyword, titles):
        normalized_keyword = (keyword or '').replace(' ', '').lower()
        exact = []
        contains = []
        others = []

        for title in titles:
            normalized_title = title.replace(' ', '').lower()
            if normalized_title == normalized_keyword:
                exact.append(title)
            elif normalized_keyword and (normalized_keyword in normalized_title or normalized_title in normalized_keyword):
                contains.append(title)
            else:
                others.append(title)

        return exact + contains + others

    def save_plant(self, item, wiki_data, refresh=False):
        category = PlantCategory.objects.get(name=item['category'])
        defaults = {
            'scientific_name': item['scientific_name'],
            'alias': item['alias'],
            'category': category,
            'description': self.build_description(item, wiki_data),
            'difficulty': item['difficulty'],
            'light_requirement': item['light_requirement'],
            'water_requirement': item['water_requirement'],
            'temperature_min': item['temperature_min'],
            'temperature_max': item['temperature_max'],
            'humidity': item['humidity'],
            'soil_requirement': item['soil_requirement'],
            'fertilizer_tips': item['fertilizer_tips'],
            'pruning_tips': item['pruning_tips'],
            'propagation': item['propagation'],
            'common_problems': item['common_problems'],
            'care_tips': item['care_tips'],
            'is_active': True,
        }

        plant = Plant.objects.filter(name=item['name']).first()
        if plant is None:
            plant = Plant.objects.create(name=item['name'], **defaults)
            action = 'created'
        else:
            changed = self.update_existing_plant(plant, defaults, refresh=refresh)
            action = 'updated' if changed else 'skipped'

        self.sync_tags(plant, item['tags'], refresh=refresh)
        return plant, action

    def update_existing_plant(self, plant, defaults, refresh=False):
        changed = False

        for field, value in defaults.items():
            if field == 'category':
                current_value = plant.category_id
                target_value = value.id if value else None
                if refresh:
                    if current_value != target_value:
                        plant.category = value
                        changed = True
                else:
                    if current_value is None and target_value is not None:
                        plant.category = value
                        changed = True
                continue

            current_value = getattr(plant, field)
            if refresh:
                if current_value != value:
                    setattr(plant, field, value)
                    changed = True
            else:
                if current_value in [None, ''] and value not in [None, '']:
                    setattr(plant, field, value)
                    changed = True

        if changed:
            plant.save()

        return changed

    def sync_tags(self, plant, tag_names, refresh=False):
        current_names = set(
            plant.tag_relations.select_related('tag').values_list('tag__name', flat=True)
        )

        for tag in PlantTag.objects.filter(name__in=tag_names):
            if tag.name not in current_names:
                PlantTagRelation.objects.get_or_create(plant=plant, tag=tag)

        if refresh:
            plant.tag_relations.exclude(tag__name__in=tag_names).delete()

    def build_description(self, item, wiki_data):
        summary = self.normalize_text(wiki_data.get('extract', '')) if wiki_data else ''
        if not summary:
            summary = item['summary']
        return self.trim_text(summary, 220)

    def normalize_text(self, text):
        text = re.sub(r'\[[0-9]+\]', '', text or '')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def trim_text(self, text, limit=220):
        value = (text or '').strip()
        if len(value) <= limit:
            return value
        return value[:limit].rstrip('，,、；; ') + '。'


Command.CATEGORY_DEFS = CATEGORY_DEFS
Command.TAG_DEFS = TAG_DEFS
Command.PLANT_CATALOG = PLANT_CATALOG


if __name__ == "__main__":
    Command().run_from_argv([sys.argv[0], 'crawl_plant_data', *sys.argv[1:]])

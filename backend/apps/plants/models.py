from django.db import models


class PlantCategory(models.Model):
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('分类描述', blank=True)
    icon = models.CharField('图标', max_length=50, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='父分类')
    order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '植物分类'
        verbose_name_plural = verbose_name
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name


class Plant(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', '容易'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    LIGHT_CHOICES = [
        ('full_sun', '全日照'),
        ('partial_sun', '半日照'),
        ('shade', '阴凉'),
        ('indirect', '散射光'),
    ]
    
    WATER_CHOICES = [
        ('low', '少量'),
        ('medium', '适中'),
        ('high', '大量'),
    ]
    
    name = models.CharField('植物名称', max_length=100)
    scientific_name = models.CharField('学名', max_length=200, blank=True)
    alias = models.CharField('别名', max_length=200, blank=True)
    category = models.ForeignKey(PlantCategory, on_delete=models.SET_NULL, null=True,
                                  related_name='plants', verbose_name='分类')
    image = models.ImageField('图片', upload_to='plants/', null=True, blank=True)
    description = models.TextField('简介')
    
    difficulty = models.CharField('养护难度', max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    light_requirement = models.CharField('光照需求', max_length=20, choices=LIGHT_CHOICES, default='indirect')
    water_requirement = models.CharField('浇水需求', max_length=20, choices=WATER_CHOICES, default='medium')
    temperature_min = models.IntegerField('最低温度(℃)', default=10)
    temperature_max = models.IntegerField('最高温度(℃)', default=30)
    humidity = models.CharField('湿度要求', max_length=100, blank=True)
    
    soil_requirement = models.TextField('土壤要求', blank=True)
    fertilizer_tips = models.TextField('施肥建议', blank=True)
    pruning_tips = models.TextField('修剪建议', blank=True)
    propagation = models.TextField('繁殖方式', blank=True)
    common_problems = models.TextField('常见问题', blank=True)
    care_tips = models.TextField('养护要点', blank=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    view_count = models.IntegerField('浏览次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '植物'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class PlantTag(models.Model):
    name = models.CharField('标签名称', max_length=50, unique=True)
    color = models.CharField('标签颜色', max_length=20, default='#4CAF50')
    
    class Meta:
        verbose_name = '植物标签'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name


class PlantTagRelation(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(PlantTag, on_delete=models.CASCADE, related_name='plant_relations')
    
    class Meta:
        verbose_name = '植物标签关联'
        verbose_name_plural = verbose_name
        unique_together = ['plant', 'tag']


class UserPlant(models.Model):
    from apps.users.models import User
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collected_plants')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='collectors')
    nickname = models.CharField('昵称', max_length=50, blank=True)
    notes = models.TextField('备注', blank=True)
    acquired_date = models.DateField('获得日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户植物'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'plant']
        
    def __str__(self):
        return f"{self.user.username} - {self.plant.name}"


class CareRecord(models.Model):
    from apps.users.models import User
    
    CARE_TYPE_CHOICES = [
        ('water', '浇水'),
        ('fertilize', '施肥'),
        ('prune', '修剪'),
        ('repot', '换盆'),
        ('pest_control', '病虫害防治'),
        ('other', '其他'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='care_records')
    user_plant = models.ForeignKey(UserPlant, on_delete=models.CASCADE, related_name='care_records')
    care_type = models.CharField('养护类型', max_length=20, choices=CARE_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    image = models.ImageField('图片', upload_to='care_records/', null=True, blank=True)
    care_date = models.DateField('养护日期')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '养护记录'
        verbose_name_plural = verbose_name
        ordering = ['-care_date']
        
    def __str__(self):
        return f"{self.user_plant} - {self.get_care_type_display()}"

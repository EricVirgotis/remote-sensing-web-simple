<!-- 分类分析结果详情页面 -->
<template>
  <div class="app-container">
    <!-- 结果概览 -->
    <el-card class="result-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2 class="card-title">分类结果概览</h2>
          <div class="card-actions">
            <el-button type="primary" @click="downloadResult">
              <el-icon><Download /></el-icon> 下载结果
            </el-button>
            <el-button @click="goBack">
              <el-icon><Back /></el-icon> 返回列表
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border size="large">
        <el-descriptions-item label="任务名称">{{ result.name || '未命名任务' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ result.createTime }}</el-descriptions-item>
        <el-descriptions-item label="分类模型">{{ result.modelName }}</el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(result.status)">
            {{ getStatusText(result.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="原始影像">
          <el-button link type="primary" @click="viewOriginalImage">查看原图</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="处理时间">{{ result.processTime || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 分类结果展示 -->
    <div class="result-display">
      <el-row :gutter="20">
        <!-- 左侧：分类图 -->
        <el-col :span="16">
          <el-card shadow="hover" class="image-card">
            <template #header>
              <div class="card-header">
                <h3>分类结果图</h3>
                <el-radio-group v-model="currentView" size="small">
                  <el-radio-button label="classification">分类图</el-radio-button>
                  <el-radio-button label="original">原始图像</el-radio-button>
                  <el-radio-button label="comparison">对比视图</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            
            <div class="image-container">
              <!-- 分类图 -->
              <div v-show="currentView === 'classification'" class="image-view">
                <img :src="result.classificationImageUrl" alt="分类结果图" class="result-image" />
                <div class="image-legend">
                  <div v-for="(item, index) in legend" :key="index" class="legend-item">
                    <div class="color-box" :style="{ backgroundColor: item.color }"></div>
                    <span>{{ item.name }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 原始图像 -->
              <div v-show="currentView === 'original'" class="image-view">
                <img :src="result.originalImageUrl" alt="原始图像" class="result-image" />
              </div>
              
              <!-- 对比视图 -->
              <div v-show="currentView === 'comparison'" class="comparison-view">
                <div class="comparison-container">
                  <div class="comparison-slider" ref="sliderRef">
                    <div class="comparison-original">
                      <img :src="result.originalImageUrl" alt="原始图像" class="comparison-image" />
                    </div>
                    <div class="comparison-classified" :style="{ width: `${sliderPosition}%` }">
                      <img :src="result.classificationImageUrl" alt="分类结果图" class="comparison-image" />
                    </div>
                    <div class="slider-handle" 
                         :style="{ left: `${sliderPosition}%` }"
                         @mousedown="startDrag"
                         @touchstart="startDrag">
                      <div class="handle-line"></div>
                    </div>
                  </div>
                  <div class="comparison-labels">
                    <span class="label-left">原始图像</span>
                    <span class="label-right">分类结果</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧：精度评估和统计 -->
        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <template #header>
              <div class="card-header">
                <h3>精度评估</h3>
              </div>
            </template>
            
            <div class="accuracy-metrics">
              <div class="metric-item">
                <div class="metric-label">总体精度</div>
                <div class="metric-value">{{ (result.metrics?.overallAccuracy * 100).toFixed(2) }}%</div>
                <el-progress :percentage="result.metrics?.overallAccuracy * 100" :format="() => ''" />
              </div>
              
              <div class="metric-item">
                <div class="metric-label">Kappa系数</div>
                <div class="metric-value">{{ result.metrics?.kappa.toFixed(4) }}</div>
                <el-progress :percentage="result.metrics?.kappa * 100" :format="() => ''" />
              </div>
              
              <div class="metric-item">
                <div class="metric-label">平均F1分数</div>
                <div class="metric-value">{{ (result.metrics?.f1Score * 100).toFixed(2) }}%</div>
                <el-progress :percentage="result.metrics?.f1Score * 100" :format="() => ''" />
              </div>
            </div>
            
            <div class="class-accuracy">
              <h4>各类别精度</h4>
              <div class="chart-container" ref="classAccuracyChartRef"></div>
            </div>
          </el-card>
          
          <el-card shadow="hover" class="stats-card distribution-card">
            <template #header>
              <div class="card-header">
                <h3>分类统计</h3>
              </div>
            </template>
            
            <div class="chart-container" ref="distributionChartRef"></div>
            
            <el-table :data="classDistribution" size="small" border stripe>
              <el-table-column prop="name" label="类别" />
              <el-table-column prop="area" label="面积(km²)" />
              <el-table-column prop="percentage" label="百分比">
                <template #default="{ row }">
                  {{ row.percentage }}%
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 混淆矩阵 -->
    <el-card shadow="hover" class="confusion-matrix-card">
      <template #header>
        <div class="card-header">
          <h3>混淆矩阵</h3>
          <el-tooltip content="混淆矩阵展示了分类结果与真实标签之间的对应关系，对角线表示正确分类的样本数量">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>
      
      <div class="chart-container" ref="confusionMatrixChartRef"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Back, QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const resultId = Number(route.params.id)

// 图表引用
const classAccuracyChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
const confusionMatrixChartRef = ref<HTMLElement | null>(null)

// 当前视图模式
const currentView = ref('classification')

// 滑块位置（百分比）
const sliderPosition = ref(50)
const sliderRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)

// 模拟数据 - 实际项目中应该从API获取
const result = ref({
  id: resultId,
  name: '城市建筑分类任务',
  createTime: '2023-06-15 10:30:45',
  modelName: 'ResNet50-UNet',
  status: 1, // 1: 完成, 0: 进行中, 2: 失败
  processTime: '2分钟35秒',
  originalImageUrl: 'https://img2.baidu.com/it/u=1361506290,3430055932&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=333',
  classificationImageUrl: 'https://img1.baidu.com/it/u=1407750889,3441968730&fm=253&fmt=auto&app=120&f=JPEG?w=1200&h=799',
  metrics: {
    overallAccuracy: 0.912,
    kappa: 0.876,
    f1Score: 0.894,
    classAccuracy: {
      '城市建筑': 0.925,
      '植被': 0.887,
      '水体': 0.952,
      '裸地': 0.851,
      '农田': 0.903
    }
  }
})

// 图例数据
const legend = [
  { name: '城市建筑', color: '#e74c3c' },
  { name: '植被', color: '#2ecc71' },
  { name: '水体', color: '#3498db' },
  { name: '裸地', color: '#f39c12' },
  { name: '农田', color: '#9b59b6' }
]

// 类别分布数据
const classDistribution = [
  { name: '城市建筑', area: '12.5', percentage: '25.0' },
  { name: '植被', area: '18.3', percentage: '36.6' },
  { name: '水体', area: '8.7', percentage: '17.4' },
  { name: '裸地', area: '5.2', percentage: '10.4' },
  { name: '农田', area: '5.3', percentage: '10.6' }
]

// 获取状态文本
const getStatusText = (status: number) => {
  switch (status) {
    case 0: return '进行中'
    case 1: return '已完成'
    case 2: return '失败'
    default: return '未知'
  }
}

// 获取状态类型
const getStatusType = (status: number) => {
  switch (status) {
    case 0: return 'warning'
    case 1: return 'success'
    case 2: return 'danger'
    default: return 'info'
  }
}

// 查看原始图像
const viewOriginalImage = () => {
  window.open(result.value.originalImageUrl, '_blank')
}

// 下载结果
const downloadResult = () => {
  ElMessage.success('开始下载分类结果')
  // 实际项目中应该调用API下载结果文件
}

// 返回列表
const goBack = () => {
  router.push('/result')
}

// 初始化类别精度图表
const initClassAccuracyChart = () => {
  if (!classAccuracyChartRef.value) return
  
  const chart = echarts.init(classAccuracyChartRef.value)
  
  const classNames = Object.keys(result.value.metrics.classAccuracy)
  const accuracyValues = classNames.map(name => result.value.metrics.classAccuracy[name] * 100)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '精度',
        type: 'bar',
        data: accuracyValues,
        itemStyle: {
          color: function(params: any) {
            const colorList = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6']
            return colorList[params.dataIndex % colorList.length]
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%'
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 初始化分布图表
const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  
  const chart = echarts.init(distributionChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}km² ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      data: classDistribution.map(item => item.name)
    },
    series: [
      {
        name: '面积分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: classDistribution.map((item, index) => ({
          value: item.area,
          name: item.name,
          itemStyle: {
            color: legend[index].color
          }
        }))
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 初始化混淆矩阵图表
const initConfusionMatrixChart = () => {
  if (!confusionMatrixChartRef.value) return
  
  const chart = echarts.init(confusionMatrixChartRef.value)
  
  const classNames = Object.keys(result.value.metrics.classAccuracy)
  
  // 模拟混淆矩阵数据
  const confusionMatrix = [
    [920, 30, 10, 25, 15],
    [25, 887, 18, 40, 30],
    [5, 12, 952, 8, 23],
    [30, 45, 15, 851, 59],
    [20, 26, 5, 46, 903]
  ]
  
  const data = []
  for (let i = 0; i < classNames.length; i++) {
    for (let j = 0; j < classNames.length; j++) {
      data.push([i, j, confusionMatrix[i][j]])
    }
  }
  
  const option = {
    tooltip: {
      position: 'top',
      formatter: function (params: any) {
        return `预测: ${classNames[params.data[0]]}<br>实际: ${classNames[params.data[1]]}<br>数量: ${params.data[2]}`
      }
    },
    grid: {
      left: '3%',
      right: '7%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: classNames,
      name: '预测类别',
      nameLocation: 'middle',
      nameGap: 30,
      splitArea: {
        show: true
      },
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'category',
      data: classNames,
      name: '实际类别',
      nameLocation: 'middle',
      nameGap: 40,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: 1000,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#e0f7fa', '#4dd0e1', '#0097a7', '#006064']
      }
    },
    series: [
      {
        name: '混淆矩阵',
        type: 'heatmap',
        data: data,
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 开始拖动滑块
const startDrag = (e: MouseEvent | TouchEvent) => {
  e.preventDefault()
  isDragging.value = true
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('touchmove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchend', stopDrag)
}

// 拖动中
const onDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value || !sliderRef.value) return
  
  const sliderRect = sliderRef.value.getBoundingClientRect()
  const sliderWidth = sliderRect.width
  
  let clientX
  if (e instanceof MouseEvent) {
    clientX = e.clientX
  } else {
    clientX = e.touches[0].clientX
  }
  
  const offsetX = clientX - sliderRect.left
  let percent = (offsetX / sliderWidth) * 100
  
  // 限制在0-100范围内
  percent = Math.max(0, Math.min(100, percent))
  sliderPosition.value = percent
}

// 停止拖动
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchend', stopDrag)
}

onMounted(async () => {
  // 等待DOM更新后初始化图表
  await nextTick()
  initClassAccuracyChart()
  initDistributionChart()
  initConfusionMatrixChart()
})
</script>

<style lang="scss" scoped>
.app-container {
  padding: 24px;
}

.result-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.result-display {
  margin-bottom: 24px;
}

.image-card {
  height: 100%;
}

.image-container {
  position: relative;
  min-height: 400px;
}

.image-view {
  position: relative;
}

.result-image {
  width: 100%;
  max-height: 600px;
  object-fit: contain;
  border-radius: 4px;
}

.image-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding: 12px;
  background-color: rgba(250, 250, 250, 0.9);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.comparison-view {
  position: relative;
}

.comparison-container {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}

.comparison-slider {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
  cursor: ew-resize;
}

.comparison-original,
.comparison-classified {
  position: absolute;
  top: 0;
  height: 100%;
  overflow: hidden;
}

.comparison-original {
  left: 0;
  width: 100%;
  z-index: 1;
}

.comparison-classified {
  left: 0;
  width: 50%;
  z-index: 2;
  border-right: 2px solid #fff;
}

.comparison-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slider-handle {
  position: absolute;
  top: 0;
  left: 50%;
  width: 40px;
  height: 100%;
  margin-left: -20px;
  z-index: 3;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: ew-resize;
}

.handle-line {
  width: 4px;
  height: 100%;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.comparison-labels {
  display: flex;
  justify-content: space-between;
  padding: 8px 16px;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-weight: 500;
}

.stats-card {
  margin-bottom: 20px;
}

.accuracy-metrics {
  margin-bottom: 24px;
}

.metric-item {
  margin-bottom: 16px;
}

.metric-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.class-accuracy {
  h4 {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 16px;
  }
}

.chart-container {
  height: 300px;
  margin-bottom: 16px;
}

.distribution-card .chart-container {
  height: 250px;
}

.confusion-matrix-card .chart-container {
  height: 400px;
}
</style>
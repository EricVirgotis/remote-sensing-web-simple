<!-- 遥感影像智能分类分析系统首页 -->
<template>
  <div class="home-container">
    <!-- 顶部横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">遥感影像智能分类分析系统</h1>
        <p class="hero-subtitle">基于深度学习的高精度遥感影像分类解决方案</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="navigateTo('/image/upload')">
            <el-icon><Upload /></el-icon> 上传影像
          </el-button>
          <el-button type="success" size="large" @click="navigateTo('/classification')">
            <el-icon><DataAnalysis /></el-icon> 开始分析
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <img src="@/assets/images/hero-image.svg" alt="遥感影像分析" />
      </div>
    </div>

    <!-- 功能模块 -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="feature-cards">
        <el-card class="feature-card" shadow="hover" @click="navigateTo('/image/upload')">
          <el-icon class="feature-icon"><Picture /></el-icon>
          <h3 class="feature-title">影像管理</h3>
          <p class="feature-desc">上传、管理和预处理遥感影像数据，支持多种格式</p>
        </el-card>

        <el-card class="feature-card" shadow="hover" @click="navigateTo('/classification')">
          <el-icon class="feature-icon"><DataAnalysis /></el-icon>
          <h3 class="feature-title">智能分类</h3>
          <p class="feature-desc">使用先进的深度学习模型对遥感影像进行精准分类</p>
        </el-card>

        <el-card class="feature-card" shadow="hover" @click="navigateTo('/train/dataset')">
          <el-icon class="feature-icon"><Monitor /></el-icon>
          <h3 class="feature-title">模型训练</h3>
          <p class="feature-desc">使用自定义数据集训练专业的遥感影像分类模型</p>
        </el-card>

        <el-card class="feature-card" shadow="hover" @click="navigateTo('/result')">
          <el-icon class="feature-icon"><PieChart /></el-icon>
          <h3 class="feature-title">结果分析</h3>
          <p class="feature-desc">可视化展示分类结果，提供精度评估和统计分析</p>
        </el-card>
      </div>
    </div>

    <!-- 系统概览 -->
    <div class="overview-section">
      <h2 class="section-title">系统概览</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon image-icon">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.imageCount }}</div>
              <div class="stat-label">影像总数</div>
            </div>
            <div class="stat-chart">
              <div class="stat-progress" :style="{width: `${Math.min(Number(stats.imageCount) / 50 * 100, 100)}%`}"></div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon task-icon">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.taskCount }}</div>
              <div class="stat-label">任务总数</div>
            </div>
            <div class="stat-chart">
              <div class="stat-progress" :style="{width: `${Math.min(Number(stats.taskCount) / 30 * 100, 100)}%`}"></div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon model-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.modelCount }}</div>
              <div class="stat-label">模型总数</div>
            </div>
            <div class="stat-chart">
              <div class="stat-progress" :style="{width: `${Math.min(Number(stats.modelCount) / 10 * 100, 100)}%`}"></div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon result-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.resultCount }}</div>
              <div class="stat-label">结果总数</div>
            </div>
            <div class="stat-chart">
              <div class="stat-progress" :style="{width: `${Math.min(Number(stats.resultCount) / 40 * 100, 100)}%`}"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分类精度展示 -->
    <div class="accuracy-section">
      <h2 class="section-title">分类精度</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <h3>各类别精度统计</h3>
              </div>
            </template>
            <div class="chart-container" ref="accuracyChartRef"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <h3>影像类型分布</h3>
              </div>
            </template>
            <div class="chart-container" ref="imageTypeChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近任务 -->
    <div class="recent-tasks">
      <div class="section-header">
        <h2 class="section-title">最近任务</h2>
        <el-button type="primary" text @click="navigateTo('/task/list')">
          查看全部
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>

      <el-card shadow="hover">
        <el-table :data="recentTasks" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="任务名称" min-width="180" />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewTaskDetail(row.id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 系统流程 -->
    <div class="workflow-section">
      <h2 class="section-title">使用流程</h2>
      <div class="workflow-steps">
        <div class="workflow-step">
          <div class="step-number">1</div>
          <div class="step-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <h3 class="step-title">上传影像</h3>
          <p class="step-desc">上传您的遥感影像文件，支持TIFF、JPEG、PNG等格式</p>
        </div>

        <div class="workflow-step">
          <div class="step-number">2</div>
          <div class="step-icon">
            <el-icon><Select /></el-icon>
          </div>
          <h3 class="step-title">选择模型</h3>
          <p class="step-desc">选择合适的分类模型，或使用自定义数据集训练新模型</p>
        </div>

        <div class="workflow-step">
          <div class="step-number">3</div>
          <div class="step-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <h3 class="step-title">开始分析</h3>
          <p class="step-desc">启动分类分析任务，系统将自动处理影像数据</p>
        </div>

        <div class="workflow-step">
          <div class="step-number">4</div>
          <div class="step-icon">
            <el-icon><PieChart /></el-icon>
          </div>
          <h3 class="step-title">查看结果</h3>
          <p class="step-desc">查看分类结果，包括分类图、精度评估和统计分析</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, DataAnalysis, Picture, Monitor, PieChart, ArrowRight, List, Select } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

// 加载状态
const loading = ref(false)

// 统计数据
const stats = ref({
  imageCount: '25',
  taskCount: '18',
  modelCount: '5',
  resultCount: '32'
})

// 最近任务
const recentTasks = ref([
  { id: 1, name: '城市建筑分类任务', createTime: '2023-06-15 10:30:45', status: 1 },
  { id: 2, name: '植被覆盖分析', createTime: '2023-06-14 16:22:18', status: 1 },
  { id: 3, name: '水体识别分析', createTime: '2023-06-13 09:15:32', status: 0 },
  { id: 4, name: '土地利用分类', createTime: '2023-06-12 14:45:20', status: 2 }
])

// 图表引用
const accuracyChartRef = ref<HTMLElement | null>(null)
const imageTypeChartRef = ref<HTMLElement | null>(null)

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

// 导航到指定路由
const navigateTo = (path: string) => {
  router.push(path)
}

// 查看任务详情
const viewTaskDetail = (id: number) => {
  router.push(`/task/detail/${id}`)
}

// 初始化精度统计图表
const initAccuracyChart = () => {
  if (!accuracyChartRef.value) return
  
  const chart = echarts.init(accuracyChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['城市建筑', '植被', '水体', '裸地', '农田']
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '分类精度',
        type: 'bar',
        data: [92.5, 88.7, 95.2, 85.1, 90.3],
        itemStyle: {
          color: function(params: any) {
            const colorList = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
            return colorList[params.dataIndex]
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

// 初始化影像类型分布图表
const initImageTypeChart = () => {
  if (!imageTypeChartRef.value) return
  
  const chart = echarts.init(imageTypeChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ['TIFF', 'JPEG', 'PNG', '其他']
    },
    series: [
      {
        name: '影像类型',
        type: 'pie',
        radius: ['50%', '70%'],
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
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 15, name: 'TIFF' },
          { value: 6, name: 'JPEG' },
          { value: 3, name: 'PNG' },
          { value: 1, name: '其他' }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

onMounted(async () => {
  // 等待DOM更新后初始化图表
  await nextTick()
  initAccuracyChart()
  initImageTypeChart()
})
</script>

<style lang="scss" scoped>
.home-container {
  padding: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 24px;
  position: relative;
  padding-left: 16px;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 24px;
    background-color: var(--el-color-primary);
    border-radius: 2px;
  }
}

.hero-section {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%);
  border-radius: 16px;
  padding: 60px 40px;
  margin-bottom: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
  
  @media (max-width: 768px) {
    flex-direction: column;
    padding: 40px 24px;
  }
}

.hero-content {
  flex: 1;
  z-index: 1;
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--el-color-primary);
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--el-text-color-secondary);
  margin-bottom: 32px;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  
  @media (max-width: 576px) {
    flex-direction: column;
    gap: 12px;
  }
}

.hero-image {
  flex: 0 0 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  @media (max-width: 768px) {
    margin-top: 40px;
    flex: 0 0 auto;
  }
}

.features-section {
  margin-bottom: 40px;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 576px) {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  height: 100%;
  padding: 24px;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    
    .feature-icon {
      transform: scale(1.1);
    }
  }
  
  .feature-icon {
    font-size: 48px;
    color: var(--el-color-primary);
    margin-bottom: 20px;
    transition: transform 0.3s;
  }
  
  .feature-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 12px;
  }
  
  .feature-desc {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
  }
}

.overview-section {
  margin-bottom: 40px;
}

.stat-card {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  position: relative;
  padding: 24px;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    
    .el-icon {
      font-size: 28px;
      color: #fff;
    }
  }
  
  .image-icon {
    background-color: #409eff;
  }
  
  .task-icon {
    background-color: #67c23a;
  }
  
  .model-icon {
    background-color: #e6a23c;
  }
  
  .result-icon {
    background-color: #f56c6c;
  }
  
  .stat-info {
    margin-bottom: 20px;
  }
  
  .stat-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--el-text-color-primary);
    line-height: 1.2;
  }
  
  .stat-label {
    font-size: 16px;
    color: var(--el-text-color-secondary);
    margin-top: 8px;
  }
  
  .stat-chart {
    height: 6px;
    background-color: var(--el-fill-color-lighter);
    border-radius: 3px;
    overflow: hidden;
    
    .stat-progress {
      height: 100%;
      background-color: var(--el-color-primary);
      border-radius: 3px;
      transition: width 0.8s ease;
    }
  }
}

.accuracy-section {
  margin-bottom: 40px;
}

.chart-card {
  height: 100%;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0;
    }
  }
  
  .chart-container {
    height: 350px;
  }
}

.recent-tasks {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.workflow-section {
  margin-bottom: 40px;
}

.workflow-steps {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  
  @media (max-width: 992px) {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  @media (max-width: 576px) {
    flex-direction: column;
    align-items: center;
  }
}

.workflow-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 32px 24px;
  background-color: var(--el-bg-color);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }
  
  @media (max-width: 992px) {
    flex: 0 0 calc(50% - 12px);
  }
  
  @media (max-width: 576px) {
    width: 100%;
  }
  
  .step-number {
    position: absolute;
    top: -16px;
    left: 50%;
    transform: translateX(-50%);
    width: 32px;
    height: 32px;
    background-color: var(--el-color-primary);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 16px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .step-icon {
    font-size: 48px;
    color: var(--el-color-primary);
    margin-bottom: 20px;
  }
  
  .step-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 12px;
  }
  
  .step-desc {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
  }
}
</style>
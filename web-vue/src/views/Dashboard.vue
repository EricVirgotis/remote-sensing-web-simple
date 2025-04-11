<!-- 仪表盘页面 - 遥感影像智能分类分析系统首页 -->
<template>
  <div class="dashboard">
    <!-- 欢迎区域 - 使用更现代的设计 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用遥感智能分类分析系统</h1>
        <p class="welcome-subtitle">{{ currentDate }} · {{ greeting }}，{{ userInfo?.realName || userInfo?.username }}</p>
        <div class="welcome-description">
          <p>本系统提供遥感影像上传、智能分类分析、结果可视化展示等功能，帮助您快速完成遥感影像的分类分析任务。</p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="navigateTo('/image/upload')">
            <el-icon><Upload /></el-icon> 上传影像
          </el-button>
          <el-button type="success" size="large" @click="navigateTo('/classification')">
            <el-icon><DataAnalysis /></el-icon> 开始分析
          </el-button>
        </div>
      </div>
      <div class="welcome-image">
        <img src="@/assets/images/dashboard-welcome.svg" alt="Welcome" />
      </div>
    </div>

    <!-- 数据统计区 - 使用更美观的卡片设计 -->
    <div class="statistics-section">
      <h2 class="section-title">数据统计</h2>
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
              <div class="stat-progress" :style="{width: `${Math.min(stats.taskCount / 30 * 100, 100)}%`}"></div>
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
              <div class="stat-progress" :style="{width: `${Math.min(stats.modelCount / 10 * 100, 100)}%`}"></div>
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
              <div class="stat-progress" :style="{width: `${Math.min(stats.resultCount / 40 * 100, 100)}%`}"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速操作区 - 更现代的卡片设计 -->
    <div class="quick-actions-section">
      <h2 class="section-title">快速操作</h2>
      <div class="action-cards">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/image/upload')">
          <el-icon class="action-icon"><Upload /></el-icon>
          <div class="action-title">上传影像</div>
          <div class="action-desc">上传遥感影像文件</div>
          <div class="action-footer">
            <el-button text>立即上传 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </el-card>

        <el-card class="action-card" shadow="hover" @click="navigateTo('/classification')">
          <el-icon class="action-icon"><DataAnalysis /></el-icon>
          <div class="action-title">分类分析</div>
          <div class="action-desc">对影像进行智能分类</div>
          <div class="action-footer">
            <el-button text>开始分析 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </el-card>

        <el-card class="action-card" shadow="hover" @click="navigateTo('/train/dataset')">
          <el-icon class="action-icon"><Files /></el-icon>
          <div class="action-title">数据集管理</div>
          <div class="action-desc">管理训练数据集</div>
          <div class="action-footer">
            <el-button text>查看数据集 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </el-card>

        <el-card class="action-card" shadow="hover" @click="navigateTo('/result')">
          <el-icon class="action-icon"><PieChart /></el-icon>
          <div class="action-title">结果查看</div>
          <div class="action-desc">查看分析结果</div>
          <div class="action-footer">
            <el-button text>查看结果 <el-icon><ArrowRight /></el-icon></el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 最近任务区 - 更现代的表格设计 -->
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

    <!-- 系统概览区域 - 新增 -->
    <div class="system-overview">
      <h2 class="section-title">系统概览</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="overview-card">
            <template #header>
              <div class="card-header">
                <h3>分类精度统计</h3>
              </div>
            </template>
            <div class="chart-container" ref="accuracyChartRef"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="overview-card">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Upload, List, DataAnalysis, Picture, Monitor, PieChart, ArrowRight, Files } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 当前日期
const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

// 问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  return '晚上好'
})

// 加载状态
const loading = ref(false)

// 统计数据
const stats = ref({
  imageCount: 25,
  taskCount: 18,
  modelCount: 5,
  resultCount: 32
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

// 获取统计数据和最近任务
onMounted(() => {
  // 这里可以添加实际的API调用来获取数据
  // 目前使用模拟数据
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
  position: relative;
  padding-left: 12px;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 18px;
    background-color: var(--el-color-primary);
    border-radius: 2px;
  }
}

.welcome-section {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
  
  @media (max-width: 768px) {
    flex-direction: column;
    padding: 30px 20px;
  }
}

.welcome-content {
  flex: 1;
  z-index: 1;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-color-primary);
  margin-bottom: 12px;
}

.welcome-subtitle {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin-bottom: 20px;
}

.welcome-description {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 24px;
  max-width: 600px;
  line-height: 1.6;
}

.welcome-actions {
  display: flex;
  gap: 16px;
  
  @media (max-width: 576px) {
    flex-direction: column;
    gap: 12px;
  }
}

.welcome-image {
  flex: 0 0 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  @media (max-width: 768px) {
    margin-top: 30px;
    flex: 0 0 auto;
  }
}

.statistics-section {
  margin-bottom: 30px;
}

.stat-card {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  position: relative;
  padding: 20px;
  
  &:hover {
    transform: translateY(-5px);
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    
    .el-icon {
      font-size: 24px;
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
    margin-bottom: 16px;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--el-text-color-primary);
    line-height: 1.2;
  }
  
  .stat-label {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
  
  .stat-chart {
    height: 4px;
    background-color: var(--el-fill-color-lighter);
    border-radius: 2px;
    overflow: hidden;
    
    .stat-progress {
      height: 100%;
      background-color: var(--el-color-primary);
      border-radius: 2px;
      transition: width 0.8s ease;
    }
  }
}

.quick-actions-section {
  margin-bottom: 30px;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 576px) {
    grid-template-columns: 1fr;
  }
}

.action-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    
    .action-icon {
      transform: scale(1.1);
    }
  }
  
  .action-icon {
    font-size: 36px;
    color: var(--el-color-primary);
    margin-bottom: 16px;
    transition: transform 0.3s;
  }
  
  .action-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 8px;
  }
  
  .action-desc {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-bottom: 16px;
    flex-grow: 1;
  }
  
  .action-footer {
    margin-top: auto;
  }
}

.recent-tasks {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.system-overview {
  margin-bottom: 30px;
}

.overview-card {
  height: 100%;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin: 0;
    }
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>
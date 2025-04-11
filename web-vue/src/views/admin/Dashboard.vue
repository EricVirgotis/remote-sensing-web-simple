<!-- 管理控制台页面 -->
<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 系统概览卡片 -->
      <el-col :span="24">
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
              <el-button text @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <div class="data-card">
                <el-icon class="card-icon" :size="40"><User /></el-icon>
                <div class="card-content">
                  <div class="card-value">{{ statistics.userCount }}</div>
                  <div class="card-label">用户总数</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="data-card">
                <el-icon class="card-icon" :size="40"><Picture /></el-icon>
                <div class="card-content">
                  <div class="card-value">{{ statistics.imageCount }}</div>
                  <div class="card-label">影像总数</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="data-card">
                <el-icon class="card-icon" :size="40"><DataAnalysis /></el-icon>
                <div class="card-content">
                  <div class="card-value">{{ statistics.taskCount }}</div>
                  <div class="card-label">任务总数</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="data-card">
                <el-icon class="card-icon" :size="40"><Document /></el-icon>
                <div class="card-content">
                  <div class="card-value">{{ formatSize(statistics.storageUsage) }}</div>
                  <div class="card-label">存储用量</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- 系统管理功能卡片 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统管理</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-card class="function-card" shadow="hover" @click="navigateTo('/admin/users')">
                <el-icon class="function-icon"><UserFilled /></el-icon>
                <div class="function-title">用户管理</div>
                <div class="function-desc">管理系统用户信息和权限</div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-card class="function-card" shadow="hover" @click="navigateTo('/admin/files')">
                <el-icon class="function-icon"><Folder /></el-icon>
                <div class="function-title">成果文件管理</div>
                <div class="function-desc">管理系统生成的成果文件</div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-card class="function-card" shadow="hover" @click="navigateTo('/admin/settings')">
                <el-icon class="function-icon"><Setting /></el-icon>
                <div class="function-title">系统设置</div>
                <div class="function-desc">配置系统参数和运行环境</div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- 系统监控图表 -->
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户活跃度</span>
            </div>
          </template>
          <div id="userActivityChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务分布</span>
            </div>
          </template>
          <div id="taskDistributionChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { User, Picture, DataAnalysis, Document, UserFilled, Folder, Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 系统统计数据
const statistics = ref({
  userCount: 0,
  imageCount: 0,
  taskCount: 0,
  storageUsage: 0
})

// 图表实例
let userActivityChart: echarts.ECharts | null = null
let taskDistributionChart: echarts.ECharts | null = null

// 格式化存储大小
const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 刷新数据
const refreshData = async () => {
  try {
    // 模拟获取数据
    statistics.value = {
      userCount: Math.floor(Math.random() * 100) + 50,
      imageCount: Math.floor(Math.random() * 500) + 200,
      taskCount: Math.floor(Math.random() * 300) + 100,
      storageUsage: Math.floor(Math.random() * 1024 * 1024 * 1024 * 10)
    }
    
    // 刷新图表
    initCharts()
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新数据失败', error)
    ElMessage.error('刷新数据失败')
  }
}

// 初始化图表
const initCharts = () => {
  // 用户活跃度图表
  if (userActivityChart) {
    userActivityChart.dispose()
  }
  const userActivityDom = document.getElementById('userActivityChart')
  if (userActivityDom) {
    userActivityChart = echarts.init(userActivityDom)
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const data = days.map(() => Math.floor(Math.random() * 100))
    
    userActivityChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: days
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data,
        type: 'line',
        smooth: true,
        areaStyle: {}
      }]
    })
  }

  // 任务分布图表
  if (taskDistributionChart) {
    taskDistributionChart.dispose()
  }
  const taskDistributionDom = document.getElementById('taskDistributionChart')
  if (taskDistributionDom) {
    taskDistributionChart = echarts.init(taskDistributionDom)
    
    taskDistributionChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '任务类型',
        type: 'pie',
        radius: '70%',
        data: [
          { value: Math.floor(Math.random() * 100), name: '分类任务' },
          { value: Math.floor(Math.random() * 100), name: '训练任务' },
          { value: Math.floor(Math.random() * 100), name: '预测任务' },
          { value: Math.floor(Math.random() * 100), name: '其他任务' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

// 页面导航
const navigateTo = (path: string) => {
  router.push(path)
}

onMounted(() => {
  refreshData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (userActivityChart) {
    userActivityChart.dispose()
  }
  if (taskDistributionChart) {
    taskDistributionChart.dispose()
  }
})

// 处理窗口大小变化
const handleResize = () => {
  if (userActivityChart) {
    userActivityChart.resize()
  }
  if (taskDistributionChart) {
    taskDistributionChart.resize()
  }
}
</script>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  transition: all 0.3s;

  &:hover {
    background-color: #f5f7fa;
  }

  .card-icon {
    color: #409eff;
    margin-right: 15px;
  }

  .card-content {
    flex: 1;
  }

  .card-value {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    line-height: 1.2;
  }

  .card-label {
    font-size: 14px;
    color: #909399;
    margin-top: 5px;
  }
}

.function-card {
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
  }

  .function-icon {
    font-size: 40px;
    color: #409eff;
    margin-bottom: 10px;
  }

  .function-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 5px;
  }

  .function-desc {
    font-size: 12px;
    color: #909399;
    text-align: center;
  }
}

.chart {
  height: 300px;
}
</style>
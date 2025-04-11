<!-- 用户历史记录时间轴组件 -->
<template>
  <div class="history-timeline">
    <div class="timeline-header">
      <h3 class="timeline-title">历史操作记录</h3>
      <el-select v-model="filterType" placeholder="筛选类型" size="small" class="filter-select">
        <el-option label="全部" value="all" />
        <el-option label="影像上传" value="image_upload" />
        <el-option label="分类分析" value="classification" />
        <el-option label="模型训练" value="train" />
        <el-option label="个人信息" value="profile" />
      </el-select>
    </div>
    
    <el-timeline>
      <el-timeline-item
        v-for="(activity, index) in filteredActivities"
        :key="index"
        :type="getTimelineItemType(activity.type)"
        :color="getTimelineItemColor(activity.type)"
        :timestamp="activity.time"
        :hollow="activity.hollow"
      >
        <div class="timeline-content">
          <h4 class="timeline-item-title">{{ activity.title }}</h4>
          <p class="timeline-item-content">{{ activity.content }}</p>
          
          <div v-if="activity.link" class="timeline-item-link">
            <el-button link type="primary" size="small" @click="navigateTo(activity.link)">
              查看详情
            </el-button>
          </div>
        </div>
      </el-timeline-item>
      
      <el-timeline-item v-if="filteredActivities.length === 0">
        <div class="empty-timeline">
          <el-empty description="暂无历史记录" />
        </div>
      </el-timeline-item>
    </el-timeline>
    
    <div class="timeline-footer" v-if="hasMore">
      <el-button type="primary" link @click="loadMore">加载更多</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 活动类型
type ActivityType = 'image_upload' | 'classification' | 'train' | 'profile' | 'login' | 'other'

// 活动项接口
interface Activity {
  id: number
  title: string
  content: string
  type: ActivityType
  time: string
  link?: string
  hollow?: boolean
}

const router = useRouter()

// 筛选类型
const filterType = ref<string>('all')

// 活动列表
const activities = ref<Activity[]>([])

// 是否有更多数据
const hasMore = ref(true)

// 当前页码
const currentPage = ref(1)

// 每页条数
const pageSize = ref(10)

// 加载状态
const loading = ref(false)

// 根据类型筛选活动
const filteredActivities = computed(() => {
  if (filterType.value === 'all') {
    return activities.value
  }
  return activities.value.filter(activity => activity.type === filterType.value)
})

// 获取时间轴项类型
const getTimelineItemType = (type: ActivityType): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  switch (type) {
    case 'image_upload':
      return 'primary'
    case 'classification':
      return 'success'
    case 'train':
      return 'warning'
    case 'profile':
      return 'info'
    case 'login':
      return 'info'
    default:
      return 'info'
  }
}

// 获取时间轴项颜色
const getTimelineItemColor = (type: ActivityType): string => {
  switch (type) {
    case 'image_upload':
      return '#409EFF'
    case 'classification':
      return '#67C23A'
    case 'train':
      return '#E6A23C'
    case 'profile':
      return '#909399'
    case 'login':
      return '#909399'
    default:
      return '#909399'
  }
}

// 导航到指定链接
const navigateTo = (link: string) => {
  router.push(link)
}

// 加载更多数据
const loadMore = async () => {
  if (loading.value || !hasMore.value) return
  
  try {
    loading.value = true
    currentPage.value++
    await fetchUserActivities()
  } finally {
    loading.value = false
  }
}

// 获取用户活动记录
const fetchUserActivities = async () => {
  // 模拟API调用，实际项目中应该调用后端API
  // 这里使用模拟数据
  setTimeout(() => {
    // 模拟数据
    const mockData: Activity[] = [
      {
        id: 1,
        title: '上传遥感影像',
        content: '上传了一张新的遥感影像：forest_area_2023.tiff',
        type: 'image_upload',
        time: '2023-06-15 14:30:25',
        link: '/image/list'
      },
      {
        id: 2,
        title: '执行分类分析',
        content: '使用ResNet50模型对forest_area_2023.tiff进行了分类分析',
        type: 'classification',
        time: '2023-06-15 15:12:40',
        link: '/classification'
      },
      {
        id: 3,
        title: '查看分类结果',
        content: '查看了forest_area_2023.tiff的分类结果',
        type: 'classification',
        time: '2023-06-15 15:30:18',
        link: '/result/classification/1'
      },
      {
        id: 4,
        title: '修改个人信息',
        content: '更新了个人资料信息',
        type: 'profile',
        time: '2023-06-14 09:45:12'
      },
      {
        id: 5,
        title: '创建训练任务',
        content: '创建了一个新的模型训练任务：城市建筑识别模型',
        type: 'train',
        time: '2023-06-13 16:20:35',
        link: '/train/detail/1'
      },
      {
        id: 6,
        title: '上传数据集',
        content: '上传了城市建筑识别数据集',
        type: 'train',
        time: '2023-06-13 15:50:22',
        link: '/train/dataset'
      },
      {
        id: 7,
        title: '系统登录',
        content: '登录了遥感智能分类分析系统',
        type: 'login',
        time: '2023-06-13 09:10:05'
      }
    ]
    
    // 如果是第一页，直接赋值，否则追加
    if (currentPage.value === 1) {
      activities.value = mockData
    } else {
      // 模拟没有更多数据的情况
      if (currentPage.value > 2) {
        hasMore.value = false
      } else {
        // 生成一些额外的模拟数据
        const moreData = mockData.map((item, index) => ({
          ...item,
          id: item.id + activities.value.length,
          time: '2023-06-10 ' + (10 + index) + ':' + (20 + index) + ':00'
        }))
        activities.value = [...activities.value, ...moreData]
      }
    }
  }, 500)
}

// 组件挂载时获取数据
onMounted(() => {
  fetchUserActivities()
})
</script>

<style scoped>
.history-timeline {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.timeline-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.filter-select {
  width: 120px;
}

.timeline-content {
  padding: 10px 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  transition: all 0.3s;
}

.timeline-content:hover {
  background-color: #f0f9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timeline-item-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 8px 0;
}

.timeline-item-content {
  font-size: 14px;
  color: #606266;
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.timeline-item-link {
  text-align: right;
}

.timeline-footer {
  margin-top: 20px;
  text-align: center;
}

.empty-timeline {
  padding: 20px 0;
}
</style>
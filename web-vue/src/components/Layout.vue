<!-- 布局组件 -->
<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="aside">
      <!-- Logo -->
      <div class="logo" :class="{ 'logo-collapse': isCollapse }">
        <img src="../assets/images/logo.png" alt="Logo" class="logo-img" />
        <span v-if="!isCollapse" class="logo-text">遥感智能分类分析系统</span>
      </div>

      <!-- 菜单 -->
      <el-menu
        :default-active="router.currentRoute.value.path"
        :collapse="isCollapse"
        :router="false"
        class="el-menu-vertical"
        @select="handleMenuClick"
      >
        <template v-for="item in menuItems" :key="item.index">
          <!-- 子菜单 -->
          <el-sub-menu
            v-if="item.children"
            :index="item.index"
            popper-class="menu-popper"
          >
            <template #title>
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.title }}</span>
            </template>

            <el-menu-item
              v-for="child in item.children"
              :key="child.index"
              :index="child.index"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>

          <!-- 普通菜单项 -->
          <el-menu-item
            v-else
            :index="item.index"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 主体区域 -->
    <el-container class="main-container">
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <!-- 折叠按钮 -->
          <el-icon
            class="collapse-btn"
            @click="isCollapse = !isCollapse"
          >
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>

          <!-- 面包屑导航 -->
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ router.currentRoute.value.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 算法健康检查 -->
          <AlgoHealthCheck class="algo-health" />
          
          <!-- 用户菜单 -->
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar
                :size="32"
                :src="userStore.userInfo?.avatar || defaultAvatar"
              />
              <span class="username">{{ userStore.userInfo?.realName || userStore.userInfo?.username }}</span>
              <el-icon class="el-icon-arrow-down"><ArrowDown /></el-icon>
            </div>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import AlgoHealthCheck from './AlgoHealthCheck.vue'
import {
  House,
  Picture,
  DataAnalysis,
  Setting,
  User,
  SwitchButton,
  ArrowDown,
  Monitor,
  Files,
  Histogram,
  Document,
  UserFilled
} from '@element-plus/icons-vue'

interface MenuItem {
  index: string
  title: string
  icon: string
  children?: {
    index: string
    title: string
  }[]
}

const router = useRouter()
const userStore = useUserStore()

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 菜单是否折叠
const isCollapse = ref(false)

// 菜单项配置
const menuItems = computed<MenuItem[]>(() => {
  const items: MenuItem[] = [
    {
      index: '/home',
      title: '首页',
      icon: 'House'
    },
    {
      index: '/dashboard',
      title: '仪表盘',
      icon: 'Monitor'
    },
    {
      index: '/image',
      title: '遥感影像',
      icon: 'Picture',
      children: [
        {
          title: '影像列表',
          index: '/image/list'
        },
        {
          title: '上传影像',
          index: '/image/upload'
        }
      ]
    },
    {
      index: '/classification',
      title: '分类分析',
      icon: 'DataAnalysis'
    },
    {
      title: '模型训练',
      index: '/train',
      icon: 'Monitor',
      children: [
        {
          title: '数据集管理',
          index: '/train/dataset'
        },
        {
          title: '训练任务',
          index: '/train/list'
        }
      ]
    },
    {
      title: '任务管理',
      index: '/task',
      icon: 'Files',
      children: [
        {
          title: '任务列表',
          index: '/task/list'
        },
        {
          title: '创建任务',
          index: '/task/create'
        }
      ]
    },
    {
      icon: 'Histogram',
      title: '结果分析',
      index: '/result'
    }
  ]

  // 管理员菜单
  if (userStore.isAdmin()) {
    items.push({
      index: '/admin',
      title: '系统管理',
      icon: 'Setting',
      children: [
        // {
        //   index: '/admin/dashboard',
        //   title: '管理控制台'
        // },
        {
          index: '/admin/users',
          title: '用户管理'
        }
      ]
    })
  }

  return items
})

// 处理菜单点击
const handleMenuClick = (index: string) => {
  router.push(index)
}

// 处理用户菜单点击
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100%;
  width: 100%;
}

.aside {
  background-color: #001529;
  height: 100vh;
  transition: width 0.3s;
  overflow-x: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #001529;
  overflow: hidden;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-img {
  width: 32px;
  height: 32px;
  transition: all 0.3s;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  margin-left: 12px;
  transition: all 0.3s;
}

.logo-collapse {
  justify-content: center;
  padding: 0 16px;
  
  .logo-img {
    margin-right: 0;
  }
  
  .logo-text {
    opacity: 0;
    display: none;
  }
}

.el-menu-vertical {
  border-right: none;
  background-color: #001529;
  transition: all 0.3s;
  
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    color: rgba(255, 255, 255, 0.65);
    height: 50px;
    line-height: 50px;
    
    &:hover {
      color: #fff;
      background-color: #002140;
    }
    
    &.is-active {
      color: #fff;
      background-color: #1890ff;
    }
  }
  
  :deep(.el-sub-menu.is-active .el-sub-menu__title) {
    color: #fff;
  }
}

.main-container {
  background-color: #f0f2f5;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  position: relative;
  z-index: 9;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
  
  &:hover {
    color: var(--el-color-primary);
    transform: scale(1.1);
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.algo-health {
  margin-right: 20px;
}

.user-dropdown {
  cursor: pointer;
  transition: all 0.3s;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.025);
  }
}

.username {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
}

.main {
  padding: 24px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
  flex: 1;
  
  // 添加滚动条样式
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #d9d9d9;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f5f7fa;
  }
}

:deep(.menu-popper) {
  background-color: #001529 !important;
  border: none !important;
  
  .el-menu {
    background-color: #001529 !important;
  }
  
  .el-menu-item {
    color: rgba(255, 255, 255, 0.65) !important;
    height: 40px !important;
    line-height: 40px !important;
    padding-left: 48px !important;
    
    &:hover {
      color: #fff !important;
      background-color: #002140 !important;
    }
    
    &.is-active {
      color: #fff !important;
      background-color: #1890ff !important;
    }
  }

  .el-sub-menu__title {
    color: rgba(255, 255, 255, 0.65) !important;
    
    &:hover {
      color: #fff !important;
      background-color: #002140 !important;
    }
  }
}

:deep(.el-menu--popup) {
  background-color: #000c17 !important;
  padding: 0 !important;
  min-width: 180px !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

:deep(.el-sub-menu__title) {
  &:hover {
    background-color: #002140 !important;
  }
}

:deep(.el-menu--inline) {
  background-color: #000c17 !important;
  
  .el-menu-item {
    padding-left: 48px !important;
    background-color: #000c17 !important;
    
    &:hover {
      background-color: #002140 !important;
    }
    
    &.is-active {
      background-color: #1890ff !important;
    }
  }
}
</style>
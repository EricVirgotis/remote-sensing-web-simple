import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Layout from '@/components/Layout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: {
          title: '首页',
          requiresAuth: true
        }
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/user',
    component: Layout,
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人中心',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/admin',
    component: Layout,
    meta: {
      requiresAuth: true,
      requiresAdmin: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: '管理控制台',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: {
          title: '用户管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'files',
        name: 'FileManagement',
        component: () => import('@/views/admin/FileManagement.vue'),
        meta: {
          title: '成果文件管理',
          requiresAuth: true,
          requiresAdmin: true
        }
      },
      {
        path: 'settings',
        name: 'SystemSettings',
        component: () => import('@/views/admin/SystemSettings.vue'),
        meta: {
          title: '系统设置',
          requiresAuth: true,
          requiresAdmin: true
        }
      }
    ]
  },
  {
    path: '/train',
    component: Layout,
    children: [
      {
        path: 'dataset',
        name: 'Dataset',
        component: () => import('@/views/train/DatasetList.vue'),
        meta: { title: '数据集管理' }
      },
      {
        path: 'list',
        name: 'TrainTaskList',
        component: () => import('@/views/train/TrainTaskList.vue'),
        meta: { title: '训练任务列表' }
      },
      {
        path: 'detail/:id',
        name: 'TrainTaskDetail',
        component: () => import('@/views/train/TrainTaskDetail.vue'),
        meta: { title: '训练任务详情' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/user/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/user/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false
    }
  },
  {
    path: '/result',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Result',
        component: () => import('@/views/result/ResultView.vue'),
        meta: { title: '结果查看' }
      },
      {
        path: 'classification/:id',
        name: 'ClassificationResult',
        component: () => import('@/views/result/ClassificationResult.vue'),
        meta: { title: '分类结果详情' }
      }
    ]
  },
  {
    path: '/classification',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Classification',
        component: () => import('@/views/classification/index.vue'),
        meta: {
          title: '图像分类',
          icon: 'Picture',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/task',
    component: Layout,
    children: [
      {
        path: 'list',
        name: 'TaskList',
        component: () => import('@/views/task/TaskList.vue'),
        meta: {
          title: '任务列表',
          requiresAuth: true
        }
      },
      {
        path: 'create',
        name: 'TaskCreate',
        component: () => import('@/views/task/TaskCreate.vue'),
        meta: {
          title: '创建任务',
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/image',
    component: Layout,
    children: [
      {
        path: 'upload',
        name: 'ImageUpload',
        component: () => import('@/views/image/ImageUpload.vue'),
        meta: {
          title: '图片上传',
          requiresAuth: true
        }
      },
      {
        path: 'list',
        name: 'ImageList',
        component: () => import('@/views/image/ImageList.vue'),
        meta: {
          title: '图片列表',
          requiresAuth: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)

  // 设置页面标题
  document.title = `${to.meta.title} - 遥感图像分析平台`

  if (requiresAuth) {
    if (!userStore.isLoggedIn()) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    if (requiresAdmin && !userStore.isAdmin()) {
      next({ name: 'Dashboard' })
      return
    }
  }

  next()
})

export default router
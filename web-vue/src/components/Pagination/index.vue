<script setup lang="ts">
import { computed } from 'vue'
import { ElPagination } from 'element-plus'

interface Props {
  current: number
  size: number
  total: number
}

const props = withDefaults(defineProps<Props>(), {
  current: 1,
  size: 10,
  total: 0
})

const emit = defineEmits(['update:current', 'update:size', 'change'])

// 当前页
const currentPage = computed({
  get: () => props.current,
  set: (val: number) => {
    emit('update:current', val)
    emit('change')
  }
})

// 每页条数
const pageSize = computed({
  get: () => props.size,
  set: (val: number) => {
    emit('update:size', val)
    emit('change')
  }
})
</script>

<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      background
    />
  </div>
</template>

<style lang="scss" scoped>
.pagination-container {
  padding: 16px;
  text-align: right;
}
</style>
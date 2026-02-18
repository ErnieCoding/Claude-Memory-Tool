<template>
  <div v-if="files.length > 0 && !isProcessing" class="created-files-panel">
    <div class="panel-header">
      <h2>📄 Созданные файлы</h2>
      <span class="file-count">{{ files.length }}</span>
    </div>

    <div class="file-list">
      <div
        v-for="file in files"
        :key="file.path"
        @click="$emit('load-file', file.path)"
        class="file-item">
        <span class="file-icon">📁</span>
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreatedFiles',
  props: {
    files: {
      type: Array,
      default: () => []
    },
    isProcessing: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
  }
};
</script>

<style scoped>
.created-files-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  width: 320px;
  flex-shrink: 0;
  align-self: flex-start;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #0ea5e9;
}

h2 {
  font-size: 18px;
  font-weight: 600;
  color: #0c4a6e;
  margin: 0;
}

.file-count {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-color: #0ea5e9;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #0c4a6e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: #64748b;
}

/* Стилизация скроллбара */
.file-list::-webkit-scrollbar {
  width: 6px;
}

.file-list::-webkit-scrollbar-track {
  background: #f0f9ff;
  border-radius: 3px;
}

.file-list::-webkit-scrollbar-thumb {
  background: #bae6fd;
  border-radius: 3px;
}

.file-list::-webkit-scrollbar-thumb:hover {
  background: #0ea5e9;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .created-files-panel {
    width: 100%;
  }

  .file-list {
    max-height: 400px;
  }
}
</style>

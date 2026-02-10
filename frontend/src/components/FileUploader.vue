<template>
  <div class="file-uploader">
    <div class="upload-section">
      <h2>Загрузка файлов</h2>

      <div class="upload-area"
           :class="{ 'drag-over': isDragOver }"
           @drop.prevent="handleDrop"
           @dragover.prevent="isDragOver = true"
           @dragleave.prevent="isDragOver = false"
           @click="triggerFileInput">
        <div class="upload-icon">📁</div>
        <p class="upload-text">
          Перетащите файлы сюда или кликните для выбора
        </p>
        <p class="upload-hint">
          Поддерживаемые форматы: JSON, TXT, XML, PDF, CSV, XLSX
        </p>
        <input
          ref="fileInput"
          type="file"
          multiple
          @change="handleFileSelect"
          accept=".json,.txt,.xml,.pdf,.csv,.xlsx,.xls"
          style="display: none;">
      </div>

      <div v-if="uploadProgress > 0 && uploadProgress < 100" class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        <span class="progress-text">{{ uploadProgress }}%</span>
      </div>

      <div v-if="uploadedFiles.length > 0" class="uploaded-files">
        <h3>Загруженные файлы ({{ uploadedFiles.length }})</h3>
        <div class="file-list">
          <div v-for="file in uploadedFiles" :key="file.path" class="file-item">
            <div class="file-info">
              <span class="file-icon">{{ getFileIcon(file.extension) }}</span>
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
            </div>
            <button @click="deleteFile(file.path)" class="delete-btn">✕</button>
          </div>
        </div>
        <button @click="clearAllFiles" class="clear-btn">Очистить все</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'FileUploader',
  data() {
    return {
      isDragOver: false,
      uploadProgress: 0,
      uploadedFiles: []
    };
  },
  mounted() {
    this.loadFiles();
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const files = Array.from(event.target.files);
      this.uploadFiles(files);
    },
    handleDrop(event) {
      this.isDragOver = false;
      const files = Array.from(event.dataTransfer.files);
      this.uploadFiles(files);
    },
    async uploadFiles(files) {
      if (files.length === 0) return;

      try {
        this.uploadProgress = 0;
        const result = await api.uploadFiles(files, (progress) => {
          this.uploadProgress = progress;
        });

        this.$emit('filesUploaded', result.files);
        this.uploadProgress = 100;

        setTimeout(() => {
          this.uploadProgress = 0;
          this.loadFiles();
        }, 1000);

      } catch (error) {
        console.error('Upload error:', error);
        alert('Ошибка загрузки: ' + (error.response?.data?.error || error.message));
        this.uploadProgress = 0;
      }
    },
    async loadFiles() {
      try {
        const result = await api.listFiles();
        this.uploadedFiles = result.files;
      } catch (error) {
        console.error('Load files error:', error);
      }
    },
    async deleteFile(filepath) {
      if (!confirm('Удалить файл?')) return;

      try {
        await api.deleteFile(filepath);
        this.loadFiles();
      } catch (error) {
        console.error('Delete error:', error);
        alert('Ошибка удаления: ' + (error.response?.data?.error || error.message));
      }
    },
    async clearAllFiles() {
      if (!confirm('Удалить все файлы?')) return;

      try {
        await api.clearAllFiles();
        this.loadFiles();
      } catch (error) {
        console.error('Clear error:', error);
        alert('Ошибка очистки: ' + (error.response?.data?.error || error.message));
      }
    },
    getFileIcon(extension) {
      const icons = {
        '.json': '📄',
        '.txt': '📝',
        '.xml': '📋',
        '.pdf': '📕',
        '.csv': '📊',
        '.xlsx': '📈',
        '.xls': '📈'
      };
      return icons[extension] || '📄';
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
  }
};
</script>

<style scoped>
.file-uploader {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #1d1d1f;
}

.upload-area {
  border: 2px dashed #d2d2d7;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #0071e3;
  background: #f5f5f7;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: #86868b;
}

.progress-bar {
  margin-top: 20px;
  height: 8px;
  background: #e5e5e7;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #0071e3;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: -20px;
  right: 0;
  font-size: 12px;
  color: #86868b;
}

.uploaded-files {
  margin-top: 24px;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1d1d1f;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f5f5f7;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background 0.2s ease;
}

.file-item:hover {
  background: #e8e8ed;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-size: 14px;
  color: #1d1d1f;
  flex: 1;
}

.file-size {
  font-size: 12px;
  color: #86868b;
}

.delete-btn {
  background: none;
  border: none;
  color: #86868b;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s ease;
}

.delete-btn:hover {
  color: #ff3b30;
}

.clear-btn {
  margin-top: 12px;
  width: 100%;
  padding: 12px;
  background: #ff3b30;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.clear-btn:hover {
  opacity: 0.8;
}
</style>

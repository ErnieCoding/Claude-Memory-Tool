<template>
  <div class="response-viewer">
    <div class="header">
      <h2>Ответ</h2>
      <div class="header-actions" v-if="response">
        <button @click="copyResponse" class="icon-btn" title="Копировать">
          📋
        </button>
        <button @click="clearResponse" class="icon-btn" title="Очистить">
          🗑️
        </button>
      </div>
    </div>

    <div class="response-content" v-if="response || isProcessing">
      <!-- Статус обработки -->
      <div v-if="isProcessing && !response" class="processing-indicator">
        <div class="spinner"></div>
        <span>{{ processingStatus }}</span>
      </div>

      <!-- Конечный ответ -->
      <div v-if="response" class="final-response">
        <pre>{{ response }}</pre>

        <div v-if="usage" class="usage-info">
          <span>Токены: {{ usage.input_tokens }} вход / {{ usage.output_tokens }} выход</span>
        </div>
      </div>

      <!-- Ошибка -->
      <div v-if="error" class="error-message">
        <span class="error-icon">⚠️</span>
        <span>{{ error }}</span>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="empty-icon">💭</div>
      <p>Здесь появится ответ от Claude</p>
    </div>

    <!-- История ответов -->
    <div v-if="savedResponses.length > 0" class="saved-responses">
      <h3>Сохраненные ответы</h3>
      <div class="response-list">
        <div
          v-for="resp in savedResponses"
          :key="resp.path"
          @click="loadResponse(resp.path)"
          class="response-item">
          <span class="response-name">{{ resp.name }}</span>
          <span class="response-date">{{ formatDate(resp.modified) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'ResponseViewer',
  props: {
    response: String,
    isProcessing: Boolean,
    processingStatus: String,
    error: String,
    usage: Object
  },
  data() {
    return {
      savedResponses: []
    };
  },
  mounted() {
    this.loadSavedResponses();
  },
  methods: {
    async loadSavedResponses() {
      try {
        const result = await api.listResponses();
        this.savedResponses = result.responses;
      } catch (error) {
        console.error('Load responses error:', error);
      }
    },
    async loadResponse(filepath) {
      try {
        const result = await api.getResponse(filepath);
        this.$emit('load-response', result.content);
      } catch (error) {
        console.error('Load response error:', error);
        alert('Ошибка загрузки: ' + (error.response?.data?.error || error.message));
      }
    },
    copyResponse() {
      if (this.response) {
        navigator.clipboard.writeText(this.response).then(() => {
          alert('Скопировано в буфер обмена');
        });
      }
    },
    clearResponse() {
      this.$emit('clear-response');
    },
    formatDate(timestamp) {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString('ru-RU');
    }
  },
  watch: {
    response() {
      this.loadSavedResponses();
    }
  }
};
</script>

<style scoped>
.response-viewer {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: #f5f5f7;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.icon-btn:hover {
  background: #e8e8ed;
}

.response-content {
  min-height: 200px;
}

.processing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f5f7;
  border-radius: 8px;
  font-size: 14px;
  color: #1d1d1f;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #d2d2d7;
  border-top-color: #0071e3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.streaming-text,
.final-response {
  position: relative;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 15px;
  line-height: 1.6;
  color: #1d1d1f;
  margin: 0;
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 20px;
  background: #0071e3;
  animation: blink 1s infinite;
  vertical-align: middle;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.usage-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #d2d2d7;
  font-size: 13px;
  color: #86868b;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff3f3;
  border: 1px solid #ffcccc;
  border-radius: 8px;
  color: #ff3b30;
  font-size: 14px;
  margin-top: 16px;
}

.error-icon {
  font-size: 24px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #86868b;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.saved-responses {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #d2d2d7;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1d1d1f;
}

.response-list {
  max-height: 200px;
  overflow-y: auto;
}

.response-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f5f5f7;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.response-item:hover {
  background: #e8e8ed;
}

.response-name {
  font-size: 14px;
  color: #1d1d1f;
}

.response-date {
  font-size: 12px;
  color: #86868b;
}
</style>

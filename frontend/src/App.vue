<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <h1>Claude Memory Tool</h1>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <div class="grid">
          <!-- Загрузка файлов -->
          <div class="grid-item">
            <FileUploader @filesUploaded="handleFilesUploaded" />
          </div>

          <!-- Запрос и ответ -->
          <div class="grid-item">
            <QueryInput
              :isProcessing="isProcessing"
              @send-query="handleSendQuery"
              @stop-processing="handleStopProcessing"
            />

            <div class="spacer"></div>

            <ResponseViewer
              :response="response"
              :isProcessing="isProcessing"
              :processingStatus="processingStatus"
              :error="error"
              :usage="usage"
              @clear-response="clearResponse"
              @load-response="loadResponse"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import FileUploader from './components/FileUploader.vue';
import QueryInput from './components/QueryInput.vue';
import ResponseViewer from './components/ResponseViewer.vue';
import api from './services/api';

export default {
  name: 'App',
  components: {
    FileUploader,
    QueryInput,
    ResponseViewer
  },
  data() {
    return {
      isProcessing: false,
      processingStatus: 'Генерация ответа...',
      response: '',
      error: '',
      usage: null
    };
  },
  methods: {
    handleFilesUploaded(files) {
      console.log('Files uploaded:', files);
    },

    async handleSendQuery(query) {
      this.isProcessing = true;
      this.response = '';
      this.error = '';
      this.usage = null;
      this.processingStatus = 'Генерация ответа...';

      try {
        // Используем обычный POST запрос (без streaming)
        const result = await api.sendQuery(query);

        // Устанавливаем результат
        this.response = result.response;
        this.usage = result.usage;

      } catch (error) {
        this.error = 'Ошибка: ' + (error.response?.data?.error || error.message);
        console.error('Query error:', error);
      } finally {
        this.isProcessing = false;
      }
    },

    handleStopProcessing() {
      // В синхронном режиме нельзя отменить запрос
      // Можно добавить поддержку отмены через AbortController если нужно
      this.isProcessing = false;
    },

    clearResponse() {
      this.response = '';
      this.error = '';
      this.usage = null;
    },

    loadResponse(content) {
      this.response = content;
      this.error = '';
    }
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f7;
  color: #1d1d1f;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px 0;
  color: white;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  padding: 32px 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.spacer {
  height: 0;
}

.app-footer {
  background: white;
  padding: 24px 0;
  text-align: center;
  color: #86868b;
  font-size: 13px;
  border-top: 1px solid #d2d2d7;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f5f5f7;
}

::-webkit-scrollbar-thumb {
  background: #d2d2d7;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #86868b;
}
</style>

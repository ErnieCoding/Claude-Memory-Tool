<template>
  <div class="query-input">
    <h2>Запрос к файлам</h2>

    <div class="input-container">
      <textarea
        v-model="query"
        placeholder="Введите ваш запрос... Например: 'Проанализируй загруженные файлы и создай краткое резюме'"
        :disabled="isProcessing"
        @keydown.ctrl.enter="sendQuery"
      ></textarea>

      <div class="actions">
        <button
          @click="sendQuery"
          :disabled="!query.trim() || isProcessing"
          class="send-btn">
          {{ isProcessing ? 'Обработка...' : 'Отправить' }}
        </button>

        <button
          v-if="isProcessing"
          @click="stopProcessing"
          class="stop-btn">
          Остановить
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QueryInput',
  props: {
    isProcessing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      query: '',
      examples: [
        'Проанализируй все загруженные файлы и создай краткое резюме',
        'Найди ключевые данные в CSV файлах',
        'Сравни содержимое JSON файлов',
        'Извлеки основные выводы из документов'
      ]
    };
  },
  methods: {
    sendQuery() {
      if (!this.query.trim() || this.isProcessing) return;

      this.$emit('send-query', this.query);
    },
    stopProcessing() {
      this.$emit('stop-processing');
    }
  }
};
</script>

<style scoped>
.query-input {
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

textarea {
  width: 100%;
  min-height: 120px;
  padding: 16px;
  border: 2px solid #d2d2d7;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s ease;
}

textarea:focus {
  outline: none;
  border-color: #0071e3;
}

textarea:disabled {
  background: #f5f5f7;
  color: #86868b;
  cursor: not-allowed;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.send-btn,
.stop-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.send-btn {
  background: #0071e3;
  color: white;
  flex: 1;
}

.send-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.send-btn:disabled {
  background: #d2d2d7;
  cursor: not-allowed;
}

.stop-btn {
  background: #ff3b30;
  color: white;
}

.stop-btn:hover {
  opacity: 0.8;
}

.examples {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #d2d2d7;
}

.examples-title {
  font-size: 13px;
  color: #86868b;
  margin-bottom: 12px;
}

.example-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-chip {
  padding: 8px 16px;
  background: #f5f5f7;
  border: 1px solid #d2d2d7;
  border-radius: 20px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-chip:hover {
  background: #e8e8ed;
  border-color: #0071e3;
}
</style>

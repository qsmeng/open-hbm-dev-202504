<template>
  <div class="game-view">
    <Header />
    <div class="game-status-bar">
      <div class="status-item">
        <span class="label">轮次:</span>
        <span class="value">{{ turnCount }}</span>
      </div>
      <div class="status-item">
        <span class="label">稳定度:</span>
        <span class="value">{{ stability }}%</span>
      </div>
      <div class="status-item">
        <span class="label">体力:</span>
        <div class="energy-container">
          <div class="energy-bar" :style="{ width: energy + '%' }"></div>
          <span class="energy-value">{{ energy }}/100</span>
        </div>
      </div>
    </div>
    <div class="game-container">
      <!-- Main game area -->
      <div class="game-main">
        <h1>游戏页面</h1>
        <div class="chat-area">
          <div class="messages" ref="messagesContainer">
            <div v-for="(message, index) in messages" :key="index" 
                 :class="['message', message.sender === 'user' ? 'user-message' : 'bot-message']">
              <div class="message-content">
                <span class="message-text">{{ message.text }}</span>
                <span class="message-timestamp">{{ formatTimestamp(message.timestamp) }}</span>
              </div>
            </div>
            <div v-if="aiOptions.length > 0" class="ai-options-container">
              <div v-for="(option, index) in aiOptions" :key="'ai-'+index"
                   class="ai-option" @click="selectAiOption(option)">
                {{ option }}
              </div>
            </div>
          </div>
          <div class="message-input">
            <input v-model="inputMessage" @keyup.enter="sendMessage" 
                   placeholder="输入消息..." class="input-field" />
            <button @click="sendMessage" class="send-button">发送</button>
          </div>
        </div>
      </div>
      
      <!-- Side panels -->
      <div class="side-panel">
        <!-- Treasure display section -->
        <div class="treasure-area">
          <div class="treasure-image-container" @click="rotateTreasure">
            <img :src="currentTreasure.image" alt="宝物" class="treasure-image" 
                 :style="{ transform: `rotateY(${rotationAngle}deg)` }">
          </div>
          
          <div class="treasure-details">
            <h3 v-if="currentTreasure.identified">{{ currentTreasure.name }}</h3>
            <h3 v-else>未鉴定的宝物</h3>
            
            <div v-if="currentTreasure.identified" class="treasure-properties">
              <div class="property">
                <span class="label">强度:</span>
                <span class="value">{{ currentTreasure.strength }}</span>
              </div>
              <div class="property">
                <span class="label">效果:</span>
                <span class="value">{{ currentTreasure.effect }}</span>
              </div>
            </div>
            <div v-else class="unidentified-prompt">
              <button @click="identifyTreasure" class="identify-button">鉴定宝物</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <router-link to="/" class="back-button">返回首页</router-link>
    <Footer />
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const messages = ref([])
const inputMessage = ref('')
const messagesContainer = ref(null)
const aiOptions = ref([])
const rotationAngle = ref(0)
const isRotating = ref(false)

// 游戏状态
const turnCount = ref(1)
const stability = ref(85)
const energy = ref(80)
const energyTimer = ref(null)

// 宝物数据
const currentTreasure = ref({
  name: '神秘宝物',
  strength: 0,
  effect: '',
  image: '/src/assets/images/background.png',
  identified: false
})

// 初始化体力恢复计时器
const startEnergyRecovery = () => {
  energyTimer.value = setInterval(() => {
    if (energy.value < 100) {
      energy.value = Math.min(energy.value + 5, 100)
    }
  }, 30000) // 每30秒恢复5点体力
}

// 模拟宝物数据
const treasures = [
  {
    name: '空间加固卡',
    strength: 128,
    effect: '延长当前事件空间的存在时间',
    image: '/src/assets/images/treasure1.png'
  },
  {
    name: '空间震荡卡',
    strength: 85,
    effect: '有一定概率将当前个人探索空间转为事件空间',
    image: '/src/assets/images/treasure2.png'
  },
  {
    name: '复制品',
    strength: 64,
    effect: '强度削弱的复刻宝物',
    image: '/src/assets/images/treasure3.png'
  }
]

const setDefaultImage = (e) => {
  e.target.src = '/src/assets/images/background.png'
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 旋转宝物
const rotateTreasure = () => {
  if (isRotating.value) return
  isRotating.value = true
  rotationAngle.value += 180
  setTimeout(() => {
    isRotating.value = false
  }, 500)
}

// 鉴定宝物
const identifyTreasure = () => {
  if (currentTreasure.value.identified) return
  
  // 模拟鉴定过程
  setTimeout(() => {
    const randomTreasure = treasures[Math.floor(Math.random() * treasures.length)]
    currentTreasure.value = {
      ...randomTreasure,
      identified: true
    }
  }, 1000)
}

const sendMessage = async () => {
  if (inputMessage.value.trim() === '') return;

  // 添加用户消息
  messages.value.push({ 
    sender: 'user', 
    text: inputMessage.value,
    timestamp: Date.now()
  });
  scrollToBottom()

  // 调用后台接口
  try {
    const response = await axios.post('/api/ollamaByLangchain', { message: inputMessage.value });
    messages.value.push({ 
      sender: 'bot', 
      text: response.data.response,
      timestamp: Date.now()
    });
    
    // 模拟AI备选回复
    aiOptions.value = [
      '这是一个备选回复1',
      '这是另一个备选回复2',
      '这是第三个备选回复3'
    ]
    
    // 模拟获取新宝物
    if (Math.random() > 0.7) {
      currentTreasure.value = {
        name: '神秘宝物',
        strength: 0,
        effect: '',
        image: '/src/assets/images/background.png',
        identified: false
      }
    }
    
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ 
      sender: 'bot', 
      text: '抱歉，暂时无法处理您的请求。',
      timestamp: Date.now()
    });
  }

  scrollToBottom()
  inputMessage.value = '';
};

const selectAiOption = (option) => {
  inputMessage.value = option
  aiOptions.value = []
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.game-view {
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  min-height: 100vh;
  gap: 1rem;
}

.game-status-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label {
  font-weight: bold;
  color: #64748b;
}

.value {
  font-weight: 600;
  color: #334155;
}

.energy-container {
  position: relative;
  width: 100px;
  height: 20px;
  background-color: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.energy-bar {
  position: absolute;
  height: 100%;
  background-color: #10b981;
  transition: width 0.3s ease;
}

.energy-value {
  position: absolute;
  width: 100%;
  text-align: center;
  font-size: 0.75rem;
  color: white;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.game-container {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  height: calc(100vh - 120px);
}

.game-main {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f8fafc;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease-out;
}

.message-content {
  display: inline-block;
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  position: relative;
}

.user-message .message-content {
  background-color: #3b82f6;
  color: white;
  margin-left: auto;
}

.bot-message .message-content {
  background-color: #e2e8f0;
  color: #334155;
}

.message-timestamp {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.user-message .message-timestamp {
  text-align: right;
}

.bot-message .message-timestamp {
  text-align: left;
}

.ai-options-container {
  margin-top: 1rem;
  border-top: 1px dashed #e2e8f0;
  padding-top: 1rem;
}

.ai-option {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-option:hover {
  background-color: #f1f5f9;
  transform: translateY(-2px);
}

.message-input {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: white;
}

.input-field {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  outline: none;
  transition: border-color 0.2s;
}

.input-field:focus {
  border-color: #3b82f6;
}

.send-button {
  padding: 0 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover {
  background-color: #2563eb;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.treasure-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
}

.treasure-image-container {
  perspective: 1000px;
  cursor: pointer;
  margin: 0 auto;
  width: 200px;
  height: 200px;
}

.treasure-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.5s ease;
  backface-visibility: hidden;
}

.treasure-details {
  padding: 1rem;
  text-align: center;
}

.treasure-properties {
  margin-top: 1rem;
  text-align: left;
}

.property {
  display: flex;
  margin-bottom: 0.5rem;
}

.label {
  font-weight: bold;
  min-width: 60px;
  color: #64748b;
}

.value {
  flex: 1;
  color: #334155;
}

.unidentified-prompt {
  margin-top: 1rem;
}

.identify-button {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.identify-button:hover {
  background-color: #2563eb;
}

.identify-button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

/* Existing styles... */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.back-button {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: #2563eb;
}

@media (max-width: 768px) {
  .game-container {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .side-panel {
    flex-direction: row;
  }
  
  .message-content {
    max-width: 90%;
  }
  
  .treasure-image-container {
    width: 150px;
    height: 150px;
  }
}
</style>
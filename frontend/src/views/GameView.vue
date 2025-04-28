<template>
  <div class="forum-layout">
    <Header />
    
    <!-- 主内容区 -->
    <div class="main-content">
      <div class="world-map">
        <div v-if="loadingWorld" class="loading">加载中...</div>
        <div v-else class="world-posts">
          <div v-for="post in worldPosts" :key="post.id" class="post">
            <h3>{{ post.title }}</h3>
            <div class="post-content" v-html="post.content"></div>
            <div class="post-meta">
              <span>作者: {{ post.author }}</span>
              <span>时间: {{ formatPostTime(post.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="story-content">
        <h2>故事背景</h2>
        <p>{{ currentStory }}</p>
      </div>
    </div>
    
    <!-- 可折叠侧边栏 -->
    <div class="sidebar" :class="{collapsed: isSidebarCollapsed}">
      <button class="toggle-sidebar" @click="toggleSidebar">
        {{ isSidebarCollapsed ? '>' : '<' }}
      </button>
      <div class="treasure-area" v-show="!isSidebarCollapsed">
        <div class="treasure-image-container" @click="rotateTreasure">
          <img :src="currentTreasure.image" alt="宝物" 
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
    
    <!-- 底部输入区 -->
    <div class="input-area">
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
    
    <!-- 悬浮面板 -->
    <div class="floating-panel" v-if="showFloatingPanel" 
         :style="{ left: panelPosition.x + 'px', top: panelPosition.y + 'px' }">
      <div class="panel-header" @mousedown="startDrag">
        <span>游戏状态</span>
        <button @click="togglePanel">×</button>
      </div>
      <div class="panel-content">
        <div class="status-item">
          <span>轮次: {{ turnCount }}</span>
        </div>
        <div class="status-item">
          <span>稳定度: {{ stability }}%</span>
        </div>
        <div class="status-item">
          <span>体力: {{ energy }}/100</span>
        </div>
      </div>
    </div>
    
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

// 世界帖子数据
const worldPosts = ref([])
const loadingWorld = ref(false)

// 获取世界帖子
const fetchWorldPosts = async () => {
  loadingWorld.value = true
  try {
    const response = await axios.get('/api/world/posts')
    worldPosts.value = response.data.posts
  } catch (error) {
    console.error('获取世界帖子失败:', error)
  } finally {
    loadingWorld.value = false
  }
}

const formatPostTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// UI状态
const isSidebarCollapsed = ref(false)
const showFloatingPanel = ref(true)
const panelPosition = ref({ x: 20, y: 20 })
const isDragging = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const togglePanel = () => {
  showFloatingPanel.value = !showFloatingPanel.value
}

const startDrag = (e) => {
  isDragging.value = true
  const startX = e.clientX
  const startY = e.clientY
  const startLeft = panelPosition.value.x
  const startTop = panelPosition.value.y

  const onMouseMove = (e) => {
    panelPosition.value = {
      x: startLeft + e.clientX - startX,
      y: startTop + e.clientY - startY
    }
  }

  const onMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

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

const selectAiOption = (option) => {
  inputMessage.value = option
  aiOptions.value = []
}

onMounted(() => {
  scrollToBottom()
  startEnergyRecovery()
  fetchWorldPosts()
})

onUnmounted(() => {
  if (energyTimer.value) {
    clearInterval(energyTimer.value)
  }
})

// 发送消息时更新游戏状态
const updateGameState = () => {
  // 消耗体力
  energy.value = Math.max(0, energy.value - 10)
  
  // 增加轮次
  turnCount.value += 1
  
  // 随机变化稳定度
  stability.value = Math.min(100, Math.max(0, stability.value + (Math.random() > 0.5 ? 5 : -3)))
}

const sendMessage = async () => {
  if (inputMessage.value.trim() === '' || energy.value < 10) return;

  // 更新游戏状态
  updateGameState()

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
</script>

<style scoped>
.forum-layout {
  display: grid;
  grid-template-areas:
    "header header"
    "main sidebar"
    "input input"
    "footer footer";
  grid-template-columns: 1fr 300px;
  grid-template-rows: auto 1fr auto auto;
  min-height: 100vh;
  gap: 1rem;
  padding: 1rem;
}

.main-content {
  grid-area: main;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.world-map {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
}

.story-content {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
}

.sidebar {
  grid-area: sidebar;
  position: relative;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 50px;
}

.toggle-sidebar {
  position: absolute;
  left: -25px;
  top: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  border: none;
  cursor: pointer;
  z-index: 10;
}

.input-area {
  grid-area: input;
}

.floating-panel {
  position: fixed;
  width: 200px;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.panel-header {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  cursor: move;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-content {
  padding: 1rem;
}

.status-item {
  margin-bottom: 0.5rem;
}

/* 保留原有聊天区域样式 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f8fafc;
}

/* 保留原有宝物区域样式 */
.treasure-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
}

@media (max-width: 768px) {
  .forum-layout {
    grid-template-areas:
      "header"
      "main"
      "sidebar"
      "input"
      "footer";
    grid-template-columns: 1fr;
  }

  .sidebar {
    width: 100%;
  }

  .sidebar.collapsed {
    width: 60px;
  }

  .toggle-sidebar {
    left: 10px;
  }
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
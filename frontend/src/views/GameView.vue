<template>
  <Header />
  <div class="game-container">

    <!-- 动态切换布局 -->
    <div class="main-content">
      <!-- 空间列表视图 -->
      <div v-if="!currentSpace" class="space-list-view">
        <div class="space-category">
          <h3>个人探索</h3>
          <div v-for="space in tempSpaces" :key="space.id" class="space-item" @click="loadSpace(space)">
            {{ space.name }}
          </div>
        </div>

        <div class="space-category">
          <h3>团队探索</h3>
          <div v-for="space in stableSpaces" :key="space.id" class="space-item" @click="loadSpace(space)">
            {{ space.name }} ({{ space.stability }}%)
          </div>
        </div>

        <div class="space-category">
          <h3>公共探索</h3>
          <div v-for="space in fixedSpaces" :key="space.id" class="space-item" @click="loadSpace(space)">
            {{ space.name }}
          </div>
        </div>
      </div>

      <!-- 空间内容视图 -->
      <div v-else class="space-detail-view">
        <button class="back-button" @click="backToList">
          ← 返回空间列表
        </button>

        <div class="space-header">
          <h2>{{ currentSpace.name }}</h2>
          <div class="space-meta">
            <span>稳定度: {{ currentSpace.stability }}%</span>
            <span>剩余轮次: {{ currentSpace.turnsLeft }}</span>
          </div>
        </div>

        <div class="space-story">
          {{ currentSpace.story }}
        </div>

        <div class="conversation-history">
          <div v-for="reply in currentReplies" :key="reply.id" class="reply">
            <div class="reply-content">{{ reply.content }}</div>
            <div class="reply-meta">
              <span>{{ reply.author }}</span>
              <span>{{ formatTime(reply.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧状态面板 (始终显示) -->
    <div class="status-panel">
      <!-- 宝物区 -->
      <div class="treasure-area">
        <div v-if="currentTreasure.identified" class="treasure-identified">
          <img :src="currentTreasure.image" alt="宝物" class="treasure-image">
          <h3>{{ currentTreasure.name }}</h3>
          <div class="treasure-stats">
            <div>强度: {{ currentTreasure.strength }}/256</div>
            <div>效果: {{ currentTreasure.effect }}</div>
          </div>
        </div>
        <div v-else class="treasure-unidentified">
          <img src="@/assets/images/background.png" alt="未鉴定宝物" class="treasure-image">
          <button @click="identifyTreasure" class="identify-btn">鉴定宝物</button>
        </div>
      </div>

      <!-- 状态区 -->
      <div class="status-area">
        <div class="status-item">
          <span>轮次</span>
          <span>{{ turnCount }}/10</span>
        </div>
        <div class="status-item">
          <span>体力</span>
          <span>{{ energy }}/100</span>
        </div>
        <div class="status-item">
          <span>资历</span>
          <span>{{ experience }}</span>
        </div>
      </div>

      <!-- 行动选择区 -->
      <div class="action-area">
        <div class="action-buttons">
          <button @click="takeAction('explore')" :disabled="energy < 15">探索</button>
          <button @click="takeAction('attack')" :disabled="energy < 20">攻击</button>
          <button @click="showCardSelection = true" :disabled="energy < 10">使用卡牌</button>
        </div>

        <div v-if="showCardSelection" class="card-selection">
          <div v-for="card in availableCards" :key="card.id" @click="useCard(card)" class="card-item">
            {{ card.name }}
          </div>
        </div>

        <div class="custom-action">
          <input v-model="customMessage" placeholder="自定义行动...">
          <button @click="submitCustomAction">提交</button>
        </div>
      </div>
    </div>
  </div>

  <Footer />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 空间数据
const tempSpaces = ref([])
const stableSpaces = ref([])
const fixedSpaces = ref([])
const currentSpace = ref(null)
const currentReplies = ref([])

// 状态数据
const turnCount = ref(1)
const energy = ref(100)
const experience = ref(0)

// 宝物数据
const currentTreasure = ref({
  identified: false,
  name: '',
  image: '',
  strength: 0,
  effect: ''
})

// 卡牌数据
const availableCards = ref([])
const showCardSelection = ref(false)

// 初始化加载数据
const loadInitialData = async () => {
  try {
    const [spacesRes, cardsRes] = await Promise.all([
      axios.get('/api/game/spaces'),
      axios.get('/api/game/treasures')
    ])
    
    tempSpaces.value = spacesRes.data.filter(s => s.type === 'temp')
    stableSpaces.value = spacesRes.data.filter(s => s.type === 'stable')
    fixedSpaces.value = spacesRes.data.filter(s => s.type === 'fixed')
    availableCards.value = cardsRes.data
  } catch (error) {
    console.error('初始化数据加载失败:', error)
  }
}

// 加载空间详情
const loadSpace = async (space) => {
  try {
    const [spaceRes, repliesRes] = await Promise.all([
      axios.get(`/api/game/spaces/${space.id}/status`),
      axios.get(`/api/game/spaces/${space.id}/replies`)
    ])
    
    currentSpace.value = spaceRes.data
    currentReplies.value = repliesRes.data
  } catch (error) {
    console.error('加载空间详情失败:', error)
  }
}

// 鉴定宝物
const identifyTreasure = async () => {
  try {
    const res = await axios.post(`/api/game/treasures/identify`, {
      treasureId: currentTreasure.value.id
    })
    currentTreasure.value = res.data
  } catch (error) {
    console.error('鉴定宝物失败:', error)
  }
}

// 执行行动
const takeAction = async (actionType) => {
  try {
    const res = await axios.post('/api/game/actions', {
      type: actionType,
      spaceId: currentSpace.value?.id
    })
    
    // 更新状态
    energy.value = res.data.energy
    turnCount.value = res.data.turnCount
    experience.value = res.data.experience
    
    // 如果有新宝物
    if (res.data.newTreasure) {
      currentTreasure.value = res.data.newTreasure
    }
  } catch (error) {
    console.error('执行行动失败:', error)
  }
}

// 使用卡牌
const useCard = async (card) => {
  try {
    const res = await axios.post(`/api/game/treasures/${card.id}/use`, {
      spaceId: currentSpace.value?.id
    })
    
    // 更新状态
    energy.value = res.data.energy
    showCardSelection.value = false
    
    // 如果有新宝物
    if (res.data.newTreasure) {
      currentTreasure.value = res.data.newTreasure
    }
  } catch (error) {
    console.error('使用卡牌失败:', error)
  }
}

// 提交自定义行动
const submitCustomAction = async () => {
  if (!customMessage.value.trim()) return
  
  try {
    const res = await axios.post('/api/game/actions/custom', {
      message: customMessage.value,
      spaceId: currentSpace.value?.id
    })
    
    // 更新对话历史
    currentReplies.value.push(res.data.newReply)
    customMessage.value = ''
  } catch (error) {
    console.error('提交自定义行动失败:', error)
  }
}

onMounted(() => {
  loadInitialData()
  
  // 初始化体力恢复计时器
  setInterval(() => {
    if (energy.value < 100) {
      energy.value = Math.min(energy.value + 1, 100)
    }
  }, 60000) // 每分钟恢复1点体力
})
</script>

<style scoped>
.game-container {
  display: flex;
  height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.space-list-view {
  max-width: 800px;
  margin: 0 auto;
}

.space-detail-view {
  max-width: 800px;
  margin: 0 auto;
  animation: fadeIn 0.3s ease-out;
}

.back-button {
  margin-bottom: 20px;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.back-button:hover {
  background: #2563eb;
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

.space-list {
  border-right: 1px solid #eee;
  padding-right: 10px;
}

.space-category {
  margin-bottom: 20px;
}

.space-item {
  padding: 10px;
  margin: 5px 0;
  cursor: pointer;
  border-radius: 4px;
}

.space-item:hover {
  background-color: #f5f5f5;
}

.main-content {
  overflow-y: auto;
}

.space-detail {
  padding: 10px;
}

.conversation-history {
  margin-top: 20px;
}

.reply {
  margin-bottom: 15px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.status-panel {
  border-left: 1px solid #eee;
  padding-left: 10px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.treasure-area {
  text-align: center;
}

.treasure-image {
  width: 150px;
  height: 150px;
  object-fit: contain;
}

.identify-btn {
  margin-top: 10px;
  padding: 5px 10px;
}

.status-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
}

.action-area {
  margin-top: auto;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}

.action-buttons button {
  padding: 8px;
}

.card-selection {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.card-item {
  padding: 8px;
  margin: 3px 0;
  cursor: pointer;
}

.card-item:hover {
  background-color: #f5f5f5;
}

.custom-action {
  display: flex;
  gap: 5px;
}

.custom-action input {
  flex: 1;
  padding: 8px;
}
</style>

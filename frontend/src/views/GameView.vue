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
        <div v-if="currentTreasure && currentTreasure.identified" class="treasure-identified">
          <img v-lazy="currentTreasure.image" alt="宝物" class="treasure-image">
          <h3>{{ currentTreasure.name }}</h3>
          <div class="treasure-stats">
            <div>强度: {{ currentTreasure.strength }}/256</div>
            <div>效果: {{ currentTreasure.effect }}</div>
          </div>
        </div>
        <div v-else class="treasure-unidentified">
          <img v-lazy="'@/assets/images/defcard.png'" alt="未鉴定宝物" class="treasure-image">
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
import { ref } from 'vue';
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';

// 定义使用的组件
const currentSpace = ref(null);
const tempSpaces = ref([
  { id: 'temp1', name: '临时空间1' },
  { id: 'temp2', name: '临时空间2' }
]);
const stableSpaces = ref([
  { id: 'stable1', name: '稳定空间1', stability: 75 },
  { id: 'stable2', name: '稳定空间2', stability: 85 }
]);
const fixedSpaces = ref([
  { id: 'fixed1', name: '固定空间1' },
  { id: 'fixed2', name: '固定空间2' }
]);
const currentReplies = ref([
  { id: 'r1', content: '这是一个回复', author: '用户1', createdAt: new Date() }
]);
const currentTreasure = ref({
  identified: false,
  name: '',
  strength: 0,
  effect: '',
  image: ''
});
const turnCount = ref(5);
const energy = ref(100);
const experience = ref(0);
const showCardSelection = ref(false);
const availableCards = ref([
  { id: 'card1', name: '卡牌1' },
  { id: 'card2', name: '卡牌2' }
]);
const customMessage = ref('');

// 格式化时间方法
function formatTime(date) {
  return date.toLocaleString();
}

// 加载空间方法
function loadSpace(space) {
  currentSpace.value = space;
}

// 返回列表方法
function backToList() {
  currentSpace.value = null;
}

// 鉴定宝物方法
function identifyTreasure() {
  // 模拟鉴定结果
  currentTreasure.value = {
    identified: true,
    name: '神秘宝珠',
    strength: 150,
    effect: '增加空间稳定性',
    image: '@/assets/images/treasure.png'
  };
}

// 执行行动方法
function takeAction(actionType) {
  // 这里添加实际的行动逻辑
  console.log(`执行${actionType}行动`);
}

// 使用卡牌方法
function useCard(card) {
  // 这里添加使用卡牌的逻辑
  console.log(`使用卡牌: ${card.name}`);
  showCardSelection.value = false;
}

// 提交自定义行动
function submitCustomAction() {
  // 这里添加提交逻辑
  console.log('提交自定义行动:', customMessage.value);
}
</script>

<style scoped>
/* 移动端专用样式 */
@media (max-width: 768px) {
  .game-container {
    flex-direction: column;
  }
  
  .space-list {
    flex: 0 0 auto;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .space-detail {
    flex: 1 1 auto;
    overflow-y: auto;
  }
  
  .action-panel {
    flex-direction: column;
    padding: 10px;
  }
  
  .card-display {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>
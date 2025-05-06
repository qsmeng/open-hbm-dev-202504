import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import VueLazyload from 'vue-lazyload'

import './assets/main.css'

const app = createApp(App)

// 配置图片懒加载
app.use(VueLazyload, {
  loading: '/src/assets/images/defcard.png', // 加载中显示的图片
  error: '/src/assets/images/defcard.png',  // 加载失败显示的图片
  attempt: 3, // 尝试加载次数
  throttleWait: 300 // 节流等待时间(ms)
})

app.use(router)

app.mount('#app')
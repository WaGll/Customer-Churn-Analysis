import { createApp } from 'vue'
import './styles/tokens.css'
import './styles/transitions.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus, { locale: undefined })  // 默认中文
app.use(router)
app.mount('#app')

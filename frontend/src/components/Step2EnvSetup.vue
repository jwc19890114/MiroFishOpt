<template>
  <div class="env-setup-panel">
    <div class="scroll-container">
      <!-- Step 01: 模拟实例 -->
      <div class="step-card" :class="{ 'active': phase === 0, 'completed': phase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">模拟实例初始化</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 0" class="badge success">已完成</span>
            <span v-else class="badge processing">初始化</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/simulation/create</p>
          <p class="description">
            新建simulation实例，拉取模拟世界参数模版
          </p>

          <div v-if="simulationId" class="info-card">
            <div class="info-row">
              <span class="info-label">Project ID</span>
              <span class="info-value mono">{{ projectData?.project_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Graph ID</span>
              <span class="info-value mono">{{ projectData?.graph_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Simulation ID</span>
              <span class="info-value mono">{{ simulationId }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Task ID</span>
              <span class="info-value mono">{{ taskId || '异步任务已完成' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 02: 生成 Agent 人设 -->
      <div class="step-card" :class="{ 'active': phase === 1, 'completed': phase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">生成 Agent 人设</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 1" class="badge success">已完成</span>
            <span v-else-if="phase === 1" class="badge processing">{{ prepareProgress }}%</span>
            <span v-else class="badge pending">等待</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            结合上下文，自动调用工具从知识图谱梳理实体与关系，初始化模拟个体，并基于现实种子赋予他们独特的行为与记忆
          </p>

          <!-- Profiles Stats -->
          <div v-if="profiles.length > 0" class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ profiles.length }}</span>
              <span class="stat-label">当前Agent数</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ expectedTotal || '-' }}</span>
              <span class="stat-label">预期Agent总数</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ totalTopicsCount }}</span>
              <span class="stat-label">现实种子当前关联话题数</span>
            </div>
          </div>

          <!-- Profiles List Preview -->
          <div v-if="profiles.length > 0" class="profiles-preview">
            <div class="preview-header">
              <span class="preview-title">已生成的 Agent 人设</span>
            </div>
            <div class="profiles-list">
              <div 
                v-for="(profile, idx) in profiles" 
                :key="idx" 
                class="profile-card"
                @click="selectProfile(profile)"
              >
                <div class="profile-header">
                  <span class="profile-realname">{{ profile.realname || 'Unknown' }}</span>
                  <span class="profile-username">@{{ profile.username || `agent_${idx}` }}</span>
                </div>
                <div class="profile-meta">
                  <span class="profile-profession">{{ profile.profession || '未知职业' }}</span>
                </div>
                <p class="profile-bio">{{ profile.bio || '暂无简介' }}</p>
                <div v-if="profile.interested_topics?.length" class="profile-topics">
                  <span 
                    v-for="topic in profile.interested_topics.slice(0, 3)" 
                    :key="topic" 
                    class="topic-tag"
                  >{{ topic }}</span>
                  <span v-if="profile.interested_topics.length > 3" class="topic-more">
                    +{{ profile.interested_topics.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 03: 生成双平台模拟配置 -->
      <div class="step-card" :class="{ 'active': phase === 2, 'completed': phase > 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">生成双平台模拟配置</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 2" class="badge success">已完成</span>
            <span v-else-if="phase === 2" class="badge processing">生成中</span>
            <span v-else class="badge pending">等待</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            LLM 根据模拟需求与现实种子，智能设置世界时间流速、推荐算法、每个个体的活跃时间段、发言频率、事件触发等参数
          </p>
          
          <!-- Config Preview -->
          <div v-if="simulationConfig" class="config-preview">
            <div class="config-section">
              <span class="config-label">模拟时长</span>
              <span class="config-value">{{ simulationConfig.time_config?.total_simulation_hours || '-' }} 小时</span>
            </div>
            <div class="config-section">
              <span class="config-label">总轮次</span>
              <span class="config-value">{{ (simulationConfig.time_config?.total_simulation_hours * 60 / simulationConfig.time_config?.minutes_per_round) || '-' }} 轮</span>
            </div>
            <div class="config-section">
              <span class="config-label">平台配置</span>
              <span class="config-value">
                <span v-if="simulationConfig.twitter_config" class="platform-tag">Twitter</span>
                <span v-if="simulationConfig.reddit_config" class="platform-tag">Reddit</span>
              </span>
            </div>
            
            <!-- LLM Reasoning -->
            <div v-if="simulationConfig.generation_reasoning" class="reasoning-section">
              <span class="reasoning-label">LLM 配置推理</span>
              <p class="reasoning-text">{{ simulationConfig.generation_reasoning.split('|')[0] }} ...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 04: 初始激活编排 -->
      <div class="step-card" :class="{ 'active': phase === 3, 'completed': phase > 3 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">04</span>
            <span class="step-title">初始激活编排</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 3" class="badge success">已完成</span>
            <span v-else-if="phase === 3" class="badge processing">编排中</span>
            <span v-else class="badge pending">等待</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">Event Orchestration</p>
          <p class="description">
            基于叙事方向，自动生成初始激活事件与热点话题，引导模拟世界的初始状态
          </p>

          <div v-if="simulationConfig?.event_config" class="orchestration-content">
            <!-- 叙事方向 -->
            <div class="narrative-box">
              <span class="box-label">叙事引导方向</span>
              <p class="narrative-text">{{ simulationConfig.event_config.narrative_direction }}</p>
            </div>

            <!-- 热点话题 -->
            <div class="topics-section">
              <span class="box-label">初始热点话题</span>
              <div class="hot-topics-grid">
                <span v-for="topic in simulationConfig.event_config.hot_topics" :key="topic" class="hot-topic-tag">
                  # {{ topic }}
                </span>
              </div>
            </div>

            <!-- 初始帖子流 -->
            <div class="initial-posts-section">
              <span class="box-label">初始激活序列 ({{ simulationConfig.event_config.initial_posts.length }})</span>
              <div class="posts-timeline">
                <div v-for="(post, idx) in simulationConfig.event_config.initial_posts" :key="idx" class="timeline-item">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="post-header">
                      <span class="post-role">{{ post.poster_type }}</span>
                      <span class="post-agent-info">
                        <span class="post-id">Agent {{ post.poster_agent_id }}</span>
                        <span class="post-username">@{{ getAgentUsername(post.poster_agent_id) }}</span>
                      </span>
                    </div>
                    <p class="post-text">{{ post.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 05: 准备完成 -->
      <div class="step-card" :class="{ 'active': phase === 4 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">05</span>
            <span class="step-title">准备完成</span>
          </div>
          <div class="step-status">
            <span v-if="phase >= 4" class="badge processing">进行中</span>
          </div>
        </div>

        <div class="card-content">
          <p class="description">模拟环境已准备完成，可以开始运行模拟</p>
          <div class="action-group">
            <button 
              class="action-btn secondary"
              @click="$emit('go-back')"
            >
              ← 返回图谱
            </button>
            <button 
              class="action-btn primary"
              :disabled="phase < 4"
              @click="$emit('next-step')"
            >
              开始模拟 ➝
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Detail Modal -->
    <div v-if="selectedProfile" class="profile-modal-overlay" @click.self="selectedProfile = null">
      <div class="profile-modal">
        <div class="modal-header">
          <div class="modal-header-info">
            <div class="modal-name-row">
              <span class="modal-realname">{{ selectedProfile.realname }}</span>
              <span class="modal-username">@{{ selectedProfile.username }}</span>
            </div>
            <span class="modal-profession">{{ selectedProfile.profession }}</span>
          </div>
          <button class="close-btn" @click="selectedProfile = null">×</button>
        </div>
        
        <div class="modal-body">
          <!-- 基本信息 -->
          <div class="modal-info-grid">
            <div class="info-item">
              <span class="info-label">事件外显年龄</span>
              <span class="info-value">{{ selectedProfile.age || '-' }} 岁</span>
            </div>
            <div class="info-item">
              <span class="info-label">事件外显性别</span>
              <span class="info-value">{{ { male: '男', female: '女', other: '其他' }[selectedProfile.gender] || selectedProfile.gender }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">国家/地区</span>
              <span class="info-value">{{ selectedProfile.country || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">事件外显MBTI</span>
              <span class="info-value mbti">{{ selectedProfile.mbti || '-' }}</span>
            </div>
          </div>

          <!-- 简介 -->
          <div class="modal-section">
            <span class="section-label">人设简介</span>
            <p class="section-bio">{{ selectedProfile.bio || '暂无简介' }}</p>
          </div>

          <!-- 关注话题 -->
          <div class="modal-section" v-if="selectedProfile.interested_topics?.length">
            <span class="section-label">现实种子关联话题</span>
            <div class="topics-grid">
              <span 
                v-for="topic in selectedProfile.interested_topics" 
                :key="topic" 
                class="topic-item"
              >{{ topic }}</span>
            </div>
          </div>

          <!-- 详细人设 -->
          <div class="modal-section" v-if="selectedProfile.persona">
            <span class="section-label">详细人设背景</span>
            
            <!-- 人设维度概览 -->
            <div class="persona-dimensions">
              <div class="dimension-card">
                <span class="dim-title">事件全景经历</span>
                <span class="dim-desc">在此事件中的完整行为轨迹</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">行为模式侧写</span>
                <span class="dim-desc">经验总结与行事风格偏好</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">独特记忆印记</span>
                <span class="dim-desc">基于现实种子形成的记忆</span>
              </div>
              <div class="dimension-card">
                <span class="dim-title">社会关系网络</span>
                <span class="dim-desc">个体链接与交互图谱</span>
              </div>
            </div>

            <div class="persona-content">
              <p class="section-persona">{{ selectedProfile.persona }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Info / Logs -->
    <div class="system-logs">
      <div class="log-header">
        <span class="log-title">SYSTEM DASHBOARD</span>
        <span class="log-id">{{ simulationId || 'NO_SIMULATION' }}</span>
      </div>
      <div class="log-content" ref="logContent">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { 
  prepareSimulation, 
  getPrepareStatus, 
  getSimulationProfilesRealtime,
  getSimulationConfig,
  getSimulationConfigRealtime 
} from '../api/simulation'

const props = defineProps({
  simulationId: String,  // 从父组件传入
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

// State
const phase = ref(0) // 0: 初始化, 1: 生成人设, 2: 生成配置, 3: 完成
const taskId = ref(null)
const prepareProgress = ref(0)
const currentStage = ref('')
const progressMessage = ref('')
const profiles = ref([])
const entityTypes = ref([])
const expectedTotal = ref(null)
const simulationConfig = ref(null)
const selectedProfile = ref(null)
const showProfilesDetail = ref(true)

// Watch stage to update phase
watch(currentStage, (newStage) => {
  if (newStage === '生成Agent人设' || newStage === 'generating_profiles') {
    phase.value = 1
  } else if (newStage === '生成模拟配置' || newStage === 'generating_config') {
    phase.value = 2
    // 进入配置生成阶段，开始轮询配置
    if (!configTimer) {
      addLog('开始生成双平台模拟配置...')
      startConfigPolling()
    }
  } else if (newStage === '准备模拟脚本' || newStage === 'copying_scripts') {
    phase.value = 2 // 仍属于配置阶段
  }
})

// Polling timer
let pollTimer = null
let profilesTimer = null
let configTimer = null

// Computed
const displayProfiles = computed(() => {
  if (showProfilesDetail.value) {
    return profiles.value
  }
  return profiles.value.slice(0, 6)
})

// 根据agent_id获取对应的username
const getAgentUsername = (agentId) => {
  if (profiles.value && profiles.value.length > agentId && agentId >= 0) {
    const profile = profiles.value[agentId]
    return profile?.username || `agent_${agentId}`
  }
  return `agent_${agentId}`
}

// 计算所有人设的关联话题总数
const totalTopicsCount = computed(() => {
  return profiles.value.reduce((sum, p) => {
    return sum + (p.interested_topics?.length || 0)
  }, 0)
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

const truncateBio = (bio) => {
  if (bio.length > 80) {
    return bio.substring(0, 80) + '...'
  }
  return bio
}

const selectProfile = (profile) => {
  selectedProfile.value = profile
}

// 自动开始准备模拟
const startPrepareSimulation = async () => {
  if (!props.simulationId) {
    addLog('错误：缺少 simulationId')
    emit('update-status', 'error')
    return
  }
  
  // 标记第一步完成，开始第二步
  phase.value = 1
  addLog(`模拟实例已创建: ${props.simulationId}`)
  addLog('正在准备模拟环境...')
  emit('update-status', 'processing')
  
  try {
    const res = await prepareSimulation({
      simulation_id: props.simulationId,
      use_llm_for_profiles: true,
      parallel_profile_count: 5
    })
    
    if (res.success && res.data) {
      if (res.data.already_prepared) {
        addLog('检测到已有完成的准备工作，直接使用')
        await loadPreparedData()
        return
      }
      
      taskId.value = res.data.task_id
      addLog(`准备任务已启动: ${res.data.task_id}`)
      
      // 开始轮询进度
      startPolling()
      // 开始实时获取 Profiles
      startProfilesPolling()
    } else {
      addLog(`准备失败: ${res.error || '未知错误'}`)
      emit('update-status', 'error')
    }
  } catch (err) {
    addLog(`准备异常: ${err.message}`)
    emit('update-status', 'error')
  }
}

const startPolling = () => {
  pollTimer = setInterval(pollPrepareStatus, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const startProfilesPolling = () => {
  profilesTimer = setInterval(fetchProfilesRealtime, 3000)
}

const stopProfilesPolling = () => {
  if (profilesTimer) {
    clearInterval(profilesTimer)
    profilesTimer = null
  }
}

const pollPrepareStatus = async () => {
  if (!taskId.value && !props.simulationId) return
  
  try {
    const res = await getPrepareStatus({
      task_id: taskId.value,
      simulation_id: props.simulationId
    })
    
    if (res.success && res.data) {
      const data = res.data
      
      // 更新进度
      prepareProgress.value = data.progress || 0
      progressMessage.value = data.message || ''
      
      // 解析阶段信息
      if (data.progress_detail) {
        currentStage.value = data.progress_detail.current_stage_name || ''
      } else if (data.message) {
        // 从消息中提取阶段
        const match = data.message.match(/\[(\d+)\/(\d+)\]\s*([^:]+)/)
        if (match) {
          currentStage.value = match[3].trim()
        }
      }
      
      // 检查是否完成
      if (data.status === 'completed' || data.status === 'ready' || data.already_prepared) {
        addLog('准备工作已完成')
        stopPolling()
        stopProfilesPolling()
        await loadPreparedData()
      } else if (data.status === 'failed') {
        addLog(`准备失败: ${data.error || '未知错误'}`)
        stopPolling()
        stopProfilesPolling()
      }
    }
  } catch (err) {
    console.warn('轮询状态失败:', err)
  }
}

const fetchProfilesRealtime = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getSimulationProfilesRealtime(props.simulationId, 'reddit')
    
    if (res.success && res.data) {
      profiles.value = res.data.profiles || []
      expectedTotal.value = res.data.total_expected
      
      // 提取实体类型
      const types = new Set()
      profiles.value.forEach(p => {
        if (p.entity_type) types.add(p.entity_type)
      })
      entityTypes.value = Array.from(types)
    }
  } catch (err) {
    console.warn('获取 Profiles 失败:', err)
  }
}

// 配置轮询
const startConfigPolling = () => {
  configTimer = setInterval(fetchConfigRealtime, 2000)
}

const stopConfigPolling = () => {
  if (configTimer) {
    clearInterval(configTimer)
    configTimer = null
  }
}

const fetchConfigRealtime = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    
    if (res.success && res.data) {
      const data = res.data
      
      // 如果配置已生成
      if (data.config_generated && data.config) {
        simulationConfig.value = data.config
        addLog('模拟配置生成完成')
        
        // 显示配置摘要
        if (data.summary) {
          addLog(`配置摘要: ${data.summary.total_agents}个Agent, ${data.summary.simulation_hours}小时, ${data.summary.initial_posts_count}条初始帖子`)
        }
        
        stopConfigPolling()
        phase.value = 4
        addLog('环境搭建完成，可以开始模拟')
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('获取 Config 失败:', err)
  }
}

const loadPreparedData = async () => {
  phase.value = 2
  addLog('正在加载配置数据...')

  // 最后获取一次 Profiles
  await fetchProfilesRealtime()

  // 获取配置（使用实时接口）
  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    if (res.success && res.data) {
      if (res.data.config_generated && res.data.config) {
        simulationConfig.value = res.data.config
        addLog('模拟配置加载成功')
        
        // 显示配置摘要
        if (res.data.summary) {
          addLog(`配置摘要: ${res.data.summary.total_agents}个Agent, ${res.data.summary.simulation_hours}小时`)
        }
        
        addLog('环境搭建完成，可以开始模拟')
        phase.value = 4
        emit('update-status', 'completed')
      } else {
        // 配置尚未生成，开始轮询
        addLog('配置生成中，等待完成...')
        startConfigPolling()
      }
    }
  } catch (err) {
    addLog(`加载配置失败: ${err.message}`)
    emit('update-status', 'error')
  }
}

// Scroll log to bottom
const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})

onMounted(() => {
  // 自动开始准备流程
  if (props.simulationId) {
    addLog('Step2 环境搭建初始化')
    startPrepareSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
  stopProfilesPolling()
  stopConfigPolling()
})
</script>

<style scoped>
.env-setup-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #FAFAFA;
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Step Card */
.step-card {
  background: #FFF;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #EAEAEA;
  transition: all 0.3s ease;
  position: relative;
}

.step-card.active {
  border-color: #FF5722;
  box-shadow: 0 4px 12px rgba(255, 87, 34, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 700;
  color: #E0E0E0;
}

.step-card.active .step-num,
.step-card.completed .step-num {
  color: #000;
}

.step-title {
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.badge {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.success { background: #E8F5E9; color: #2E7D32; }
.badge.processing { background: #FFF3E0; color: #E65100; }
.badge.pending { background: #F5F5F5; color: #999; }
.badge.accent { background: #E3F2FD; color: #1565C0; }

.card-content {
  /* No extra padding - uses step-card's padding */
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #999;
  margin-bottom: 8px;
}

.description {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 16px;
}

/* Action Section */
.action-section {
  margin-top: 16px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.primary {
  background: #000;
  color: #FFF;
}

.action-btn.primary:hover:not(:disabled) {
  background: #FF5722;
}

.action-btn.secondary {
  background: #F5F5F5;
  color: #333;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #E5E5E5;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-group {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

/* Info Card */
.info-card {
  background: #F5F5F5;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #E0E0E0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 12px;
  color: #666;
}

.info-value {
  font-size: 13px;
  font-weight: 500;
}

.info-value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  background: #F9F9F9;
  padding: 16px;
  border-radius: 6px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #000;
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 9px;
  color: #999;
  text-transform: uppercase;
  margin-top: 4px;
  display: block;
}

/* Profiles Preview */
.profiles-preview {
  margin-top: 20px;
  border-top: 1px solid #E5E5E5;
  padding-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-title {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profiles-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 4px;
}

.profiles-list::-webkit-scrollbar {
  width: 4px;
}

.profiles-list::-webkit-scrollbar-thumb {
  background: #DDD;
  border-radius: 2px;
}

.profiles-list::-webkit-scrollbar-thumb:hover {
  background: #CCC;
}

.profile-card {
  background: #FAFAFA;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-card:hover {
  border-color: #FF5722;
  background: #FFF;
}

.profile-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}

.profile-realname {
  font-size: 14px;
  font-weight: 700;
  color: #000;
}

.profile-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #999;
}

.profile-meta {
  margin-bottom: 8px;
}

.profile-profession {
  font-size: 11px;
  color: #666;
  background: #F0F0F0;
  padding: 2px 8px;
  border-radius: 3px;
}

.profile-bio {
  font-size: 12px;
  color: #444;
  line-height: 1.6;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.profile-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.topic-tag {
  font-size: 10px;
  color: #1565C0;
  background: #E3F2FD;
  padding: 2px 8px;
  border-radius: 10px;
}

.topic-more {
  font-size: 10px;
  color: #999;
  padding: 2px 6px;
}

/* Config Preview */
.config-preview {
  background: #FAFAFA;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.config-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #E0E0E0;
}

.config-section:last-child {
  border-bottom: none;
}

.config-label {
  font-size: 12px;
  color: #666;
}

.config-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.platform-tag {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  background: #333;
  color: #FFF;
  padding: 2px 8px;
  border-radius: 3px;
  margin-left: 6px;
}

.reasoning-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E0E0E0;
}

.reasoning-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.reasoning-text {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* Profile Modal */
.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.profile-modal {
  background: #FFF;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: #FFF;
  border-bottom: 1px solid #F0F0F0;
}

.modal-header-info {
  flex: 1;
}

.modal-name-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 8px;
}

.modal-realname {
  font-size: 20px;
  font-weight: 700;
  color: #000;
}

.modal-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #999;
}

.modal-profession {
  font-size: 12px;
  color: #666;
  background: #F5F5F5;
  padding: 4px 10px;
  border-radius: 4px;
  display: inline-block;
  font-weight: 500;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #999;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: color 0.2s;
  padding: 0;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* 基本信息网格 */
.modal-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px 16px;
  margin-bottom: 32px;
  padding: 0;
  background: transparent;
  border-radius: 0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.info-value.mbti {
  font-family: 'JetBrains Mono', monospace;
  color: #FF5722;
}

/* 模块区域 */
.modal-section {
  margin-bottom: 28px;
}

.section-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.section-bio {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
  padding: 16px;
  background: #F9F9F9;
  border-radius: 6px;
  border-left: 3px solid #E0E0E0;
}

/* 话题标签 */
.topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-item {
  font-size: 11px;
  color: #1565C0;
  background: #E3F2FD;
  padding: 4px 10px;
  border-radius: 12px;
  transition: all 0.2s;
  border: none;
}

.topic-item:hover {
  background: #BBDEFB;
  color: #0D47A1;
}

/* 详细人设 */
.persona-dimensions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.dimension-card {
  background: #F8F9FA;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #DDD;
  transition: all 0.2s;
}

.dimension-card:hover {
  background: #F0F0F0;
  border-left-color: #999;
}

.dim-title {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.dim-desc {
  display: block;
  font-size: 10px;
  color: #888;
  line-height: 1.4;
}

.persona-content {
  max-height: none;
  overflow: visible;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
}

.persona-content::-webkit-scrollbar {
  width: 4px;
}

.persona-content::-webkit-scrollbar-thumb {
  background: #DDD;
  border-radius: 2px;
}

.section-persona {
  font-size: 13px;
  color: #555;
  line-height: 1.8;
  margin: 0;
  text-align: justify;
}

/* System Logs */
.system-logs {
  background: #000;
  color: #DDD;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid #222;
  flex-shrink: 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #333;
  padding-bottom: 8px;
  margin-bottom: 8px;
  font-size: 10px;
  color: #888;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 80px; /* Approx 4 lines visible */
  overflow-y: auto;
  padding-right: 4px;
}

.log-content::-webkit-scrollbar {
  width: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}

.log-line {
  font-size: 11px;
  display: flex;
  gap: 12px;
  line-height: 1.5;
}

.log-time {
  color: #666;
  min-width: 75px;
}

.log-msg {
  color: #CCC;
  word-break: break-all;
}

/* Spinner */
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid #E5E5E5;
  border-top-color: #FF5722;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
/* Orchestration Content */
.orchestration-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 16px;
}

.box-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.narrative-box {
  background: #F9F9F9;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #FF5722;
}

.narrative-text {
  font-size: 13px;
  color: #444;
  line-height: 1.6;
  margin: 0;
  text-align: justify;
}

.topics-section {
  background: #FFF;
}

.hot-topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-topic-tag {
  font-size: 12px;
  color: #FF5722;
  background: #FFF3E0;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.hot-topic-more {
  font-size: 11px;
  color: #999;
  padding: 4px 6px;
}

.initial-posts-section {
  border-top: 1px solid #EAEAEA;
  padding-top: 16px;
}

.posts-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 8px;
  border-left: 2px solid #F0F0F0;
  margin-top: 12px;
}

.timeline-item {
  position: relative;
  padding-left: 20px;
}

.timeline-marker {
  position: absolute;
  left: 0;
  top: 14px;
  width: 12px;
  height: 2px;
  background: #DDD;
}

.timeline-content {
  background: #F9F9F9;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #EEE;
}

.post-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.post-role {
  font-size: 11px;
  font-weight: 700;
  color: #333;
  text-transform: uppercase;
}

.post-agent-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.post-id,
.post-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #666;
  line-height: 1;
  vertical-align: baseline;
}

.post-username {
  margin-right: 6px;
}

.post-text {
  font-size: 12px;
  color: #555;
  line-height: 1.5;
  margin: 0;
}
</style>


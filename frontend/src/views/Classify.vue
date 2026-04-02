<template>
  <div class="classify-page container">
    <div class="page-header">
      <h1>智能垃圾识别</h1>
      <el-tag v-if="currentModel" round type="info" size="small">模型: {{ currentModel }}</el-tag>
    </div>

    <div class="classify-card">
      <el-tabs v-model="activeTab" class="classify-tabs">
        <!-- 单张识别 -->
        <el-tab-pane label="单张识别" name="single">
          <div class="tab-content">
            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept="image/*"
            >
              <div class="upload-inner">
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <p class="upload-text">将图片拖到此处，或<em>点击上传</em></p>
                <p class="upload-hint">支持 JPG、PNG、BMP 格式</p>
              </div>
            </el-upload>

            <div v-if="previewImage" class="preview-area">
              <img :src="previewImage" alt="预览图" />
              <el-button type="primary" round @click="handlePredict" :loading="predicting">
                <el-icon><MagicStick /></el-icon> 开始识别
              </el-button>
            </div>

            <Transition name="page-fade">
              <div v-if="result" class="result-card">
                <div class="result-header">
                  <el-icon :size="24" color="var(--color-success)"><SuccessFilled /></el-icon>
                  <div>
                    <h3>{{ result.predicted_class }}</h3>
                    <span class="confidence">置信度 {{ result.confidence }}%</span>
                  </div>
                </div>

                <div class="top3-list">
                  <div v-for="(item, i) in result.top3_results" :key="i" class="top3-item">
                    <span class="top3-rank">#{{ i + 1 }}</span>
                    <span class="top3-name">{{ item.class_name }}</span>
                    <div class="top3-bar-bg">
                      <div class="top3-bar" :style="{ width: item.confidence + '%' }"></div>
                    </div>
                    <span class="top3-pct">{{ item.confidence }}%</span>
                  </div>
                </div>

                <div class="result-actions">
                  <el-button v-if="userStore.isLoggedIn" round @click="handleShowFeedback(result)">
                    <el-icon><WarningFilled /></el-icon> 识别有误？反馈
                  </el-button>
                  <span v-else class="hint-text">登录后可提交反馈帮助改进准确度</span>
                </div>
              </div>
            </Transition>
          </div>
        </el-tab-pane>

        <!-- 摄像头识别 -->
        <el-tab-pane label="摄像头识别" name="camera">
          <div class="tab-content camera-content">
            <div v-if="!cameraActive" class="camera-placeholder">
              <el-icon :size="48" color="var(--text-tertiary)"><Camera /></el-icon>
              <p>点击下方按钮开启摄像头</p>
              <el-button type="primary" round size="large" @click="startCamera">
                <el-icon><Camera /></el-icon> 打开摄像头
              </el-button>
              <span class="hint-text">需要允许浏览器访问摄像头权限</span>
            </div>

            <div v-else class="camera-live">
              <video ref="videoElement" autoplay playsinline></video>
              <canvas ref="canvasElement" style="display: none;"></canvas>
              <div class="camera-controls">
                <el-button type="primary" round @click="capturePhoto" :loading="predicting">
                  <el-icon><Camera /></el-icon> 拍照识别
                </el-button>
                <el-button round @click="stopCamera">
                  <el-icon><Close /></el-icon> 关闭
                </el-button>
              </div>
            </div>

            <Transition name="page-fade">
              <div v-if="cameraResult" class="result-card">
                <div class="result-header">
                  <el-icon :size="24" color="var(--color-success)"><SuccessFilled /></el-icon>
                  <div>
                    <h3>{{ cameraResult.predicted_class }}</h3>
                    <span class="confidence">置信度 {{ cameraResult.confidence }}%</span>
                  </div>
                </div>
                <div class="top3-list">
                  <div v-for="(item, i) in cameraResult.top3_results" :key="i" class="top3-item">
                    <span class="top3-rank">#{{ i + 1 }}</span>
                    <span class="top3-name">{{ item.class_name }}</span>
                    <div class="top3-bar-bg">
                      <div class="top3-bar" :style="{ width: item.confidence + '%' }"></div>
                    </div>
                    <span class="top3-pct">{{ item.confidence }}%</span>
                  </div>
                </div>
                <div class="result-actions">
                  <el-button v-if="userStore.isLoggedIn" round @click="handleShowFeedback(cameraResult)">
                    <el-icon><WarningFilled /></el-icon> 识别有误？反馈
                  </el-button>
                </div>
              </div>
            </Transition>
          </div>
        </el-tab-pane>

        <!-- 批量识别 -->
        <el-tab-pane name="batch">
          <template #label>
            <span class="tab-label-with-icon">
              批量识别
              <el-icon v-if="!userStore.isLoggedIn" style="color: var(--text-tertiary); margin-left: 4px;"><Lock /></el-icon>
            </span>
          </template>

          <div class="tab-content">
            <el-alert v-if="!userStore.isLoggedIn" type="warning" :closable="false" show-icon style="margin-bottom: var(--space-5); border-radius: var(--radius-md);">
              <template #title>批量识别需要登录</template>
              <template #default>
                <p style="margin: var(--space-2) 0;">登录后可一次上传最多 10 张图片进行批量识别。</p>
                <el-button type="primary" size="small" round @click="handleShowLogin">立即登录</el-button>
              </template>
            </el-alert>

            <div v-else>
              <el-upload
                class="upload-area"
                drag
                multiple
                :auto-upload="false"
                :on-change="handleBatchFileChange"
                :file-list="batchFiles"
                accept="image/*"
              >
                <div class="upload-inner">
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <p class="upload-text">将图片拖到此处，或<em>点击上传</em></p>
                  <p class="upload-hint">最多上传 10 张图片</p>
                </div>
              </el-upload>

              <el-button
                v-if="batchFiles.length > 0"
                type="primary"
                round
                @click="handleBatchPredict"
                :loading="batchPredicting"
                style="margin-top: var(--space-5);"
              >
                批量识别（{{ batchFiles.length }} 张）
              </el-button>

              <div v-if="batchResults.length > 0" class="batch-results">
                <h3>识别结果</h3>
                <el-table :data="batchResults" stripe>
                  <el-table-column prop="predicted_class" label="分类" />
                  <el-table-column prop="confidence" label="置信度">
                    <template #default="scope">{{ scope.row.confidence }}%</template>
                  </el-table-column>
                  <el-table-column prop="created_at" label="时间" />
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 反馈对话框 -->
    <el-dialog v-model="showFeedbackDialog" title="提交识别反馈" width="460px" :close-on-click-modal="false">
      <el-form :model="feedbackForm" label-width="80px">
        <el-form-item label="识别结果">
          <el-input v-model="feedbackForm.predicted_class" disabled />
        </el-form-item>
        <el-form-item label="正确分类" required>
          <el-input v-model="feedbackForm.correct_class" placeholder="请输入正确的垃圾分类" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="feedbackForm.comment" type="textarea" :rows="3" placeholder="描述识别错误情况（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button round @click="showFeedbackDialog = false">取消</el-button>
        <el-button type="primary" round @click="handleSubmitFeedback" :loading="submittingFeedback">提交反馈</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { predictSingle, predictBatch, submitFeedback } from '@/api/predict'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const userStore = useUserStore()

const currentModel = ref('')
const activeTab = ref('single')
const previewImage = ref('')
const currentFile = ref(null)
const predicting = ref(false)
const result = ref(null)

const cameraActive = ref(false)
const videoElement = ref(null)
const canvasElement = ref(null)
const mediaStream = ref(null)
const cameraResult = ref(null)

const batchFiles = ref([])
const batchPredicting = ref(false)
const batchResults = ref([])

const showFeedbackDialog = ref(false)
const submittingFeedback = ref(false)
const feedbackForm = ref({
  prediction_id: null,
  predicted_class: '',
  correct_class: '',
  comment: ''
})

const handleFileChange = (file) => {
  currentFile.value = file.raw
  previewImage.value = URL.createObjectURL(file.raw)
  result.value = null
}

const handlePredict = async () => {
  if (!currentFile.value) { ElMessage.warning('请先选择图片'); return }
  predicting.value = true
  try {
    const formData = new FormData()
    formData.append('file', currentFile.value)
    result.value = await predictSingle(formData)
    ElMessage.success('识别成功')
  } catch (error) {
    ElMessage.error('识别失败')
  } finally {
    predicting.value = false
  }
}

const handleBatchFileChange = (file, fileList) => {
  if (fileList.length > 10) {
    ElMessage.warning('最多上传10张图片')
    batchFiles.value = fileList.slice(0, 10)
  } else {
    batchFiles.value = fileList
  }
}

const handleBatchPredict = async () => {
  if (batchFiles.value.length === 0) { ElMessage.warning('请先选择图片'); return }
  batchPredicting.value = true
  try {
    const formData = new FormData()
    batchFiles.value.forEach(file => formData.append('files', file.raw))
    batchResults.value = await predictBatch(formData)
    ElMessage.success(`成功识别 ${batchResults.value.length} 张图片`)
  } catch (error) {
    ElMessage.error('批量识别失败')
  } finally {
    batchPredicting.value = false
  }
}

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
    })
    mediaStream.value = stream
    cameraActive.value = true
    cameraResult.value = null
    await new Promise(resolve => setTimeout(resolve, 100))
    if (videoElement.value) videoElement.value.srcObject = stream
    ElMessage.success('摄像头已启动')
  } catch (error) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
  }
}

const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  cameraActive.value = false
  cameraResult.value = null
}

const capturePhoto = async () => {
  if (!videoElement.value || !canvasElement.value) { ElMessage.error('摄像头未就绪'); return }
  predicting.value = true
  cameraResult.value = null
  try {
    const video = videoElement.value
    const canvas = canvasElement.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95))
    const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
    const formData = new FormData()
    formData.append('file', file)
    cameraResult.value = await predictSingle(formData)
    ElMessage.success('识别成功')
  } catch (error) {
    ElMessage.error('识别失败，请重试')
  } finally {
    predicting.value = false
  }
}

onUnmounted(() => stopCamera())

const handleShowFeedback = (predictionResult) => {
  feedbackForm.value = {
    prediction_id: predictionResult.id,
    predicted_class: predictionResult.predicted_class,
    correct_class: '',
    comment: ''
  }
  showFeedbackDialog.value = true
}

const handleSubmitFeedback = async () => {
  if (!feedbackForm.value.correct_class) { ElMessage.warning('请输入正确的分类'); return }
  submittingFeedback.value = true
  try {
    await submitFeedback({
      prediction_id: feedbackForm.value.prediction_id,
      correct_class: feedbackForm.value.correct_class,
      comment: feedbackForm.value.comment
    })
    ElMessage.success('感谢您的反馈！')
    showFeedbackDialog.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交反馈失败')
  } finally {
    submittingFeedback.value = false
  }
}

const handleShowLogin = () => ElMessage.info('请点击右上角"登录"按钮')

const fetchCurrentModel = async () => {
  try {
    const response = await axios.get('/api/model/current')
    currentModel.value = response.data.model_file || ''
  } catch (error) { /* ignore */ }
}

onMounted(() => fetchCurrentModel())
</script>

<style scoped>
.classify-page {
  padding: var(--space-8) var(--space-6);
  max-width: 860px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.classify-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.tab-content {
  padding-top: var(--space-4);
}

/* Upload Area */
.upload-area :deep(.el-upload-dragger) {
  border-radius: var(--radius-xl) !important;
  padding: var(--space-10) var(--space-6) !important;
}

.upload-inner {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: var(--color-primary-light);
  margin-bottom: var(--space-3);
}

.upload-text {
  font-size: var(--text-md);
  color: var(--text-secondary);
}

.upload-text em {
  color: var(--color-primary);
  font-style: normal;
  font-weight: var(--font-medium);
}

.upload-hint {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--space-2);
}

/* Preview */
.preview-area {
  text-align: center;
  margin-top: var(--space-6);
}

.preview-area img {
  max-width: 360px;
  max-height: 360px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-5);
  display: block;
  margin-left: auto;
  margin-right: auto;
}

/* Result Card */
.result-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  margin-top: var(--space-6);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
}

.result-header h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.confidence {
  font-size: var(--text-sm);
  color: var(--color-primary);
  font-weight: var(--font-medium);
}

/* Top 3 */
.top3-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.top3-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.top3-rank {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--text-tertiary);
  min-width: 28px;
}

.top3-name {
  font-size: var(--text-base);
  color: var(--text-primary);
  min-width: 120px;
  font-weight: var(--font-medium);
}

.top3-bar-bg {
  flex: 1;
  height: 8px;
  background: var(--border-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.top3-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: var(--radius-full);
  transition: width 0.6s ease;
}

.top3-pct {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  min-width: 50px;
  text-align: right;
}

.result-actions {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-secondary);
}

.hint-text {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* Camera */
.camera-content {
  text-align: center;
}

.camera-placeholder {
  padding: var(--space-12) var(--space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.camera-placeholder p {
  color: var(--text-tertiary);
  font-size: var(--text-md);
}

.camera-live video {
  width: 100%;
  max-width: 600px;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}

.camera-controls {
  margin-top: var(--space-5);
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

/* Batch */
.batch-results {
  margin-top: var(--space-6);
}

.batch-results h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

/* Responsive */
@media (max-width: 768px) {
  .classify-page {
    padding: var(--space-4);
  }
  .classify-card {
    padding: var(--space-4);
  }
  .top3-name {
    min-width: 80px;
  }
  .preview-area img {
    max-width: 100%;
  }
}
</style>

<template>
  <div class="classify">
    <el-card>
      <template #header>
        <h2>智能垃圾识别</h2>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 单张识别 -->
        <el-tab-pane label="单张识别" name="single">
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept="image/*"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将图片拖到此处，或<em>点击上传</em>
            </div>
          </el-upload>

          <div v-if="previewImage" class="preview-section">
            <img :src="previewImage" alt="预览图" />
            <el-button type="primary" @click="handlePredict" :loading="predicting">
              开始识别
            </el-button>
          </div>

          <div v-if="result" class="result-section">
            <el-result icon="success" title="识别完成">
              <template #sub-title>
                <div class="result-details">
                  <h3>识别结果：{{ result.predicted_class }}</h3>
                  <p>置信度：{{ result.confidence }}%</p>

                  <el-divider />

                  <h4>Top 3 预测结果：</h4>
                  <el-table :data="result.top3_results" style="width: 100%">
                    <el-table-column prop="class_name" label="分类" />
                    <el-table-column prop="confidence" label="置信度">
                      <template #default="scope">
                        {{ scope.row.confidence }}%
                      </template>
                    </el-table-column>
                  </el-table>

                  <div v-if="userStore.isLoggedIn" style="margin-top: 20px;">
                    <el-button type="warning" @click="handleShowFeedback(result)">
                      识别有误？提交反馈
                    </el-button>
                  </div>
                  <div v-else style="margin-top: 20px; color: #999; font-size: 14px;">
                    登录后可提交反馈帮助改进识别准确度
                  </div>
                </div>
              </template>
            </el-result>
          </div>
        </el-tab-pane>

        <!-- 摄像头识别 -->
        <el-tab-pane label="摄像头识别" name="camera">
          <div class="camera-section">
            <div v-if="!cameraActive" class="camera-start">
              <el-button type="primary" size="large" @click="startCamera">
                <el-icon><Camera /></el-icon>
                打开摄像头
              </el-button>
              <p style="margin-top: 10px; color: #999;">需要允许浏览器访问摄像头权限</p>
            </div>

            <div v-else class="camera-active">
              <video ref="videoElement" autoplay playsinline></video>
              <canvas ref="canvasElement" style="display: none;"></canvas>

              <div class="camera-controls">
                <el-button type="primary" @click="capturePhoto" :loading="predicting">
                  <el-icon><Camera /></el-icon>
                  拍照识别
                </el-button>
                <el-button @click="stopCamera">
                  <el-icon><Close /></el-icon>
                  关闭摄像头
                </el-button>
              </div>
            </div>

            <div v-if="cameraResult" class="result-section">
              <el-result icon="success" title="识别完成">
                <template #sub-title>
                  <div class="result-details">
                    <h3>识别结果：{{ cameraResult.predicted_class }}</h3>
                    <p>置信度：{{ cameraResult.confidence }}%</p>

                    <el-divider />

                    <h4>Top 3 预测结果：</h4>
                    <el-table :data="cameraResult.top3_results" style="width: 100%">
                      <el-table-column prop="class_name" label="分类" />
                      <el-table-column prop="confidence" label="置信度">
                        <template #default="scope">
                          {{ scope.row.confidence }}%
                        </template>
                      </el-table-column>
                    </el-table>

                    <div v-if="userStore.isLoggedIn" style="margin-top: 20px;">
                      <el-button type="warning" @click="handleShowFeedback(cameraResult)">
                        识别有误？提交反馈
                      </el-button>
                    </div>
                    <div v-else style="margin-top: 20px; color: #999; font-size: 14px;">
                      登录后可提交反馈帮助改进识别准确度
                    </div>
                  </div>
                </template>
              </el-result>
            </div>
          </div>
        </el-tab-pane>

        <!-- 批量识别 -->
        <el-tab-pane name="batch">
          <template #label>
            <span>
              批量识别
              <el-tooltip v-if="!userStore.isLoggedIn" content="需要登录后使用" placement="top">
                <el-icon style="color: #909399; margin-left: 4px;"><Lock /></el-icon>
              </el-tooltip>
            </span>
          </template>

          <el-alert
            v-if="!userStore.isLoggedIn"
            title="批量识别需要登录"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <template #default>
              <p>批量识别功能需要登录后才能使用，登录后可以：</p>
              <ul style="margin: 10px 0; padding-left: 20px;">
                <li>一次上传最多10张图片</li>
                <li>保存识别历史记录</li>
                <li>查看个人数据统计</li>
              </ul>
              <el-button type="primary" size="small" @click="handleShowLogin">
                立即登录
              </el-button>
            </template>
          </el-alert>

          <div v-else>
            <el-upload
              class="upload-demo"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleBatchFileChange"
              :file-list="batchFiles"
              accept="image/*"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将图片拖到此处，或<em>点击上传</em><br>
                <span style="font-size: 12px; color: #999;">最多上传10张图片</span>
              </div>
            </el-upload>

            <el-button
              v-if="batchFiles.length > 0"
              type="primary"
              @click="handleBatchPredict"
              :loading="batchPredicting"
              style="margin-top: 20px;"
            >
              批量识别（{{ batchFiles.length }}张）
            </el-button>

            <div v-if="batchResults.length > 0" class="batch-results">
              <h3>识别结果</h3>
              <el-table :data="batchResults" style="width: 100%">
                <el-table-column prop="predicted_class" label="分类" />
                <el-table-column prop="confidence" label="置信度">
                  <template #default="scope">
                    {{ scope.row.confidence }}%
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="识别时间" />
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 反馈对话框 -->
    <el-dialog
      v-model="showFeedbackDialog"
      title="提交识别反馈"
      width="500px"
    >
      <el-form :model="feedbackForm" label-width="100px">
        <el-form-item label="识别结果">
          <el-input v-model="feedbackForm.predicted_class" disabled />
        </el-form-item>
        <el-form-item label="正确分类" required>
          <el-input
            v-model="feedbackForm.correct_class"
            placeholder="请输入正确的垃圾分类"
          />
        </el-form-item>
        <el-form-item label="备注说明">
          <el-input
            v-model="feedbackForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请描述识别错误的情况（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFeedbackDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitFeedback" :loading="submittingFeedback">
          提交反馈
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import { predictSingle, predictBatch, submitFeedback } from '@/api/predict'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const activeTab = ref('single')
const previewImage = ref('')
const currentFile = ref(null)
const predicting = ref(false)
const result = ref(null)

// 摄像头识别相关
const cameraActive = ref(false)
const videoElement = ref(null)
const canvasElement = ref(null)
const mediaStream = ref(null)
const cameraResult = ref(null)

// 批量识别相关
const batchFiles = ref([])
const batchPredicting = ref(false)
const batchResults = ref([])

// 反馈相关
const showFeedbackDialog = ref(false)
const submittingFeedback = ref(false)
const feedbackForm = ref({
  prediction_id: null,
  predicted_class: '',
  correct_class: '',
  comment: ''
})

// 处理文件选择
const handleFileChange = (file) => {
  currentFile.value = file.raw
  previewImage.value = URL.createObjectURL(file.raw)
  result.value = null
}

// 处理识别
const handlePredict = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

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

// 处理批量文件选择
const handleBatchFileChange = (file, fileList) => {
  if (fileList.length > 10) {
    ElMessage.warning('最多上传10张图片')
    batchFiles.value = fileList.slice(0, 10)
  } else {
    batchFiles.value = fileList
  }
}

// 处理批量识别
const handleBatchPredict = async () => {
  if (batchFiles.value.length === 0) {
    ElMessage.warning('请先选择图片')
    return
  }

  batchPredicting.value = true
  try {
    const formData = new FormData()
    batchFiles.value.forEach(file => {
      formData.append('files', file.raw)
    })

    batchResults.value = await predictBatch(formData)
    ElMessage.success(`成功识别 ${batchResults.value.length} 张图片`)
  } catch (error) {
    ElMessage.error('批量识别失败')
  } finally {
    batchPredicting.value = false
  }
}

// 启动摄像头
const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment', // 优先使用后置摄像头
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    })

    mediaStream.value = stream
    cameraActive.value = true
    cameraResult.value = null

    // 等待 DOM 更新
    await new Promise(resolve => setTimeout(resolve, 100))

    if (videoElement.value) {
      videoElement.value.srcObject = stream
    }

    ElMessage.success('摄像头已启动')
  } catch (error) {
    console.error('启动摄像头失败:', error)
    ElMessage.error('无法访问摄像头，请检查权限设置')
  }
}

// 关闭摄像头
const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  cameraActive.value = false
  cameraResult.value = null
}

// 拍照并识别
const capturePhoto = async () => {
  if (!videoElement.value || !canvasElement.value) {
    ElMessage.error('摄像头未就绪')
    return
  }

  predicting.value = true
  cameraResult.value = null

  try {
    // 获取视频尺寸
    const video = videoElement.value
    const canvas = canvasElement.value

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // 绘制当前帧到 canvas
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // 将 canvas 转换为 Blob
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95))

    // 创建 File 对象
    const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })

    // 上传识别
    const formData = new FormData()
    formData.append('file', file)

    cameraResult.value = await predictSingle(formData)
    ElMessage.success('识别成功')
  } catch (error) {
    console.error('拍照识别失败:', error)
    ElMessage.error('识别失败，请重试')
  } finally {
    predicting.value = false
  }
}

// 组件卸载时关闭摄像头
onUnmounted(() => {
  stopCamera()
})

// 显示反馈对话框
const handleShowFeedback = (predictionResult) => {
  feedbackForm.value = {
    prediction_id: predictionResult.id,
    predicted_class: predictionResult.predicted_class,
    correct_class: '',
    comment: ''
  }
  showFeedbackDialog.value = true
}

// 提交反馈
const handleSubmitFeedback = async () => {
  if (!feedbackForm.value.correct_class) {
    ElMessage.warning('请输入正确的分类')
    return
  }

  submittingFeedback.value = true
  try {
    await submitFeedback({
      prediction_id: feedbackForm.value.prediction_id,
      correct_class: feedbackForm.value.correct_class,
      comment: feedbackForm.value.comment
    })
    ElMessage.success('感谢您的反馈！这将帮助我们改进识别准确度')
    showFeedbackDialog.value = false
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('提交反馈失败，请重试')
    }
  } finally {
    submittingFeedback.value = false
  }
}

// 显示登录对话框
const handleShowLogin = () => {
  ElMessage.info('请点击右上角的"登录"按钮进行登录')
}
</script>

<style scoped>
.classify {
  max-width: 800px;
  margin: 0 auto;
}

.preview-section {
  margin-top: 20px;
  text-align: center;
}

.preview-section img {
  max-width: 400px;
  max-height: 400px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.result-section {
  margin-top: 30px;
}

.result-details h3 {
  font-size: 24px;
  color: #409eff;
  margin-bottom: 10px;
}

.batch-results {
  margin-top: 30px;
}

/* 摄像头相关样式 */
.camera-section {
  text-align: center;
}

.camera-start {
  padding: 60px 20px;
}

.camera-active video {
  width: 100%;
  max-width: 640px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.camera-controls {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}
</style>

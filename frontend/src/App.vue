<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <div class="logo">
        <img src="/gym.svg" alt="Logo" />
        <span>OBGym 预约系统</span>
      </div>
      <div class="nav-menu">
        <div class="nav-item" :class="{ active: currentNav === 'booking' }" @click="currentNav = 'booking'">
          <el-icon>
            <Calendar />
          </el-icon>
          <span>预约</span>
        </div>
        <div class="nav-item" :class="{ active: currentNav === 'jobs' }" @click="currentNav = 'jobs'">
          <el-icon>
            <List />
          </el-icon>
          <span>任务</span>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 预约页面 -->
      <div v-if="currentNav === 'booking'">
        <!-- 原有的预约相关内容 -->
        <div class="progress-card">
          <div class="card-header">
            <h2>预约进度</h2>
            <div class="progress-info">
              <template v-if="currentStep > 0">
                <el-tag type="success" class="progress-tag">
                  <span class="tag-label">当前选择：</span>
                  <template v-if="currentStep === 1">
                    {{ store.selectedAccount }}
                  </template>
                  <template v-if="currentStep === 2">
                    {{ store.selectedCampus?.name }}
                  </template>
                  <template v-if="currentStep === 3">
                    {{ store.selectedFacility?.name }}
                  </template>
                </el-tag>
              </template>
            </div>
          </div>
          <div class="progress-steps">
            <div v-for="(step, index) in steps" :key="index" class="progress-step" :class="{
              completed: index < currentStep,
              current: index === currentStep,
              clickable: index < currentStep,
            }" @click="index < currentStep && handleStepClick(index)">
              <div class="step-circle">
                <el-icon v-if="index < currentStep"><Select /></el-icon>
                <el-icon v-else-if="index === currentStep">
                  <Loading />
                </el-icon>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="step-line" v-if="index < steps.length - 1">
                <div class="line-inner"></div>
              </div>
              <div class="step-label">{{ getStepLabel(index) }}</div>
            </div>
          </div>
        </div>

        <!-- 内容卡片 -->
        <div class="content-card" v-loading="store.loading">
          <!-- 第一步：选择用户 -->
          <transition name="el-fade-in-linear" mode="out-in">
            <div v-if="currentStep === 0" key="accounts" class="card-content">
              <div class="card-header">
                <h2>选择用户</h2>
                <div class="header-actions">
                  <el-button type="primary" @click="handleAddAccount">
                    <el-icon>
                      <Plus />
                    </el-icon>添加用户
                  </el-button>
                  <el-button @click="refreshAccounts">
                    <el-icon>
                      <Refresh />
                    </el-icon>刷新
                  </el-button>
                </div>
              </div>
              <div class="accounts-grid">
                <div v-for="account in sortedAccounts" :key="account.account" class="account-card"
                  @click="selectAccount(account)">
                  <div class="account-icon">
                    <el-icon>
                      <User />
                    </el-icon>
                  </div>
                  <div class="account-info">
                    <span class="account-name">{{ account.account }}</span>
                  </div>
                  <div class="account-actions">
                    <el-tooltip content="删除账户" placement="top">
                      <div class="action-button delete" @click.stop="handleDeleteAccount(account)">
                        <el-icon>
                          <Delete />
                        </el-icon>
                      </div>
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </div>

            <!-- 第二步：选择校区 -->
            <div v-else-if="currentStep === 1" key="campus" class="card-content">
              <div class="card-header">
                <h2>选择校区</h2>
              </div>
              <div class="campus-grid">
                <div v-for="campus in sortedCampuses" :key="campus.code" class="campus-card"
                  @click="selectCampus(campus)">
                  <div class="campus-icon">
                    <el-icon>
                      <School />
                    </el-icon>
                  </div>
                  <span class="campus-name">{{ campus.name }}</span>
                </div>
              </div>
            </div>

            <!-- 第三步：选择场馆 -->
            <div v-else-if="currentStep === 2" key="facility" class="card-content">
              <div class="card-header">
                <h2>选择场馆</h2>
              </div>
              <div class="facility-grid">
                <div v-for="facility in sortedFacilities" :key="facility.serviceid" class="facility-card"
                  @click="selectFacility(facility)">
                  <div class="facility-icon">
                    <el-icon>
                      <OfficeBuilding />
                    </el-icon>
                  </div>
                  <span class="facility-name">{{ facility.name }}</span>
                </div>
              </div>
            </div>

            <!-- 第四步：选择区域 -->
            <div v-else-if="currentStep === 3" key="area" class="card-content">
              <div class="card-header">
                <h2>选择区域</h2>
                <div class="header-actions">
                  <div class="date-selector">
                    <el-date-picker v-model="selectedDate" type="date" :disabled-date="disabledDate" format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD" placeholder="选择日��" :clearable="false" @change="handleDateChange" />
                  </div>
                  <el-button @click="refreshArea">
                    <el-icon>
                      <Refresh />
                    </el-icon>刷新
                  </el-button>
                </div>
              </div>
              <div class="areas-container">
                <div v-for="group in sortedAreas" :key="group.timeno" class="time-group">
                  <div class="time-header">
                    <el-icon>
                      <Timer />
                    </el-icon>
                    <span>时段 {{ group.timeno }}</span>
                  </div>
                  <div class="area-grid">
                    <div v-for="area in group.areas" :key="area.areaid" class="area-card" @click="showBookDialog(area)">
                      <div class="area-icon">
                        <el-icon>
                          <Location />
                        </el-icon>
                      </div>
                      <span class="area-name">{{ area.sname }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- 任务页面 -->
      <div v-else-if="currentNav === 'jobs'">
        <div class="content-card">
          <div class="card-header">
            <h2>任务列表</h2>
            <div class="header-actions">
              <el-button @click="refreshJobs">
                <el-icon>
                  <Refresh />
                </el-icon>刷新
              </el-button>
            </div>
          </div>
          <div class="jobs-list">
            <div v-if="jobs.length === 0" class="empty-jobs">暂无任务</div>
            <div v-else class="job-items">
              <div v-for="job in paginatedJobs" :key="job.job_id" class="job-card" @click="showJobInfo(job.job_id)">
                <div class="job-icon" :class="{ 'main-job': job.job_level === 0 }">
                  <el-icon>
                    <Timer />
                  </el-icon>
                </div>
                <div class="job-info">
                  <div class="job-header">
                    <div class="job-description">
                      <el-tag size="small" class="job-type-tag" :type="getJobTypeTagType(job.job_level)">
                        {{ getJobTypeText(job.job_type) }}
                      </el-tag>
                      <span class="description-text">{{
                        job.description
                        }}</span>
                    </div>
                    <el-tag :type="getStatusType(job.job_status)" size="small">
                      {{ getStatusText(job.job_status) }}
                    </el-tag>
                  </div>
                  <div class="job-time">
                    <span>创建时间：{{ formatJobTime(job.created_at) }}</span>
                    <span class="time-separator">|</span>
                    <span>更新时间：{{ formatJobTime(job.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分页器 -->
            <div class="pagination-container">
              <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="jobs.length"
                layout="prev, pager, next" @current-change="handlePageChange" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加用户对话框 -->
    <el-dialog v-model="addAccountDialogVisible" title="添加用户" width="400px" :close-on-click-modal="false"
      class="custom-dialog" @open="handleDialogOpen">
      <el-form :model="newAccount" label-width="80px" @submit.prevent="confirmAddAccount">
        <el-form-item label="账号">
          <el-input v-model="newAccount.account" placeholder="请输入账号" ref="accountInput" @keyup.enter="focusPassword" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newAccount.password" type="password" placeholder="请输入密码" ref="passwordInput"
            @keyup.enter="confirmAddAccount" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addAccountDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddAccount">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预约弹窗 -->
    <el-dialog v-model="bookDialogVisible" title="场地预约" width="400px" :close-on-click-modal="false"
      class="custom-dialog" @keyup.enter="handleBookArea">
      <div class="area-info">
        <div class="info-item">
          <span class="label">场地名称：</span>
          <span>{{ selectedArea?.sname }}</span>
        </div>
        <div class="info-item">
          <span class="label">预约日期：</span>
          <span>{{ selectedArea?.sdate }}</span>
        </div>
        <div class="info-item">
          <span class="label">时段号：</span>
          <span>{{ selectedArea?.timeno }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bookDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleBookArea">仅预约</el-button>
          <el-button type="danger" @click="handleBookAndPayArea">经费预约</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加任务详情弹窗 -->
    <el-dialog v-model="jobInfoDialogVisible" title="任务详情" width="500px" :close-on-click-modal="false"
      class="custom-dialog" @keyup.enter="jobInfoDialogVisible = false">
      <div v-if="selectedJobInfo" class="job-info-content">
        <div class="info-item">
          <span class="label">任务类型：</span>
          <el-tag :type="getJobTypeTagType(selectedJobInfo.job_level)">
            {{ getJobTypeText(selectedJobInfo.job_type) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">任务级别：</span>
          <el-tag :type="getJobTypeTagType(selectedJobInfo.job_level)">
            {{ getJobLevelText(selectedJobInfo.job_level) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">任务状态：</span>
          <el-tag :type="getStatusType(selectedJobInfo.status)">
            {{ getStatusText(selectedJobInfo.status) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">创建时间：</span>
          <span>{{ selectedJobInfo.created_at }}</span>
        </div>
        <div class="info-item">
          <span class="label">更新时间：</span>
          <span>{{ selectedJobInfo.updated_at }}</span>
        </div>
        <div class="info-item">
          <span class="label">失败次数：</span>
          <span>{{ selectedJobInfo.failed_count }}</span>
        </div>
        <div class="info-item">
          <span class="label">任务描述：</span>
          <span>{{ selectedJobInfo.description }}</span>
        </div>

        <div v-if="selectedJobInfo.task_todo" class="info-item">
          <span class="label">下次执行：</span>
          <el-tag type="warning">
            {{ selectedJobInfo.task_todo.date }}
          </el-tag>
        </div>

        <div class="result-list">
          <h3>执行记录</h3>
          <div class="timeline-container">
            <el-timeline>
              <el-timeline-item v-for="result in sortedResults" :key="result.created_at"
                :type="result.success ? 'success' : 'danger'" :timestamp="result.created_at">
                <div class="timeline-content">
                  <div class="message">{{ result.message || "执行完成" }}</div>
                  <div v-if="shouldShowData(result)" class="data-info">
                    <pre>{{ JSON.stringify(result.data, null, 2) }}</pre>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="danger" @click="handleRemoveJob" :disabled="selectedJobInfo?.job_level === 0">
            删除任务
          </el-button>
          <el-button @click="jobInfoDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from "vue";
import { useGymStore } from "./store";
import {
  User,
  School,
  OfficeBuilding,
  Location,
  Plus,
  Refresh,
  Delete,
  Timer,
  Loading,
  Select,
  Calendar,
  List,
} from "@element-plus/icons-vue";
import type { Account, GymCampus, GymFacility, GymArea } from "./types";
import { ElMessage, ElMessageBox } from "element-plus";

const store = useGymStore();
const currentStep = ref(0);
const addAccountDialogVisible = ref(false);
const newAccount = ref({ account: "", password: "" });
const steps = ["选择用户", "选择校区", "选择场馆", "选择区域"];
const currentNav = ref("booking");
const jobs = ref<
  {
    job_id: string;
    description: string;
    created_at: string;
    updated_at: string;
    job_status: number;
    job_level: number;
    job_type: number;
  }[]
>([]);
const bookDialogVisible = ref(false);
const selectedArea = ref<GymArea | null>(null);
const currentPage = ref(1);
const pageSize = ref(10);
const jobInfoDialogVisible = ref(false);
const selectedJobInfo = ref<JobInfo | null>(null);

// 修改 ref 的类型定��
const accountInput = ref<any>(null);
const passwordInput = ref<any>(null);

onMounted(async () => {
  await Promise.all([store.fetchAccounts(), refreshJobs()]);
});

const handleStepClick = (step: number) => {
  if (step < currentStep.value) {
    currentStep.value = step;
  }
};

const refreshAccounts = async () => {
  try {
    await store.fetchAccounts();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "刷新失败");
  }
};

const selectAccount = async (account: Account) => {
  try {
    store.loading = true; // 开始加载
    // 先尝试刷新账户状态
    const response = await fetch(`/api/accounts/${account.account}/renew`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    await refreshAccounts(); // 刷新账户列表

    // 只有在账户刷新成功后才获取校区列表
    try {
      await store.fetchCampus(account.account);
      currentStep.value = 1;
    } catch (error) {
      ElMessage.error(
        error instanceof Error ? error.message : "获取校区列表失败"
      );
    }
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "账户状态更新失败"
    );
  } finally {
    store.loading = false; // 结束加载
  }
};

const selectCampus = async (campus: GymCampus) => {
  try {
    await store.fetchFacility(campus);
    currentStep.value = 2;
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "获取场馆列表失败"
    );
  }
};

const selectFacility = async (facility: GymFacility) => {
  try {
    await store.fetchArea(facility, selectedDate.value);
    currentStep.value = 3;
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "获取区域列表失败"
    );
  }
};

const handleDateChange = async () => {
  if (selectedDate.value && store.selectedFacility) {
    try {
      await store.fetchArea(store.selectedFacility, selectedDate.value);
    } catch (error) {
      ElMessage.error(
        error instanceof Error ? error.message : "获取区域列表失败"
      );
    }
  }
};

const handleDialogOpen = () => {
  // 使用较短延时确保 DOM 已完全渲染
  setTimeout(() => {
    accountInput.value?.focus();
  }, 100);
};

const handleAddAccount = () => {
  newAccount.value = { account: "", password: "" };
  addAccountDialogVisible.value = true;
};

const confirmAddAccount = async () => {
  if (!newAccount.value.account || !newAccount.value.password) {
    ElMessage.warning("请输入账号和密码");
    return;
  }
  try {
    await store.addAccount(newAccount.value.account, newAccount.value.password);
    addAccountDialogVisible.value = false;
    ElMessage.success("添加成功");
    await refreshAccounts();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "添加失败");
  }
};

const handleDeleteAccount = async (account: Account) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除账户 ${account.account} 吗？`,
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await store.deleteAccount(account.account);
    ElMessage.success("删除成功");
    await refreshAccounts();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error instanceof Error ? error.message : "删除失败");
    }
  }
};

const handleRenewAccount = async (account: Account) => {
  try {
    const response = await fetch(`/api/accounts/${account.account}/renew`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    ElMessage.success("账户更新成功");
    await refreshAccounts(); // 刷新账户列表以显示最新状态
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "更新失败");
  }
};

const getStepLabel = (index: number) => {
  if (index > currentStep.value) {
    return steps[index];
  }

  switch (index) {
    case 0:
      return currentStep.value > 0 ? store.selectedAccount : "选择用户";
    case 1:
      return currentStep.value > 1 ? store.selectedCampus?.name : "选择校区";
    case 2:
      return currentStep.value > 2 ? store.selectedFacility?.name : "选择场馆";
    case 3:
      return "选择区域";
    default:
      return steps[index];
  }
};

const formatDate = (date: Date): string => {
  // 转换为中国时区
  const chinaDate = new Date(
    date.toLocaleString("en-US", { timeZone: "Asia/Shanghai" })
  );
  const year = chinaDate.getFullYear();
  const month = String(chinaDate.getMonth() + 1).padStart(2, "0");
  const day = String(chinaDate.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const selectedDate = ref(formatDate(new Date()));

const sortedAccounts = computed(() => {
  return [...store.accounts].sort((a, b) => a.account.localeCompare(b.account));
});

const sortedCampuses = computed(() => {
  return [...store.campuses].sort((a, b) => a.name.localeCompare(b.name));
});

const sortedFacilities = computed(() => {
  return [...store.facilities].sort((a, b) => a.name.localeCompare(b.name));
});

const sortedAreas = computed(() => {
  return [...store.areas]
    .sort((a, b) => {
      // 先按时段号排序
      const timeCompare = a.timeno.localeCompare(b.timeno);
      if (timeCompare !== 0) return timeCompare;

      // 如果时段号相同，则按区域名称排序
      if (a.areas && b.areas) {
        return a.areas[0]?.sname.localeCompare(b.areas[0]?.sname) || 0;
      }
      return 0;
    })
    .map((group) => ({
      ...group,
      areas: group.areas
        ? [...group.areas].sort((a, b) => a.sname.localeCompare(b.sname))
        : [],
    }));
});

const sortedJobs = computed(() => {
  return [...jobs.value].sort(
    (a, b) =>
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  );
});

const refreshJobs = async () => {
  try {
    const response = await fetch("/api/jobs");
    if (!response.ok) {
      throw new Error(await response.text());
    }
    jobs.value = await response.json();
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "获取任务列表失败"
    );
  }
};

const formatJobTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

const showBookDialog = (area: GymArea) => {
  selectedArea.value = area;
  bookDialogVisible.value = true;
};

const handleBookArea = async () => {
  if (!selectedArea.value || !store.selectedAccount) {
    ElMessage.warning("请选择场地和账号");
    return;
  }

  try {
    const response = await fetch(`/api/area/book`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sname: selectedArea.value.sname,
        sdate: selectedArea.value.sdate,
        timeno: selectedArea.value.timeno,
        serviceid: selectedArea.value.serviceid,
        areaid: selectedArea.value.areaid,
        stockid: selectedArea.value.stockid,
        account: store.selectedAccount,
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    ElMessage.success("预约任务创建成功");
    bookDialogVisible.value = false;
    currentNav.value = "jobs"; // 跳转到任务页面
    await refreshJobs(); // 刷新任务列表
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "预约失败");
  }
};

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return sortedJobs.value.slice(start, end);
});

const handlePageChange = (page: number) => {
  currentPage.value = page;
};

const showJobInfo = async (jobId: string) => {
  try {
    const response = await fetch(`/api/jobs/${jobId}`);
    if (!response.ok) {
      throw new Error(await response.text());
    }
    selectedJobInfo.value = await response.json();
    jobInfoDialogVisible.value = true;
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "获取任务详情失败"
    );
  }
};

const getStatusType = (status: number) => {
  switch (status) {
    case 0:
      return "info"; // PENDING
    case 1:
      return "warning"; // RUNNING
    case 2:
      return "warning"; // RETRY
    case 3:
      return "success"; // SUCCESS
    case 4:
      return "danger"; // FAILED
    default:
      return "info";
  }
};

const getStatusText = (status: number) => {
  switch (status) {
    case 0:
      return "等待中";
    case 1:
      return "执行中";
    case 2:
      return "重试中";
    case 3:
      return "成功";
    case 4:
      return "失败";
    default:
      return "未知";
  }
};

const handleRemoveJob = async () => {
  if (!selectedJobInfo.value) return;

  try {
    await ElMessageBox.confirm("确定要删除该任务吗?", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    const response = await fetch(`/api/jobs/${selectedJobInfo.value.job_id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    ElMessage.success("任务删除成功");
    jobInfoDialogVisible.value = false;
    await refreshJobs(); // 刷新任务列表
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error instanceof Error ? error.message : "删除失败");
    }
  }
};

const refreshArea = async () => {
  if (store.selectedFacility) {
    try {
      await store.fetchArea(store.selectedFacility, selectedDate.value);
      ElMessage.success("刷新成功");
    } catch (error) {
      ElMessage.error(error instanceof Error ? error.message : "刷新失败");
    }
  }
};

// 添加新的类型定义
interface TaskTodo {
  task_id: string;
  date: string;
}

interface JobInfo {
  status: number;
  job_level: number;
  job_id: string;
  description: string;
  result: TaskResult[];
  failed_count: number;
  created_at: string;
  task_todo?: TaskTodo; // 使用可选属性
}

const disabledDate = (time: Date) => {
  // 转换为中国时区的时间
  const chinaDate = new Date(
    time.toLocaleString("en-US", { timeZone: "Asia/Shanghai" })
  );

  // 获取中国时区的今天开始时间（0点0分0秒）
  const today = new Date(
    new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" })
  );
  today.setHours(0, 0, 0, 0);

  // 获取30天后的日期作为最大可选日期
  const maxDate = new Date(today);
  maxDate.setDate(maxDate.getDate() + 30);

  return (
    chinaDate.getTime() < today.getTime() ||
    chinaDate.getTime() > maxDate.getTime()
  );
};

// 修改聚焦密码框的方法
const focusPassword = () => {
  passwordInput.value?.focus();
};

// 添加获取任务类型文本的方法
const getJobTypeText = (type: number) => {
  switch (type) {
    case 0:
      return "未知";
    case 1:
      return "账户更新";
    case 2:
      return "场地预约";
    case 3:
      return "经费预约";
    default:
      return "未知";
  }
};

// 添加排序的计算属性
const sortedResults = computed(() => {
  if (!selectedJobInfo.value?.result) return [];
  return [...selectedJobInfo.value.result].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
});

// 添加获取任务级别文本的方法
const getJobLevelText = (level: number) => {
  switch (level) {
    case 0:
      return "系统任务";
    case 1:
      return "用户任务";
    default:
      return "未知";
  }
};

const shouldShowData = (result: TaskResult) => {
  // 如果任务成功
  if (result.success) {
    // 当数据为空对象时显示，为null时不显示
    return result.data !== null && Object.keys(result.data).length >= 0;
  }
  // 任务失败时不显示数据
  return false;
};

const getJobTypeTagType = (level: number) => {
  switch (level) {
    case 0:
      return "danger"; // 系统任务用红色
    case 1:
      return "primary"; // 用户任务用蓝色
    default:
      return "info";
  }
};

const handleBookAndPayArea = async () => {
  if (!selectedArea.value || !store.selectedAccount) {
    ElMessage.warning("请选择场地和账号");
    return;
  }

  try {
    const response = await fetch(`/api/area/book_and_pay`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sname: selectedArea.value.sname,
        sdate: selectedArea.value.sdate,
        timeno: selectedArea.value.timeno,
        serviceid: selectedArea.value.serviceid,
        areaid: selectedArea.value.areaid,
        stockid: selectedArea.value.stockid,
        account: store.selectedAccount,
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    ElMessage.success("预约任务创建成功");
    bookDialogVisible.value = false;
    currentNav.value = "jobs"; // 跳转到任务页面
    await refreshJobs(); // 刷新任务列表
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "预约失败");
  }
};
</script>
<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.navbar {
  height: 64px;
  background: white;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo img {
  height: 32px;
}

.logo span {
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(45deg,
      var(--el-color-primary),
      var(--el-color-success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.main-content {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.progress-card,
.content-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 进度条样式 */
.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
  margin-top: 40px;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  border: 2px solid #dcdfe6;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  color: #909399;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.step-line {
  position: absolute;
  top: 20px;
  left: calc(50% + 20px);
  right: calc(-50% + 20px);
  height: 2px;
  background-color: #dcdfe6;
  z-index: 1;
}

.line-inner {
  width: 0;
  height: 100%;
  background-color: var(--el-color-success);
  transition: width 0.4s ease-in-out;
}

.step-label {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
  transition: all 0.3s ease;
}

.progress-step.completed .step-circle {
  background-color: var(--el-color-success);
  border-color: var(--el-color-success);
  color: white;
}

.progress-step.completed .step-label {
  color: var(--el-color-success);
}

.progress-step.completed .line-inner {
  width: 100%;
}

.progress-step.current .step-circle {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
}

.progress-step.current .step-label {
  color: var(--el-color-primary);
  font-weight: bold;
}

.progress-step.clickable {
  cursor: pointer;
}

.progress-step.clickable:hover .step-circle {
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.2);
}

/* 网格布局 */
.accounts-grid,
.campus-grid,
.facility-grid,
.area-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  padding: 10px;
}

/* 卡片样式 */
.account-card,
.campus-card,
.facility-card,
.area-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  position: relative;
}

.account-card:hover,
.campus-card:hover,
.facility-card:hover,
.area-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.account-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.account-card.disabled .account-info,
.account-card.disabled .account-icon {
  opacity: 0.6;
}

.account-card.disabled .delete-icon {
  opacity: 1;
  cursor: pointer;
}

.account-icon,
.campus-icon,
.facility-icon,
.area-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: var(--el-color-primary-light-9);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--el-color-primary);
}

.account-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-right: 100px;
}

.account-name {
  font-weight: 500;
  color: #303133;
}

.account-status {
  font-size: 12px;
  color: #909399;
}

.account-status.available {
  color: var(--el-color-success);
}

.delete-icon {
  position: absolute;
  right: 16px;
  color: var(--el-color-danger);
  font-size: 18px;
  opacity: 1;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
  z-index: 1;
}

.delete-icon:hover {
  background-color: var(--el-color-danger-light-9);
  transform: scale(1.1);
}

/* 时间组样式 */
.time-group {
  margin-bottom: 32px;
}

.time-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #606266;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 0 16px;
  }

  .accounts-grid,
  .campus-grid,
  .facility-grid,
  .area-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .step-circle {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .step-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {

  .accounts-grid,
  .campus-grid,
  .facility-grid,
  .area-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }
}

.progress-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.progress-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  height: auto;
}

.tag-label {
  color: var(--el-color-success-dark-2);
  font-weight: normal;
}

.date-selector {
  display: flex;
  align-items: center;
}

.date-selector :deep(.el-input__wrapper) {
  background-color: var(--el-color-primary-light-9);
}

.date-selector :deep(.el-input__inner) {
  color: var(--el-color-primary);
  font-weight: 500;
}

/* 响应式设计调整 */
@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .date-selector {
    width: 100%;
  }

  .date-selector :deep(.el-date-picker) {
    width: 100%;
  }
}

.account-actions {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 8px;
}

.action-button {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: scale(1.1);
}

.action-button.refresh {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.action-button.refresh:hover {
  background-color: var(--el-color-primary-light-8);
}

.action-button.delete {
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.action-button.delete:hover {
  background-color: var(--el-color-danger-light-8);
}

.account-card.disabled .action-button.refresh {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.account-card.disabled .action-button.refresh:hover {
  background-color: var(--el-color-primary-light-8);
}

.nav-menu {
  display: flex;
  gap: 24px;
  margin-left: 40px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #606266;
}

.nav-item:hover {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.nav-item.active {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 500;
}

.jobs-list {
  min-height: 200px;
}

.empty-jobs {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.job-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 12px;
}

.job-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.job-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: var(--el-color-primary-light-9);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--el-color-primary);
}

.job-icon.main-job {
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.job-info {
  flex: 1;
  min-width: 0;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.job-description {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  margin-right: 12px;
  min-width: 0;
}

.job-type-tag {
  flex-shrink: 0;
}

.description-text {
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-time {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 12px;
  align-items: center;
}

.time-separator {
  color: #dcdfe6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-menu {
    margin-left: 20px;
  }

  .nav-item {
    padding: 6px 12px;
  }
}

@media (max-width: 480px) {
  .navbar {
    flex-direction: column;
    height: auto;
    padding: 16px;
    gap: 16px;
  }

  .nav-menu {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
}

.area-info {
  padding: 20px;
}

.info-item {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}

.info-item .label {
  color: #909399;
  min-width: 80px;
}

.custom-dialog :deep(.el-dialog__body) {
  padding-top: 0;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.job-info-content {
  padding: 20px;
}

.info-item {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-item .label {
  color: #909399;
  min-width: 80px;
}

.result-list {
  margin-top: 24px;
}

.result-list h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}

.job-card {
  cursor: pointer;
}

.job-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-content {
  margin-top: 4px;
}

.timeline-content .message {
  color: #303133;
}

.timeline-content .data-info {
  margin-top: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 8px;
}

.timeline-content pre {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  color: #606266;
}

.task-todo-info,
.task-todo-info .task-id {
  display: none;
}

.timeline-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 0 10px;
  margin: 0 -10px;
}

.timeline-container::-webkit-scrollbar {
  width: 6px;
}

.timeline-container::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.timeline-container::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

.timeline-content {
  padding: 8px 0;
}

.timeline-content .message {
  color: #303133;
  margin-bottom: 4px;
}

.timeline-content .data-info {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 8px;
  margin-top: 8px;
}

.timeline-content pre {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  color: #606266;
}

.custom-dialog :deep(.el-timeline-item__tail) {
  border-left: 2px solid #e4e7ed;
}

.custom-dialog :deep(.el-timeline-item__node--normal) {
  left: -1px;
}

.custom-dialog :deep(.el-timeline) {
  padding-left: 16px;
}
</style>

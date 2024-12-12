import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Account, GymCampus, GymFacility, GymArea, GroupedArea } from '../types';
import * as api from '../api';

export const useGymStore = defineStore('gym', () => {
  const accounts = ref<Account[]>([]);
  const selectedAccount = ref<string>('');
  const campuses = ref<GymCampus[]>([]);
  const selectedCampus = ref<GymCampus | null>(null);
  const facilities = ref<GymFacility[]>([]);
  const selectedFacility = ref<GymFacility | null>(null);
  const areas = ref<GroupedArea[]>([]);
  const loading = ref(false);
  const error = ref('');

  const fetchAccounts = async () => {
    try {
      loading.value = true;
      error.value = '';
      accounts.value = await api.getAccounts();
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取账户列表失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  const fetchCampus = async (account: string) => {
    try {
      loading.value = true;
      error.value = '';
      selectedAccount.value = account;
      campuses.value = await api.getCampus(account);
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取校区列表失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  const fetchFacility = async (campus: GymCampus) => {
    try {
      loading.value = true;
      error.value = '';
      selectedCampus.value = campus;
      facilities.value = await api.getFacility(selectedAccount.value, campus);
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取场馆列表失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  const fetchArea = async (facility: GymFacility, date: string) => {
    try {
      loading.value = true;
      error.value = '';
      selectedFacility.value = facility;
      const areaList = await api.getArea(selectedAccount.value, facility, date);

      // 按 timeno 分组
      const groupedAreas = areaList.reduce((acc: GroupedArea[], area) => {
        const existingGroup = acc.find(g => g.timeno === area.timeno);
        if (existingGroup) {
          existingGroup.areas.push(area);
        } else {
          acc.push({ timeno: area.timeno, areas: [area] });
        }
        return acc;
      }, []);

      // 按 timeno 排序
      areas.value = groupedAreas.sort((a, b) => a.timeno.localeCompare(b.timeno));
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取区域列表失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  const addAccount = async (account: string, password: string) => {
    try {
      loading.value = true;
      error.value = '';
      await api.addAccount(account, password);
    } catch (e) {
      error.value = e instanceof Error ? e.message : '添加账户失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  const deleteAccount = async (account: string) => {
    try {
      loading.value = true;
      error.value = '';
      await api.deleteAccount(account);
    } catch (e) {
      error.value = e instanceof Error ? e.message : '删除账户失败';
      throw new Error(error.value);
    } finally {
      loading.value = false;
    }
  };

  return {
    accounts,
    selectedAccount,
    campuses,
    selectedCampus,
    facilities,
    selectedFacility,
    areas,
    loading,
    error,
    fetchAccounts,
    fetchCampus,
    fetchFacility,
    fetchArea,
    addAccount,
    deleteAccount,
  };
}); 
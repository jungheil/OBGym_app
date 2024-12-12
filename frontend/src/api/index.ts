import axios from 'axios';
import type { Account, GymCampus, GymFacility, GymArea } from '../types';

const api = axios.create({
  baseURL: '/api',
});

// 添加响应拦截器处理错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      throw new Error(error.response.data.detail || '请求失败');
    }
    throw error;
  }
);

export const getAccounts = async (): Promise<Account[]> => {
  const { data } = await api.get('/accounts');
  return data;
};

export const getCampus = async (account: string): Promise<GymCampus[]> => {
  const { data } = await api.get(`/campus/${account}`);
  return data;
};

export const getFacility = async (
  account: string,
  campus: GymCampus
): Promise<GymFacility[]> => {
  const { data } = await api.get(`/facility/${account}`, {
    params: {
      campus_code: campus.code,
      campus_name: campus.name,
    },
  });
  return data;
};

export const getArea = async (
  account: string,
  facility: GymFacility,
  date: string
): Promise<GymArea[]> => {
  const { data } = await api.get(`/area/${account}`, {
    params: {
      facility_serviceid: facility.serviceid,
      facility_name: facility.name,
      date,
    },
  });
  return data;
};

export const addAccount = async (account: string, password: string): Promise<void> => {
  await api.post('/accounts', { account, password });
};

export const deleteAccount = async (account: string): Promise<void> => {
  await api.delete(`/accounts/${account}`);
}; 
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const fetchAccuracy = async (date: string, decisionCutoff: string) => {
  const { data } = await api.get(`/accuracy`, {
    params: { date, decision_cutoff: decisionCutoff },
  });
  return data;
};

export const fetchIntervalErrors = async (date: string, decisionCutoff: string) => {
  const { data } = await api.get(`/accuracy/intervals`, {
    params: { date, decision_cutoff: decisionCutoff },
  });
  return data;
};

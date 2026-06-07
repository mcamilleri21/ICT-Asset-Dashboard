import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const fetchDashboardSummary  = async ()          => (await api.get('/dashboard/summary')).data
export const fetchClauseGaps        = async ()          => (await api.get('/dashboard/clause-gaps')).data
export const fetchProviderRisk      = async ()          => (await api.get('/dashboard/provider-risk')).data
export const fetchContracts         = async (params={}) => (await api.get('/contracts', { params })).data
export const fetchContract          = async (id)        => (await api.get(`/contracts/${id}`)).data
export const fetchContractDoraScore = async (id)        => (await api.get(`/contracts/${id}/dora-score`)).data
export const fetchProviders         = async ()          => (await api.get('/providers')).data
export const fetchServices          = async (params={}) => (await api.get('/services', { params })).data

export const uploadExcel = async (file) => {
  const form = new FormData()
  form.append('file', file)
  return (await api.post('/import/excel', form)).data
}

export const upsertClause = async (contractId, type, data) =>
  (await api.put(`/contracts/${contractId}/clauses/${type}`, data)).data

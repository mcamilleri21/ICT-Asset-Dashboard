import axios from 'axios'

const api = axios.create({ baseURL: '' })

export async function fetchSummary() {
  const { data } = await api.get('/api/dashboard/summary')
  return data
}

export async function uploadExcel(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/api/import/excel', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

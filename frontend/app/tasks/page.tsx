'use client'

import { useEffect, useState } from 'react'
import { getTasks, checkTaskStatus } from '@/lib/api'

interface Task {
  id: number
  task_id: string
  service: string
  type: string
  status: string
  result_url: string | null
  thumbnail_url: string | null
  error_message: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  created: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const params: any = { limit: 100 }
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.type = typeFilter
      const data = await getTasks(params)
      setTasks(Array.isArray(data) ? data : [])
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [statusFilter, typeFilter])

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Tasks</h1>

      <div className="flex gap-3 mb-4">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border rounded p-2 text-sm">
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="created">Created</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="border rounded p-2 text-sm">
          <option value="">All types</option>
          <option value="image">Image</option>
          <option value="video">Video</option>
          <option value="audio">Audio</option>
          <option value="editing">Editing</option>
        </select>
        <button onClick={load} className="bg-blue-600 text-white px-3 py-1 rounded text-sm">Refresh</button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-100 text-left">
              <th className="p-2 border-b">Task ID</th>
              <th className="p-2 border-b">Service</th>
              <th className="p-2 border-b">Type</th>
              <th className="p-2 border-b">Status</th>
              <th className="p-2 border-b">Created</th>
              <th className="p-2 border-b">Result</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} className="border-b hover:bg-gray-50">
                <td className="p-2 font-mono text-xs max-w-[200px] truncate" title={task.task_id}>{task.task_id}</td>
                <td className="p-2">{task.service}</td>
                <td className="p-2 capitalize">{task.type}</td>
                <td className="p-2">
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[task.status] || 'bg-gray-100 text-gray-800'}`}>
                    {task.status}
                  </span>
                  {task.status === 'pending' && (
                    <button
                      onClick={async () => { try { await checkTaskStatus(task.task_id); load() } catch {} }}
                      className="ml-2 text-xs text-blue-700 hover:underline"
                    >Check</button>
                  )}
                </td>
                <td className="p-2 text-xs text-gray-500">{new Date(task.created_at).toLocaleString()}</td>
                <td className="p-2">
                  {task.result_url ? (
                    <a href={task.result_url} target="_blank" className="text-blue-700 underline">Open</a>
                  ) : task.error_message ? (
                    <span className="text-red-600 text-xs" title={task.error_message}>Error</span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!loading && tasks.length === 0 && (
          <p className="text-gray-500 text-center py-8">No tasks found.</p>
        )}
      </div>
    </div>
  )
}

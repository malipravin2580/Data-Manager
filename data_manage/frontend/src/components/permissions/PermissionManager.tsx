import { useEffect, useState } from 'react'
import { Dialog } from '@headlessui/react'
import { TrashIcon } from '@heroicons/react/24/solid'

import { permissionsApi, usersApi } from '@/services/api'
import { Permission, User } from '@/types'

interface PermissionManagerProps {
  isOpen: boolean
  onClose: () => void
  filePath: string
}

export default function PermissionManager({ isOpen, onClose, filePath }: PermissionManagerProps) {
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [formData, setFormData] = useState({ user_id: '', permission: 'view' as 'view' | 'edit' | 'admin' })

  const fetchPermissions = async () => {
    const data = await permissionsApi.getFilePermissions(filePath)
    setPermissions(data)
  }

  useEffect(() => {
    if (isOpen) {
      void fetchPermissions()
      void fetchUsers()
    }
  }, [isOpen])

  const fetchUsers = async () => {
    const data = await usersApi.list()
    setUsers(data.filter((u) => u.is_active))
  }

  const handleGrant = async (e: React.FormEvent) => {
    e.preventDefault()
    await permissionsApi.grant({
      file_path: filePath,
      user_id: parseInt(formData.user_id, 10),
      permission: formData.permission
    })
    setFormData({ user_id: '', permission: 'view' })
    await fetchPermissions()
  }

  const handleRevoke = async (id: number) => {
    await permissionsApi.revoke(id)
    await fetchPermissions()
  }

  const userNameById = new Map(users.map((u) => [u.id, u.full_name || u.username]))

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
          <Dialog.Title className="text-lg font-semibold">Manage Permissions</Dialog.Title>
          <p className="text-sm text-gray-500 mt-1">{filePath}</p>

          <ul className="divide-y mt-4">
            {permissions.map((p) => (
              <li key={p.id} className="py-2 flex items-center justify-between">
                <span className="text-sm">
                  {p.user_id ? (userNameById.get(p.user_id) || `User #${p.user_id}`) : `Team #${p.team_id}`} ({p.permission})
                </span>
                <button onClick={() => void handleRevoke(p.id)} className="text-red-500 p-1">
                  <TrashIcon className="h-4 w-4" />
                </button>
              </li>
            ))}
          </ul>

          <form onSubmit={handleGrant} className="mt-4 pt-4 border-t space-y-3">
            {/* console.log(formData.user_id)
            console.log(users) */}
            
            <select
              required
              value={formData.user_id}
              onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
              className="w-full border border-gray-300 rounded-lg py-2 px-3"
            >
              <option value="" disabled>Select user</option>
              {users
                .filter((u) => u.id !== undefined)
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {(u.full_name || u.username)} ({u.username})
                  </option>
                ))}
            </select>
            <select
              value={formData.permission}
              onChange={(e) => setFormData({ ...formData, permission: e.target.value as 'view' | 'edit' | 'admin' })}
              className="w-full border border-gray-300 rounded-lg py-2 px-3"
            >
              <option value="view">View</option>
              <option value="edit">Edit</option>
              <option value="admin">Admin</option>
            </select>
            <div className="flex gap-2">
              <button type="button" onClick={onClose} className="flex-1 border border-gray-300 py-2 rounded-lg">Close</button>
              <button type="submit" className="flex-1 bg-primary-600 text-white py-2 rounded-lg">Grant</button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

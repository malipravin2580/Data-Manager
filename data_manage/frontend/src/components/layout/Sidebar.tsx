import {
  AdjustmentsHorizontalIcon,
  CircleStackIcon,
  DocumentIcon,
  DocumentTextIcon,
  FolderIcon,
  TableCellsIcon
} from '@heroicons/react/24/outline'
import { FileType } from '@/types'

interface SidebarProps {
  selectedType: FileType
  onSelectType: (type: FileType) => void
}

const navItems: { type: FileType; label: string; icon: typeof DocumentIcon }[] = [
  { type: 'all', label: 'All Files', icon: FolderIcon },
  { type: 'csv', label: 'CSV', icon: DocumentTextIcon },
  { type: 'json', label: 'JSON', icon: DocumentIcon },
  { type: 'xlsx', label: 'Excel', icon: TableCellsIcon },
  { type: 'parquet', label: 'Parquet', icon: CircleStackIcon }
]

export default function Sidebar({ selectedType, onSelectType }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = selectedType === item.type

          return (
            <button
              key={item.type}
              onClick={() => onSelectType(item.type)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium
                transition-colors
                ${isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50'}
              `}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'text-primary-500' : 'text-gray-400'}`} />
              {item.label}
            </button>
          )
        })}

        <div className="pt-4 mt-4 border-t border-gray-200">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50">
            <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
            Settings
          </button>
        </div>
      </nav>
    </aside>
  )
}

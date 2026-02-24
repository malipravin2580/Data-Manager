interface MetadataPanelProps {
  metadata: Record<string, any>
}

export default function MetadataPanel({ metadata }: MetadataPanelProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <pre className="text-sm text-gray-800 overflow-auto max-h-[500px]">
        {JSON.stringify(metadata, null, 2)}
      </pre>
    </div>
  )
}

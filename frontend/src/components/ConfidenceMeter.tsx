interface Props {
  value: number;
}

export function ConfidenceMeter({ value }: Props) {
  const percent = Math.round(Math.max(0, Math.min(value, 1)) * 100);
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span>Confidence</span>
        <span className="font-semibold">{percent}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-300 dark:bg-slate-700">
        <div className="h-2 rounded-full bg-indigo-500" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

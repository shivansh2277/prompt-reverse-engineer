import { useState } from 'react';
import type { ReverseResponse } from '../types';
import { ConfidenceMeter } from './ConfidenceMeter';

interface Props {
  result: ReverseResponse;
}

export function ResultsPanel({ result }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [raw, setRaw] = useState(false);

  const copyPrompt = async () => {
    await navigator.clipboard.writeText(result.inferred_prompt);
  };

  if (raw) {
    return (
      <div className="rounded-xl border border-slate-300 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Raw JSON</h2>
          <button className="rounded bg-slate-200 px-3 py-1 text-sm dark:bg-slate-700" onClick={() => setRaw(false)}>Back</button>
        </div>
        <pre className="overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-xl border border-slate-300 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Analysis Results</h2>
        <button className="rounded bg-slate-200 px-3 py-1 text-sm dark:bg-slate-700" onClick={() => setRaw(true)}>JSON View</button>
      </div>

      <div>
        <div className="mb-1 text-sm text-slate-500">Inferred Prompt</div>
        <div className="rounded border border-slate-200 p-3 dark:border-slate-700">{result.inferred_prompt}</div>
        <button onClick={copyPrompt} className="mt-2 rounded bg-indigo-600 px-3 py-1 text-sm text-white">Copy</button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div><span className="text-sm text-slate-500">Prompt Style: </span><span className="rounded bg-indigo-100 px-2 py-1 text-xs dark:bg-indigo-900">{result.prompt_style}</span></div>
        <div><span className="text-sm text-slate-500">Task Type: </span>{result.task_type}</div>
        <div><span className="text-sm text-slate-500">Temperature: </span>{result.temperature_estimate}</div>
        <div><span className="text-sm text-slate-500">Cache: </span>{result.cached ? 'Hit' : 'Miss'}</div>
        <div className="sm:col-span-2"><span className="text-sm text-slate-500">Request ID: </span><code>{result.request_id}</code></div>
      </div>

      <ConfidenceMeter value={result.confidence_score} />

      <div>
        <h3 className="mb-1 font-semibold">Explainability</h3>
        <p className="text-sm">{result.explainability.summary}</p>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {result.explainability.key_signals.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>

      <div>
        <h3 className="mb-1 font-semibold">Constraints Detected</h3>
        <ul className="list-disc pl-5 text-sm">
          {result.constraints_detected.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>

      <div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="rounded bg-slate-200 px-3 py-1 text-sm dark:bg-slate-700"
        >
          {expanded ? 'Hide' : 'Show'} Reasoning Trace
        </button>
        {expanded ? (
          <ul className="mt-2 list-decimal pl-5 text-sm">
            {result.reasoning_trace.map((trace) => <li key={trace}>{trace}</li>)}
          </ul>
        ) : null}
      </div>
    </div>
  );
}

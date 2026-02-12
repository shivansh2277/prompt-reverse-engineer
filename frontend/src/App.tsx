import { FormEvent, useState } from 'react';
import { reversePrompt } from './lib/api';
import type { ReverseResponse } from './types';
import { ResultsPanel } from './components/ResultsPanel';
import { Spinner } from './components/Spinner';

const starterText = `Paste an LLM output here.\nExample:\n1. First gather constraints.\n2. Then respond in JSON format with confidence.`;

export default function App() {
  const [outputText, setOutputText] = useState(starterText);
  const [result, setResult] = useState<ReverseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await reversePrompt(outputText);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto min-h-screen max-w-5xl p-4 sm:p-8">
      <h1 className="mb-2 text-3xl font-bold">Prompt Reverse Engineer</h1>
      <p className="mb-6 text-sm text-slate-500">Paste-first workflow to infer the likely prompt that produced an LLM response.</p>

      <form onSubmit={analyze} className="space-y-4">
        <label htmlFor="outputText" className="block text-sm font-medium">LLM Output Text</label>
        <textarea
          id="outputText"
          value={outputText}
          onChange={(e) => setOutputText(e.target.value)}
          className="h-56 w-full rounded-xl border border-slate-300 bg-white p-4 text-sm outline-none ring-indigo-500 focus:ring-2 dark:border-slate-700 dark:bg-slate-900"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={loading || outputText.trim().length === 0}
            className="inline-flex items-center gap-2 rounded bg-indigo-600 px-4 py-2 text-white disabled:opacity-50"
          >
            {loading ? <Spinner /> : null}
            Analyze
          </button>
          {error ? <span className="text-sm text-red-500">{error}</span> : null}
          {error ? (
            <button type="button" onClick={(e) => analyze(e as unknown as FormEvent)} className="rounded border border-slate-400 px-3 py-1 text-sm">
              Retry
            </button>
          ) : null}
        </div>
      </form>

      <section className="mt-6">{result ? <ResultsPanel result={result} /> : null}</section>
    </main>
  );
}

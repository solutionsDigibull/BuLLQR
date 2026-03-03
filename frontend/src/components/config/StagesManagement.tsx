import { useState, useEffect } from 'react';
import { getStages } from '../../services/scan.ts';
import { createStage, updateStage, deleteStage } from '../../services/config.ts';
import type { ProductionStage } from '../../types/scan.ts';
import type { StageCreate } from '../../types/config.ts';

export default function StagesManagement() {
  const [stages, setStages] = useState<ProductionStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<{ stage_name: string; description: string }>({ stage_name: '', description: '' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadStages();
  }, []);

  async function loadStages() {
    try {
      const data = await getStages();
      setStages(data);
    } catch {
      setError('Failed to load stages');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const payload: StageCreate = {
        stage_name: form.stage_name,
        stage_sequence: stages.length + 1,
        description: form.description || undefined,
      };
      if (editingId) {
        await updateStage(editingId, { stage_name: form.stage_name, description: form.description || undefined });
      } else {
        await createStage(payload);
      }
      setShowForm(false);
      setEditingId(null);
      setForm({ stage_name: '', description: '' });
      await loadStages();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save stage');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Delete this stage? This cannot be undone.')) return;
    try {
      await deleteStage(id);
      await loadStages();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete stage');
    }
  }

  function startEdit(stage: ProductionStage) {
    setEditingId(stage.id);
    setForm({ stage_name: stage.stage_name, description: stage.description || '' });
    setShowForm(true);
  }

  if (loading) return <p className="text-sm text-gray-500">Loading stages...</p>;

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded text-sm">{error}
          <button onClick={() => setError('')} className="ml-2 text-red-500 hover:text-red-800">&times;</button>
        </div>
      )}

      <div className="flex justify-between items-center">
        <h3 className="text-base font-medium text-gray-700">Production Stages</h3>
        <button
          onClick={() => { setShowForm(true); setEditingId(null); setForm({ stage_name: '', description: '' }); }}
          className="px-3 py-1.5 bg-primary text-white text-sm rounded hover:bg-primary-dark"
        >
          + Add Stage
        </button>
      </div>

      <p className="text-xs text-gray-400">Stage order is configured per product in the Products tab (Edit Product).</p>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 border rounded-md p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Stage Name</label>
              <input
                value={form.stage_name}
                onChange={(e) => setForm({ ...form, stage_name: e.target.value })}
                required
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <input
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border rounded px-2 py-1.5 text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={saving} className="px-3 py-1.5 bg-primary text-white text-sm rounded hover:bg-primary-dark disabled:opacity-50">
              {saving ? 'Saving...' : editingId ? 'Update' : 'Create'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); setEditingId(null); }} className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300">
              Cancel
            </button>
          </div>
        </form>
      )}

      <table className="w-full text-sm border rounded-md overflow-hidden">
        <thead className="bg-gray-50">
          <tr className="text-left text-xs font-medium text-gray-500 uppercase">
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Description</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {stages.map((s) => (
            <tr key={s.id} className="hover:bg-gray-50">
              <td className="px-4 py-2 font-medium">{s.stage_name}</td>
              <td className="px-4 py-2 text-gray-500">{s.description || '—'}</td>
              <td className="px-4 py-2 space-x-2">
                <button onClick={() => startEdit(s)} className="text-primary hover:underline text-xs">Edit</button>
                <button onClick={() => handleDelete(s.id)} className="text-red-500 hover:underline text-xs">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

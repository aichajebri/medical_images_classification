import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { patientApi, PatientCreate } from '../lib/api';

export default function PatientForm() {
  const [formData, setFormData] = useState<PatientCreate>({
    patient_id: '',
    age: undefined,
    gender: '',
  });
  const [showSuccess, setShowSuccess] = useState(false);

  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: patientApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      setFormData({ patient_id: '', age: undefined, gender: '' });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.patient_id) {
      alert('Patient ID is required');
      return;
    }
    mutation.mutate(formData);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl">
          👤
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Create Patient</h2>
          <p className="text-sm text-gray-500">Register a new patient in the system</p>
        </div>
      </div>

      {/* Success Message */}
      {showSuccess && (
        <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl flex items-center gap-3">
          <span className="text-2xl">✅</span>
          <span className="text-green-700 font-medium">Patient created successfully!</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="patient_id" className="block text-sm font-semibold text-gray-700 mb-2">
            Patient ID <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🆔</span>
            <input
              type="text"
              id="patient_id"
              required
              value={formData.patient_id}
              onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-gray-50 hover:bg-white"
              placeholder="e.g., P001"
            />
          </div>
        </div>

        <div>
          <label htmlFor="age" className="block text-sm font-semibold text-gray-700 mb-2">
            Age
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">📅</span>
            <input
              type="number"
              id="age"
              value={formData.age || ''}
              onChange={(e) => setFormData({ ...formData, age: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-gray-50 hover:bg-white"
              placeholder="e.g., 45"
              min="0"
              max="120"
            />
          </div>
        </div>

        <div>
          <label htmlFor="gender" className="block text-sm font-semibold text-gray-700 mb-2">
            Gender
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">⚧</span>
            <select
              id="gender"
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-gray-50 hover:bg-white appearance-none cursor-pointer"
            >
              <option value="">Select gender</option>
              <option value="M">👨 Male</option>
              <option value="F">👩 Female</option>
              <option value="Other">🧑 Other</option>
            </select>
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">▼</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:shadow-blue-500/25 flex items-center justify-center gap-2"
        >
          {mutation.isPending ? (
            <>
              <span className="animate-spin">⏳</span> Creating...
            </>
          ) : (
            <>
              <span>✨</span> Create Patient
            </>
          )}
        </button>
      </form>
    </div>
  );
}

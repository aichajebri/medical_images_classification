import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { studyApi, patientApi, StudyCreate } from '../lib/api';

interface StudyFormProps {
  onStudyCreated?: (studyId: number) => void;
}

export default function StudyForm({ onStudyCreated }: StudyFormProps) {
  const [formData, setFormData] = useState<StudyCreate>({
    patient_id: 0,
    study_date: new Date().toISOString().split('T')[0],
    modality: 'MRI',
  });

  const queryClient = useQueryClient();

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: patientApi.getAll,
  });

  const mutation = useMutation({
    mutationFn: studyApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['studies'] });
      setFormData({
        patient_id: 0,
        study_date: new Date().toISOString().split('T')[0],
        modality: 'MRI',
      });
      if (onStudyCreated) {
        onStudyCreated(data.id);
      }
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.patient_id) {
      alert('Please select a patient');
      return;
    }
    mutation.mutate(formData);
  };

  const modalityIcons: Record<string, string> = {
    'MRI': '🧲',
    'CT': '📡',
    'X-Ray': '☢️',
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-2xl">
          📋
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Create Study</h2>
          <p className="text-sm text-gray-500">Set up a new imaging study for analysis</p>
        </div>
      </div>

      {patients.length === 0 && (
        <div className="mb-6 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-xl flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <span className="text-yellow-700">No patients found. Please create a patient first.</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="patient_id" className="block text-sm font-semibold text-gray-700 mb-2">
            Select Patient <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">👤</span>
            <select
              id="patient_id"
              required
              value={formData.patient_id}
              onChange={(e) => setFormData({ ...formData, patient_id: parseInt(e.target.value) })}
              className="w-full pl-12 pr-10 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all bg-gray-50 hover:bg-white appearance-none cursor-pointer"
            >
              <option value={0}>Select a patient...</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.patient_id} {patient.age ? `(Age: ${patient.age}, ${patient.gender || 'N/A'})` : ''}
                </option>
              ))}
            </select>
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">▼</span>
          </div>
        </div>

        <div>
          <label htmlFor="study_date" className="block text-sm font-semibold text-gray-700 mb-2">
            Study Date <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">📅</span>
            <input
              type="date"
              id="study_date"
              required
              value={formData.study_date}
              onChange={(e) => setFormData({ ...formData, study_date: e.target.value })}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all bg-gray-50 hover:bg-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Imaging Modality
          </label>
          <div className="grid grid-cols-3 gap-3">
            {['MRI', 'CT', 'X-Ray'].map((modality) => (
              <button
                key={modality}
                type="button"
                onClick={() => setFormData({ ...formData, modality })}
                className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-2 ${formData.modality === modality
                    ? 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
              >
                <span className="text-2xl">{modalityIcons[modality]}</span>
                <span className={`font-medium ${formData.modality === modality ? 'text-green-600' : 'text-gray-600'}`}>
                  {modality}
                </span>
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending || patients.length === 0}
          className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 px-6 rounded-xl hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:shadow-green-500/25 flex items-center justify-center gap-2"
        >
          {mutation.isPending ? (
            <>
              <span className="animate-spin">⏳</span> Creating...
            </>
          ) : (
            <>
              <span>📋</span> Create Study & Continue
            </>
          )}
        </button>
      </form>
    </div>
  );
}

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { patientApi, studyApi, predictionApi, PredictionResponse } from '../lib/api';
import PatientForm from '../components/PatientForm';
import StudyForm from '../components/StudyForm';
import MRIUpload from '../components/MRIUpload';
import ExplainabilityView from '../components/ExplainabilityView';
import ResultsView from '../components/ResultsView';
import AnalyticsView from '../components/AnalyticsView';

export default function WorkflowPage() {
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'patient' | 'study' | 'upload' | 'results'>('patient');

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: patientApi.getAll,
  });

  const { data: studies = [] } = useQuery({
    queryKey: ['studies'],
    queryFn: async () => {
      try {
        return [];
      } catch {
        return [];
      }
    },
  });

  const handlePredictionComplete = (result: PredictionResponse, imageUrl: string) => {
    setPredictionResult(result);
    setUploadedImageUrl(imageUrl);
    setCurrentStep('results');
  };

  const handleDownloadReport = () => {
    if (predictionResult) {
      const reportUrl = `http://localhost:8000/api/reports/${predictionResult.id}`;
      window.open(reportUrl, '_blank');
    }
  };

  const steps = [
    { key: 'patient', label: 'Create Patient', icon: '👤', description: 'Register new patient' },
    { key: 'study', label: 'Create Study', icon: '📋', description: 'Set up imaging study' },
    { key: 'upload', label: 'Upload & Predict', icon: '🧠', description: 'Analyze MRI scan' },
    { key: 'results', label: 'View Results', icon: '📊', description: 'Review diagnosis' },
  ];

  const getStepIndex = (step: string) => steps.findIndex(s => s.key === step);

  return (
    <div className="min-h-screen py-8">
      {/* Hero Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-dark rounded-2xl p-8 mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl animate-float">
              🧠
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-1">
                Brain Tumor <span className="gradient-text">Analysis System</span>
              </h1>
              <p className="text-gray-400">AI-Powered Medical Imaging Diagnosis with Explainable AI</p>
            </div>
          </div>
        </div>

        {/* Step Indicator - Premium Design */}
        <div className="glass-dark rounded-2xl p-6 mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.key} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div
                    className={`step-indicator w-14 h-14 rounded-xl flex items-center justify-center text-2xl font-semibold cursor-pointer transition-all duration-300 ${currentStep === step.key
                        ? 'active bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                        : index < getStepIndex(currentStep)
                          ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white'
                          : 'bg-gray-700 text-gray-400'
                      }`}
                    onClick={() => {
                      if (index <= getStepIndex(currentStep)) {
                        setCurrentStep(step.key as any);
                      }
                    }}
                  >
                    {index < getStepIndex(currentStep) ? '✓' : step.icon}
                  </div>
                  <span className={`mt-3 text-sm font-medium ${currentStep === step.key ? 'text-blue-400' : 'text-gray-400'
                    }`}>
                    {step.label}
                  </span>
                  <span className="text-xs text-gray-500 mt-1">{step.description}</span>
                </div>
                {index < 3 && (
                  <div
                    className={`flex-1 h-1 mx-4 rounded-full transition-all duration-500 ${index < getStepIndex(currentStep)
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                        : 'bg-gray-700'
                      }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Forms */}
          <div className="lg:col-span-2 space-y-6">
            {currentStep === 'patient' && (
              <div className="glass-card rounded-2xl overflow-hidden hover-lift">
                <PatientForm />
                {patients.length > 0 && (
                  <div className="p-6 border-t border-gray-100">
                    <button
                      onClick={() => setCurrentStep('study')}
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:shadow-blue-500/25"
                    >
                      Continue to Create Study →
                    </button>
                  </div>
                )}
              </div>
            )}

            {currentStep === 'study' && (
              <div className="glass-card rounded-2xl overflow-hidden hover-lift">
                <StudyForm onStudyCreated={(studyId) => {
                  setSelectedStudyId(studyId);
                  setCurrentStep('upload');
                }} />
              </div>
            )}

            {currentStep === 'upload' && (
              <div className="glass-card rounded-2xl overflow-hidden hover-lift">
                {selectedStudyId ? (
                  <MRIUpload
                    studyId={selectedStudyId}
                    onPredictionComplete={handlePredictionComplete}
                  />
                ) : (
                  <div className="p-8 text-center">
                    <div className="text-6xl mb-4">📋</div>
                    <h2 className="text-2xl font-bold mb-4 text-gray-800">Select or Create Study</h2>
                    <p className="text-gray-600 mb-6">Please create a study first to upload MRI images.</p>
                    <button
                      onClick={() => setCurrentStep('study')}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-8 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-semibold"
                    >
                      ← Go Back to Create Study
                    </button>
                  </div>
                )}
              </div>
            )}

            {currentStep === 'results' && predictionResult && uploadedImageUrl && (
              <div className="space-y-6">
                <ResultsView
                  result={predictionResult}
                  imageUrl={uploadedImageUrl}
                  onDownloadReport={handleDownloadReport}
                />
                <ExplainabilityView
                  originalImage={uploadedImageUrl}
                  heatmapPath={predictionResult.heatmap_path}
                  classLabel={predictionResult.class_label}
                  confidence={predictionResult.confidence}
                />
              </div>
            )}
          </div>

          {/* Right Column - Info & Analytics */}
          <div className="space-y-6">
            {currentStep === 'results' && predictionResult && (
              <AnalyticsView
                confidence={predictionResult.confidence}
                classLabel={predictionResult.class_label}
                processingTime={predictionResult.processing_time}
              />
            )}

            {/* Quick Stats Card */}
            <div className="glass-card rounded-2xl p-6 hover-lift">
              <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                <span className="text-2xl">📈</span> Quick Stats
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                  <span className="text-gray-600 flex items-center gap-2">
                    <span>👥</span> Patients
                  </span>
                  <span className="font-bold text-xl text-blue-600">{patients.length}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                  <span className="text-gray-600 flex items-center gap-2">
                    <span>📋</span> Studies
                  </span>
                  <span className="font-bold text-xl text-green-600">{studies.length}</span>
                </div>
              </div>
            </div>

            {/* Info Card */}
            <div className="glass-card rounded-2xl p-6 hover-lift">
              <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
                <span className="text-2xl">ℹ️</span> About This System
              </h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span>Deep learning-based tumor classification</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span>Grad-CAM explainability visualization</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span>Automated PDF report generation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span>4-class classification: Glioma, Meningioma, Pituitary, No Tumor</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

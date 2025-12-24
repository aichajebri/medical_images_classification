import { PredictionResponse } from '../lib/api';
import { predictionApi } from '../lib/api';
import { useState, useEffect } from 'react';

interface ResultsViewProps {
  result: PredictionResponse;
  imageUrl: string;
  onDownloadReport: () => void;
}

export default function ResultsView({ result, imageUrl, onDownloadReport }: ResultsViewProps) {
  const [animatedConfidence, setAnimatedConfidence] = useState(0);

  useEffect(() => {
    // Animate confidence from 0 to actual value
    const timer = setTimeout(() => {
      setAnimatedConfidence(result.confidence * 100);
    }, 100);
    return () => clearTimeout(timer);
  }, [result.confidence]);

  const getClassInfo = (classLabel: string) => {
    const info: Record<string, { color: string; gradient: string; icon: string; risk: string; riskClass: string }> = {
      glioma: {
        color: 'badge-glioma',
        gradient: 'from-red-500 to-rose-600',
        icon: '⚠️',
        risk: 'High Risk',
        riskClass: 'risk-high'
      },
      meningioma: {
        color: 'badge-meningioma',
        gradient: 'from-orange-500 to-amber-600',
        icon: '⚡',
        risk: 'Medium Risk',
        riskClass: 'risk-medium'
      },
      pituitary: {
        color: 'badge-pituitary',
        gradient: 'from-blue-500 to-indigo-600',
        icon: '🔵',
        risk: 'Medium Risk',
        riskClass: 'risk-medium'
      },
      notumor: {
        color: 'badge-notumor',
        gradient: 'from-green-500 to-emerald-600',
        icon: '✅',
        risk: 'Low Risk',
        riskClass: 'risk-low'
      },
    };
    return info[classLabel.toLowerCase()] || {
      color: 'bg-gray-500',
      gradient: 'from-gray-500 to-gray-600',
      icon: '❓',
      risk: 'Unknown',
      riskClass: 'text-gray-500'
    };
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'from-green-400 to-emerald-500';
    if (confidence >= 60) return 'from-yellow-400 to-amber-500';
    return 'from-red-400 to-rose-500';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 90) return 'Very High Confidence';
    if (confidence >= 75) return 'High Confidence';
    if (confidence >= 60) return 'Moderate Confidence';
    if (confidence >= 40) return 'Low Confidence';
    return 'Very Low Confidence';
  };

  const classInfo = getClassInfo(result.class_label);
  const confidencePercent = result.confidence * 100;

  return (
    <div className="glass-card rounded-2xl overflow-hidden">
      {/* Header */}
      <div className={`bg-gradient-to-r ${classInfo.gradient} p-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-5xl animate-float">{classInfo.icon}</div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">Prediction Results</h2>
              <p className="text-white/80 text-sm">AI Analysis Complete</p>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm ${classInfo.riskClass}`}>
            <span className="font-bold text-white">{classInfo.risk}</span>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Main Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left: Image */}
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Original MRI Scan</h3>
            <div className="relative rounded-xl overflow-hidden shadow-lg">
              <img
                src={imageUrl}
                alt="MRI Scan"
                className="w-full h-auto"
              />
              <div className="absolute top-3 left-3">
                <span className={`${classInfo.color} px-3 py-1 rounded-full text-sm font-bold shadow-lg`}>
                  {result.class_label.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Right: Metrics */}
          <div className="space-y-6">
            {/* Classification */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Classification</h3>
              <div className="flex items-center gap-4">
                <span className={`${classInfo.color} px-4 py-2 rounded-xl text-lg font-bold shadow-md`}>
                  {result.class_label.charAt(0).toUpperCase() + result.class_label.slice(1)}
                </span>
              </div>
            </div>

            {/* Confidence Score */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-5">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Confidence Score</h3>
                <span className="text-3xl font-bold text-gray-800">{confidencePercent.toFixed(1)}%</span>
              </div>
              <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`confidence-bar absolute left-0 top-0 h-full rounded-full bg-gradient-to-r ${getConfidenceColor(confidencePercent)}`}
                  style={{ width: `${animatedConfidence}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-gray-600">{getConfidenceLabel(confidencePercent)}</p>
            </div>

            {/* Processing Time */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Processing Time</h3>
              <div className="flex items-center gap-2">
                <span className="text-2xl">⚡</span>
                <span className="text-2xl font-bold text-gray-800">{result.processing_time.toFixed(2)}s</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-gray-100">
          <a
            href={predictionApi.downloadReport(result.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 font-semibold text-center flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:shadow-blue-500/25"
          >
            <span className="text-xl">📄</span>
            Download PDF Report
          </a>
          <button
            onClick={() => window.location.reload()}
            className="flex-1 bg-gray-100 text-gray-700 py-4 px-6 rounded-xl hover:bg-gray-200 transition-all duration-300 font-semibold text-center flex items-center justify-center gap-2"
          >
            <span className="text-xl">🔄</span>
            New Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

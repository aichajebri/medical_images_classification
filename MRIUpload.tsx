import { useState, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { predictionApi, PredictionResponse } from '../lib/api';

interface MRIUploadProps {
  studyId: number;
  onPredictionComplete: (result: PredictionResponse, imageUrl: string) => void;
}

export default function MRIUpload({ studyId, onPredictionComplete }: MRIUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const mutation = useMutation({
    mutationFn: (file: File) => predictionApi.predict(studyId, file),
    onSuccess: (data) => {
      const imageUrl = preview || '';
      onPredictionComplete(data, imageUrl);
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }
    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
      drawImageToCanvas(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const drawImageToCanvas = (imageSrc: string) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    img.src = imageSrc;
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert('Please select an image file');
      return;
    }
    mutation.mutate(selectedFile);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-2xl animate-float">
          🧠
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Upload MRI Image</h2>
          <p className="text-sm text-gray-500">Upload brain MRI scan for AI-powered analysis</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Drag & Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${dragActive
              ? 'border-purple-500 bg-purple-50'
              : preview
                ? 'border-green-500 bg-green-50'
                : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50/50'
            }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          {!preview ? (
            <div className="space-y-4">
              <div className="text-6xl animate-pulse-slow">🖼️</div>
              <div>
                <p className="text-lg font-semibold text-gray-700">
                  Drag & drop your MRI image here
                </p>
                <p className="text-gray-500">or click to browse files</p>
              </div>
              <div className="flex justify-center gap-4 text-sm text-gray-400">
                <span>📁 PNG</span>
                <span>📁 JPG</span>
                <span>📁 JPEG</span>
                <span>📁 DICOM</span>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-4xl">✅</div>
              <p className="text-green-600 font-semibold">{selectedFile?.name}</p>
              <p className="text-sm text-gray-500">Click to select a different file</p>
            </div>
          )}
        </div>

        {/* Preview */}
        {preview && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                <span>👁️</span> Image Preview
              </h3>
              <span className="text-sm text-gray-400">
                {selectedFile && `${(selectedFile.size / 1024).toFixed(1)} KB`}
              </span>
            </div>
            <div className="relative rounded-2xl overflow-hidden shadow-lg bg-gray-900">
              <canvas
                ref={canvasRef}
                className="w-full h-auto mx-auto"
                style={{ maxHeight: '400px' }}
              />
              <div className="absolute top-3 left-3 px-3 py-1 bg-black/50 backdrop-blur-sm rounded-full text-white text-sm">
                📍 Study ID: {studyId}
              </div>
            </div>
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || mutation.isPending}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-4 px-6 rounded-xl hover:from-purple-600 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:shadow-purple-500/25 flex items-center justify-center gap-3"
        >
          {mutation.isPending ? (
            <>
              <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Analyzing with AI...</span>
              <span className="text-sm opacity-75">(This may take a moment)</span>
            </>
          ) : (
            <>
              <span className="text-2xl">🔬</span>
              <span>Upload & Run AI Prediction</span>
            </>
          )}
        </button>

        {/* Processing Status */}
        {mutation.isPending && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 border-3 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="font-medium text-purple-700">Processing your MRI scan...</span>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <span>✓</span> Image uploaded successfully
              </div>
              <div className="flex items-center gap-2">
                <span className="animate-pulse">⏳</span> Running deep learning model...
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <span>○</span> Generating Grad-CAM heatmap
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <span>○</span> Creating PDF report
              </div>
            </div>
          </div>
        )}

        {/* Info Panel */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4">
          <h4 className="font-semibold text-blue-700 mb-2 flex items-center gap-2">
            <span>💡</span> Tips for Best Results
          </h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Use high-resolution MRI scans (T1/T2 weighted)</li>
            <li>• Ensure the image is properly oriented</li>
            <li>• Axial brain slices work best for tumor detection</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

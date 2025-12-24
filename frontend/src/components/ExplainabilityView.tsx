import { useEffect, useRef, useState } from 'react';

interface ExplainabilityViewProps {
  originalImage: string;
  heatmapPath: string;
  classLabel: string;
  confidence: number;
}

export default function ExplainabilityView({
  originalImage,
  heatmapPath,
  classLabel,
  confidence,
}: ExplainabilityViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const [heatmapLoaded, setHeatmapLoaded] = useState(false);
  const [heatmapError, setHeatmapError] = useState<string | null>(null);
  const [showOverlay, setShowOverlay] = useState(true);

  // Construct the correct heatmap URL
  const getHeatmapUrl = () => {
    if (heatmapPath.startsWith('http')) {
      return heatmapPath;
    }
    // The path is stored as "storage/heatmaps/filename.jpg"
    // The backend serves static files at /storage/
    return `http://localhost:8000/${heatmapPath}`;
  };

  useEffect(() => {
    const loadAndOverlay = async () => {
      const canvas = canvasRef.current;
      const overlayCanvas = overlayCanvasRef.current;
      if (!canvas || !overlayCanvas) return;

      const ctx = canvas.getContext('2d');
      const overlayCtx = overlayCanvas.getContext('2d');
      if (!ctx || !overlayCtx) return;

      // Load original image
      const originalImg = new Image();
      originalImg.crossOrigin = 'anonymous';
      originalImg.onload = () => {
        canvas.width = originalImg.width;
        canvas.height = originalImg.height;
        ctx.drawImage(originalImg, 0, 0);

        // Load heatmap
        const heatmapImg = new Image();
        heatmapImg.crossOrigin = 'anonymous';
        heatmapImg.onload = () => {
          overlayCanvas.width = originalImg.width;
          overlayCanvas.height = originalImg.height;

          // Draw original image first
          overlayCtx.drawImage(originalImg, 0, 0);

          // Then overlay heatmap with transparency
          overlayCtx.globalAlpha = 0.6;
          overlayCtx.globalCompositeOperation = 'screen';
          overlayCtx.drawImage(heatmapImg, 0, 0, originalImg.width, originalImg.height);

          setHeatmapLoaded(true);
          setHeatmapError(null);
        };
        heatmapImg.onerror = () => {
          setHeatmapError('Failed to load heatmap image');
          // Still show original on overlay canvas as fallback
          overlayCanvas.width = originalImg.width;
          overlayCanvas.height = originalImg.height;
          overlayCtx.drawImage(originalImg, 0, 0);
        };
        heatmapImg.src = getHeatmapUrl();
      };
      originalImg.src = originalImage;
    };

    loadAndOverlay();
  }, [originalImage, heatmapPath]);

  return (
    <div className="glass-card rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-4xl animate-pulse-slow">🔬</div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">Explainability View</h2>
              <p className="text-white/80 text-sm">Grad-CAM Visualization</p>
            </div>
          </div>
          {heatmapLoaded && (
            <span className="px-3 py-1 bg-white/20 rounded-full text-white text-sm">
              ✓ Heatmap Generated
            </span>
          )}
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Toggle Controls */}
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => setShowOverlay(false)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${!showOverlay
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
          >
            Original Image
          </button>
          <button
            onClick={() => setShowOverlay(true)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${showOverlay
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
          >
            With Grad-CAM Overlay
          </button>
        </div>

        {/* Comparison View */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Original Image */}
          <div className={`transition-opacity duration-300 ${!showOverlay ? 'opacity-100' : 'opacity-50'}`}>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span>🖼️</span> Original MRI
            </h3>
            <div className="relative rounded-xl overflow-hidden shadow-lg bg-gray-900">
              <canvas
                ref={canvasRef}
                className="w-full h-auto"
              />
            </div>
          </div>

          {/* Heatmap Overlay */}
          <div className={`transition-opacity duration-300 ${showOverlay ? 'opacity-100' : 'opacity-50'}`}>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span>🔥</span> Grad-CAM Heatmap
            </h3>
            <div className="relative rounded-xl overflow-hidden shadow-lg bg-gray-900">
              {heatmapError ? (
                <div className="aspect-square flex flex-col items-center justify-center bg-gray-100 text-gray-500 p-8">
                  <span className="text-4xl mb-2">⚠️</span>
                  <p className="text-center">{heatmapError}</p>
                  <p className="text-sm text-gray-400 mt-2">Path: {getHeatmapUrl()}</p>
                </div>
              ) : (
                <canvas
                  ref={overlayCanvasRef}
                  className="w-full h-auto"
                />
              )}
            </div>
          </div>
        </div>

        {/* Info Panel */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-indigo-600 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span>💡</span> Understanding the Visualization
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔴</span>
              <div>
                <p className="font-medium text-gray-800">Red/Yellow Areas</p>
                <p className="text-sm text-gray-600">High attention regions - most important for prediction</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔵</span>
              <div>
                <p className="font-medium text-gray-800">Blue/Green Areas</p>
                <p className="text-sm text-gray-600">Lower attention - less influential in the decision</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-2xl">🧠</span>
              <div>
                <p className="font-medium text-gray-800">Model Focus</p>
                <p className="text-sm text-gray-600">Shows where the AI looked to classify as <strong className="capitalize">{classLabel}</strong></p>
              </div>
            </div>
          </div>
        </div>

        {/* Direct Heatmap Image (fallback) */}
        <div className="bg-gray-50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span>📊</span> Direct Heatmap View
          </h3>
          <div className="rounded-xl overflow-hidden shadow-lg">
            <img
              src={getHeatmapUrl()}
              alt="Grad-CAM Heatmap"
              className="w-full max-w-md mx-auto"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>
        </div>
      </div>
    </div >
  );
}

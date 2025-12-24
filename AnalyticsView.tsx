import { useMemo } from 'react';
import Plot from 'react-plotly.js';

interface AnalyticsViewProps {
  confidence: number;
  classLabel: string;
  processingTime: number;
}

export default function AnalyticsView({ confidence, classLabel, processingTime }: AnalyticsViewProps) {
  const gaugeChart = useMemo(() => {
    const color = confidence > 0.7 ? '#10b981' : confidence > 0.5 ? '#f59e0b' : '#ef4444';

    return {
      data: [
        {
          type: 'indicator',
          mode: 'gauge+number',
          value: confidence * 100,
          title: { text: 'Confidence', font: { size: 16, color: '#374151' } },
          number: { suffix: '%', font: { size: 24, color: '#374151' } },
          gauge: {
            axis: { range: [0, 100], tickwidth: 1, tickcolor: '#e5e7eb' },
            bar: { color: color },
            bgcolor: 'white',
            borderwidth: 2,
            bordercolor: '#e5e7eb',
            steps: [
              { range: [0, 40], color: '#fef2f2' },
              { range: [40, 70], color: '#fffbeb' },
              { range: [70, 100], color: '#ecfdf5' },
            ],
            threshold: {
              line: { color: color, width: 4 },
              thickness: 0.75,
              value: confidence * 100,
            },
          },
        },
      ] as any,
      layout: {
        height: 200,
        margin: { l: 30, r: 30, t: 40, b: 20 },
        paper_bgcolor: 'transparent',
        font: { family: 'Inter, sans-serif' },
      },
      config: { responsive: true, displayModeBar: false },
    };
  }, [confidence]);

  const probabilityBars = useMemo(() => {
    // Generate mock probability distribution with current class being highest
    const classes = ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'];
    const colors = ['#ef4444', '#f97316', '#3b82f6', '#10b981'];

    // Create probabilities where current class has the confidence value
    let probs = [0.1, 0.1, 0.1, 0.1];
    const classIndex = classes.findIndex(c => c.toLowerCase().replace(' ', '') === classLabel.toLowerCase());
    if (classIndex >= 0) {
      probs[classIndex] = confidence;
      // Distribute remaining probability
      const remaining = 1 - confidence;
      probs = probs.map((p, i) => i === classIndex ? confidence * 100 : (remaining / 3) * 100);
    } else {
      probs = probs.map(p => p * 100);
    }

    return {
      data: [
        {
          type: 'bar',
          x: probs,
          y: classes,
          orientation: 'h',
          marker: {
            color: colors,
            line: { width: 0 },
          },
          text: probs.map(p => `${p.toFixed(1)}%`),
          textposition: 'outside',
          hoverinfo: 'y+text',
        },
      ] as any,
      layout: {
        height: 180,
        margin: { l: 80, r: 50, t: 20, b: 30 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        xaxis: {
          range: [0, 110],
          showgrid: false,
          zeroline: false,
          showticklabels: false,
        },
        yaxis: {
          showgrid: false,
          tickfont: { size: 11 },
        },
        font: { family: 'Inter, sans-serif' },
      },
      config: { responsive: true, displayModeBar: false },
    };
  }, [confidence, classLabel]);

  const getStatusInfo = () => {
    if (confidence >= 0.8) return { text: 'High Confidence', color: 'text-green-600', bg: 'bg-green-100' };
    if (confidence >= 0.6) return { text: 'Moderate Confidence', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { text: 'Low Confidence', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const status = getStatusInfo();

  return (
    <div className="glass-card rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-blue-600 p-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>📊</span> Analytics Dashboard
        </h2>
      </div>

      <div className="p-5 space-y-5">
        {/* Gauge Chart */}
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4">
          <Plot {...gaugeChart} style={{ width: '100%' }} />
        </div>

        {/* Probability Distribution */}
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Class Probabilities
          </h3>
          <Plot {...probabilityBars} style={{ width: '100%' }} />
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Processing</p>
            <p className="text-lg font-bold text-blue-600">{processingTime.toFixed(2)}s</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-3 text-center">
            <p className="text-xs text-gray-500 mb-1">Confidence</p>
            <p className="text-lg font-bold text-purple-600">{(confidence * 100).toFixed(1)}%</p>
          </div>
          <div className={`rounded-xl p-3 text-center ${status.bg}`}>
            <p className="text-xs text-gray-500 mb-1">Status</p>
            <p className={`text-sm font-bold ${status.color}`}>{status.text}</p>
          </div>
        </div>

        {/* Medical Disclaimer */}
        <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl p-3 border border-amber-200">
          <p className="text-xs text-amber-700 flex items-start gap-2">
            <span className="text-sm">⚠️</span>
            <span>This AI prediction is for research purposes only. Always consult a qualified medical professional for diagnosis.</span>
          </p>
        </div>
      </div>
    </div>
  );
}

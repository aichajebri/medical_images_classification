# Brain Tumor Analysis Frontend

React + TypeScript frontend for the Brain Tumor Analysis System.

## Tech Stack

- **React 18** with **TypeScript**
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Query** - Data fetching and state management
- **React Router** - Routing
- **Plotly.js** - Data visualizations
- **Canvas API** - Image rendering and manipulation

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build

Create a production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Features

### 1. Patient Management
- Create new patients with:
  - Patient ID (required)
  - Age (optional)
  - Gender (optional)

### 2. Study Management
- Create studies linked to patients
- Set study date and modality (MRI, CT, X-Ray)

### 3. MRI Upload & Prediction
- Upload MRI image files
- Canvas-based image preview
- Automatic prediction via ML model
- Real-time processing status

### 4. Explainability View
- Grad-CAM heatmap overlay visualization
- Shows model attention regions
- Interactive image display

### 5. Results & Analytics
- Prediction results display:
  - Class label (glioma, meningioma, pituitary, notumor)
  - Confidence score
  - Processing time
- Plotly.js visualizations:
  - Confidence score bar chart
  - Class distribution pie chart
- PDF report download

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── PatientForm.tsx
│   │   ├── StudyForm.tsx
│   │   ├── MRIUpload.tsx
│   │   ├── ExplainabilityView.tsx
│   │   ├── ResultsView.tsx
│   │   └── AnalyticsView.tsx
│   ├── pages/               # Page components
│   │   └── WorkflowPage.tsx
│   ├── lib/                 # Utilities and API client
│   │   ├── api.ts           # API client and types
│   │   └── queryClient.ts   # React Query setup
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

- `POST /patients` - Create patient
- `GET /patients` - List patients
- `POST /studies` - Create study
- `POST /predict?study_id={id}` - Upload MRI and get prediction
- `GET /predictions/{id}` - Get prediction details
- `GET /reports/{id}` - Download PDF report

## Workflow

1. **Create Patient** - Enter patient information
2. **Create Study** - Link study to patient
3. **Upload MRI** - Upload image and trigger prediction
4. **View Results** - See prediction, heatmap, and analytics
5. **Download Report** - Get PDF report

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure the backend CORS middleware allows requests from `http://localhost:3000`.

### API Connection
Verify the backend is running:
```bash
curl http://localhost:8000/health
```

### Port Conflicts
If port 3000 is in use, modify `vite.config.ts` to use a different port.

## License

Part of the Brain Tumor Analysis System project.


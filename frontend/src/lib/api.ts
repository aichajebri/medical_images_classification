import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Patient {
  id: number;
  patient_id: string;
  age?: number;
  gender?: string;
  created_at?: string;
}

export interface PatientCreate {
  patient_id: string;
  age?: number;
  gender?: string;
}

export interface Study {
  id: number;
  patient_id: number;
  study_date: string;
  modality: string;
  created_at?: string;
}

export interface StudyCreate {
  patient_id: number;
  study_date: string;
  modality?: string;
}

export interface Prediction {
  id: number;
  image_id: number;
  class_label: string;
  confidence: number;
  heatmap_path: string;
  pdf_report_path: string;
  processing_time: number;
  created_at?: string;
}

export interface PredictionResponse {
  id: number;
  image_id: number;
  class_label: string;
  confidence: number;
  heatmap_path: string;
  pdf_report_path: string;
  processing_time: number;
  created_at?: string;
}

// API Functions
export const patientApi = {
  create: async (data: PatientCreate): Promise<Patient> => {
    const response = await apiClient.post<Patient>('/patients', data);
    return response.data;
  },
  getAll: async (): Promise<Patient[]> => {
    const response = await apiClient.get<Patient[]>('/patients');
    return response.data;
  },
};

export const studyApi = {
  create: async (data: StudyCreate): Promise<Study> => {
    const response = await apiClient.post<Study>('/studies', data);
    return response.data;
  },
};

export const predictionApi = {
  predict: async (studyId: number, file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<PredictionResponse>(
      `/predict?study_id=${studyId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
  getById: async (predictionId: number): Promise<Prediction> => {
    const response = await apiClient.get<Prediction>(`/predictions/${predictionId}`);
    return response.data;
  },
  downloadReport: (predictionId: number): string => {
    return `${API_BASE_URL}/reports/${predictionId}`;
  },
};


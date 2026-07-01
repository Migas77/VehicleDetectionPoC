export interface QosProfile {
    qos_profile_name: string;
    min_ul_bitrate: string;
    max_ul_bitrate: string;
    min_dl_bitrate: string;
    max_dl_bitrate: string;
}

export interface SurveyedAreaPoint {
    latitude: number;
    longitude: number;
}

export interface SurveyedAreaOut {
    radius: number | null;
    points: SurveyedAreaPoint[] | null;
}

export interface CameraInferenceConfig {
    inference_enabled: boolean;
    stream_protocol: string | null;
    stream_ip: string | null;
    stream_port: number | null;
    stream_path: string | null;
    max_fps: number;
}

export interface CameraInfo {
    ue_supi: string;
    qos_profile: QosProfile;
    surveyed_area: SurveyedAreaOut;
    inference: CameraInferenceConfig;
}

export interface InferencePipelineListResponse {
    status: string;
    context: { request_id: string; pipeline_id: string | null };
    pipelines: string[];
}

export interface InferencePreviewOutput {
    type: string;
    value: string;
    video_metadata: {
        video_identifier: string;
        frame_number: number;
        frame_timestamp: string;
    };
}

export interface InferenceDetection {
    x: number;
    y: number;
    width: number;
    height: number;
    confidence: number;
    class_id: number;
    class: string;
    detection_id: string;
    parent_id: string;
}

export interface InferencePredictionsOutput {
    image: { width: number; height: number };
    predictions: InferenceDetection[];
}

export interface InferenceConsumeOutput {
    preview?: InferencePreviewOutput;
    predictions?: InferencePredictionsOutput;
    detections_number?: number;
    frame_number?: number;
}

export interface InferenceConsumeResponse {
    status: string;
    outputs: (InferenceConsumeOutput | null)[];
}

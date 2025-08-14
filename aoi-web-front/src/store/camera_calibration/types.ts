export interface CameraCalibrationState {
    calibrationData: Record<string, any>;
    isCalibrating: boolean;
    calibrationError: string | null;
}

export interface CalibrationPayload {
    cameraId: string;
    data: any;
}
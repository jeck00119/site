
export interface WebCamSettingsModel {
    uid: string | null;
    name: string | null;
    camera_type: string;
    resolution: number[];
    brightness: number;
    contrast: number;
    saturation: number;
    sharpness: number;
    gain: number;
    auto_exposure: number;
    exposure: number;
    pan: number;
    tilt: number;
    zoom: number;
    focus: number;
    auto_focus: number;
}

export interface BaslerSettingsModel {
    uid: string | null;
    camera_type: string;
    name: string;
    exposure: number;
}

export const webCamSettingsModel: WebCamSettingsModel = {
    uid: null,
    name: null,
    camera_type: 'webcam_logi',
    resolution: [480, 640],
    brightness: 128,
    contrast: 128,
    saturation: 128,
    sharpness: 128,
    gain: 0,
    auto_exposure: 0,
    exposure: 1,
    pan: 0,
    tilt: 0,
    zoom: 0,
    focus: 30,
    auto_focus: 1,
};

export const baslerSettingsModel: BaslerSettingsModel = {
    uid: null,
    camera_type: "basler_type",
    name: 'webCam',
    exposure: 30000,
};


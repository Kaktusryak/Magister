export interface SelectOptions {
    value: number,
    displayValue: string
}

export interface Result {
    positions: {
        position: number[],
        orientation: number[],
        distances: (number | null)[]
    }[],
    predictions: PredictionResult[]
}

export interface PredictionResult {
    image: {
        height: string,
        width: string
    },
    predictions: Prediction[]
}

export interface Prediction {
    class: string,
    class_id: number,
    confidence: number,
    detection_id: string,
    image_path: string,
    prediction_type: string,
    height: number,
    width: number,
    x: number,
    y: number
}
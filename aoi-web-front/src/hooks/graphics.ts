import { ref, computed, type Ref, type ComputedRef } from "vue";
import { useStore } from "vuex";
import type { Store } from "vuex";

import graphic from "../utils/graphics";

export interface GraphicData {
    [key: string]: any;
}

export interface Polygon {
    fill: string;
    [key: string]: any;
}

interface CanvasObject {
    set: (props: any) => void;
    [key: string]: any;
}

interface GraphicsHookReturn {
    selectedGraphic: Ref<GraphicData | null>;
    graphicsObject: Ref<any>;
    currentGraphics: ComputedRef<any>;
    graphicItems: ComputedRef<any>;
    canvas: ComputedRef<any>;
    updateGraphics: () => void;
    selectionChanged: (rect: any) => void;
    selectionCleared: () => void;
    selectionModified: (obj: any) => void;
    saveMasks: (polygons: Polygon[]) => void;
}

/**
 * Graphics Hook for managing graphics operations and selections
 * 
 * @returns Hook with graphics state and management functions
 */
export default function useGraphics(): GraphicsHookReturn {
    const store: Store<any> = useStore();

    const selectedGraphic: Ref<GraphicData | null> = ref(null);
    const selectedRect: Ref<any> = ref(null);
    const graphicsObject: Ref<any> = ref(null);

    const currentGraphics: ComputedRef<any> = computed(() => {
        return store.getters["graphics/getCurrentGraphics"];
    });

    const graphicItems: ComputedRef<any> = computed(() => {
        return store.getters["graphics/getCurrentGraphics"];
    });

    const canvas: ComputedRef<any> = computed(() => {
        return store.getters["graphics/getCanvas"];
    });

    /**
     * Update graphics object from current graphics items
     */
    function updateGraphics(): void {
        if (graphicItems.value && canvas.value) {
            graphicsObject.value = graphic.getGraphicsProps(graphicItems.value, canvas.value);
        }
    }

    /**
     * Handle selection change event
     * @param rect - Selected rectangle object
     */
    function selectionChanged(rect: any): void {
        if (rect && canvas.value) {
            const data = graphic.getRectProps(rect, canvas.value);
            
            selectedRect.value = rect;
            selectedGraphic.value = data;
        }
    }

    /**
     * Handle selection cleared event
     */
    function selectionCleared(): void {
        selectedRect.value = null;
        selectedGraphic.value = null;
    }

    /**
     * Handle selection modified event
     * @param obj - Modified graphics object
     */
    function selectionModified(obj: any): void {
        if (obj === selectedRect.value && canvas.value) {
            const data = graphic.getRectProps(obj, canvas.value);
            selectedGraphic.value = data;
        }
    }

    /**
     * Save masks from polygons
     * @param polygons - Array of polygon objects
     */
    function saveMasks(polygons: Polygon[]): void {
        if (!selectedRect.value || !canvas.value) return;

        const masks: number[][][] = [];
        const masksColors: number[][] = [];

        for (const polygon of polygons) {
            const points: number[][] = [];
            const updatedPoints = graphic.getUpdatedPolygonPoints(polygon, canvas.value);

            for (let i = 0; i < updatedPoints.length; i++) {
                points.push([updatedPoints[i].x, updatedPoints[i].y]);
            }

            masks.push(points);

            // Convert hex color to RGB
            const hexColor = polygon.fill;
            const r = parseInt(hexColor.substring(1, 3), 16);
            const g = parseInt(hexColor.substring(3, 5), 16);
            const b = parseInt(hexColor.substring(5, 7), 16);

            masksColors.push([r, g, b]);
        }

        selectedRect.value.set({ masks: masks, masksColors: masksColors });

        const data = graphic.getRectProps(selectedRect.value, canvas.value);
        selectedGraphic.value = data;
    }

    return {
        selectedGraphic,
        graphicsObject,
        currentGraphics,
        graphicItems,
        canvas,
        updateGraphics,
        selectionChanged,
        selectionCleared,
        selectionModified,
        saveMasks
    };
}
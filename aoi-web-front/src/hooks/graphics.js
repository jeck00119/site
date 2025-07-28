import { ref, computed } from "vue";
import { useStore } from "vuex";

import graphic from "../utils/graphics";

export default function useGraphics() {
    const store = useStore();

    const selectedGraphic = ref(null);
    const selectedRect = ref(null);

    const graphicsObject = ref(null);

    const currentGraphics = computed(function () {
        return store.getters["graphics/getCurrentGraphics"];
    });

    const graphicItems = computed(function() {
        return store.getters["graphics/getCurrentGraphics"];
    });

    const canvas = computed(function() {
        return store.getters["graphics/getCanvas"];
    });

    function updateGraphics() {
        graphicsObject.value = graphic.getGraphicsProps(graphicItems.value, canvas.value);
    }

    function selectionChanged(rect) {
        let data = graphic.getRectProps(rect, canvas.value);

        selectedRect.value = rect;
        selectedGraphic.value = data;
    }

    function selectionCleared() {
        selectedRect.value = null;
        selectedGraphic.value = null;
    }

    function selectionModified(obj) {
        if (obj === selectedRect.value) {
            let data = graphic.getRectProps(obj, canvas.value);

            selectedGraphic.value = data;
        }
    }

    function saveMasks(polygons) {
        const masks = [];
        const masksColors = [];

        for (const polygon of polygons) {
            const points = [];

            const updatedPoints = graphic.getUpdatedPolygonPoints(polygon, canvas.value);

            for (let i = 0; i < updatedPoints.length; i++) {
                points.push([updatedPoints[i].x, updatedPoints[i].y]);
            }

            masks.push(points);

            let hexColor = polygon.fill;

            let r = parseInt(hexColor.substring(1, 3), 16);
            let g = parseInt(hexColor.substring(3, 5), 16);
            let b = parseInt(hexColor.substring(5, 7), 16);

            masksColors.push([r, g, b]);
        }
        selectedRect.value.set({ masks: masks, masksColors: masksColors })

        let data = graphic.getRectProps(selectedRect.value, canvas.value);
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
    }
}
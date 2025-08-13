/**
 * Canvas Registry
 * Manages Fabric.js canvas instances outside of Vuex to avoid strict mode violations
 */

import type { Canvas } from 'fabric';

class CanvasRegistry {
    private canvases = new Map<string, Canvas>();
    private activeCanvasId: string | null = null;

    register(id: string, canvas: Canvas): void {
        this.canvases.set(id, canvas);
    }

    unregister(id: string): void {
        this.canvases.delete(id);
        if (this.activeCanvasId === id) {
            this.activeCanvasId = null;
        }
    }

    get(id: string): Canvas | undefined {
        return this.canvases.get(id);
    }

    setActive(id: string): void {
        if (this.canvases.has(id)) {
            this.activeCanvasId = id;
        }
    }

    getActive(): Canvas | null {
        return this.activeCanvasId ? this.canvases.get(this.activeCanvasId) || null : null;
    }

    clear(): void {
        this.canvases.clear();
        this.activeCanvasId = null;
    }
}

export const canvasRegistry = new CanvasRegistry();
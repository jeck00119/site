import * as fabric from 'fabric';

export interface RectAlgIOOptions {
    rectType?: string;
    label?: string;
    valueType?: string;
    index?: number;
    [key: string]: any; // Allow any additional Fabric.js properties
}

export interface GraphicsRectOptions {
    masks?: any[];
    masksColors?: any[];
    [key: string]: any; // Allow any additional Fabric.js properties
}

export class RectAlgIO extends fabric.Rect {
    public rectType: string;
    public label: string;
    public valueType: string;
    public index: number;

    constructor(options: RectAlgIOOptions = {}) {
        super(options as any);
        this.type = 'rectAlgIO';
        this.rectType = options.rectType || 'input';
        this.label = options.label || '';
        this.valueType = options.valueType || '';
        this.index = options.index || 0;
    }

    toObject(propertiesToInclude?: any[]): any {
        return {
            ...super.toObject(propertiesToInclude as any),
            rectType: this.rectType,
            label: this.label,
            valueType: this.valueType,
            index: this.index
        };
    }

    _render(ctx: CanvasRenderingContext2D): void {
        super._render(ctx);
        ctx.font = '15px Helvetica';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.fillText(this.label, 0, 0);
    }
}

export class GraphicsRect extends fabric.Rect {
    public masks: any[];
    public masksColors: any[];

    constructor(options: GraphicsRectOptions = {}) {
        super(options as any);
        this.masks = options.masks || [];
        this.masksColors = options.masksColors || [];
    }

    toObject(propertiesToInclude?: any[]): any {
        return {
            ...super.toObject(propertiesToInclude as any),
            masks: this.masks,
            masksColors: this.masksColors
        };
    }
}

// Custom object creation helper
export function createCustomFabricObject(object: any): fabric.Object | null {
    if (object.type === 'rectAlgIO') {
        return new RectAlgIO(object);
    }
    // Return null to let Fabric handle other types normally
    return null;
}

export default {
    RectAlgIO,
    GraphicsRect
};
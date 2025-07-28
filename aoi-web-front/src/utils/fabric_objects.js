import * as fabric from 'fabric';

class RectAlgIO extends fabric.Rect {
    constructor(options = {}) {
        super(options);
        this.type = 'rectAlgIO';
        this.rectType = options.rectType || 'input';
        this.label = options.label || '';
        this.valueType = options.valueType || '';
        this.index = options.index || 0;
    }

    toObject(propertiesToInclude) {
        return {
            ...super.toObject(propertiesToInclude),
            rectType: this.rectType,
            label: this.label,
            valueType: this.valueType,
            index: this.index
        };
    }

    _render(ctx) {
        super._render(ctx);
        ctx.font = '15px Helvetica';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.fillText(this.label, 0, 0);
    }
}

class GraphicsRect extends fabric.Rect {
    constructor(options = {}) {
        super(options);
        this.masks = options.masks || [];
        this.masksColors = options.masksColors || [];
    }

    toObject(propertiesToInclude) {
        return {
            ...super.toObject(propertiesToInclude),
            masks: this.masks,
            masksColors: this.masksColors
        };
    }
}

export { RectAlgIO, GraphicsRect }
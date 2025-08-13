import * as fabric from 'fabric';

export interface GraphicData {
    bound: [number, number, number, number]; // [x, y, width, height]
    rect: [number, number, number, number];  // [x, y, width, height]
    rotation: number;
    offset: [number, number]; // [offsetX, offsetY]
    color: string;
    masks?: any;
    masksColors?: any;
}

export interface GraphicProps {
    fill: string;
    angle: number;
    width: number;
    height: number;
    scaleX: number;
    scaleY: number;
    masks?: any;
    masksColors?: any;
    getBoundingRect(): fabric.Rect;
    aCoords: {
        tl: { x: number; y: number };
        br: { x: number; y: number };
    };
}

export default {
    getGraphicsProps(graphicItems: Record<string, GraphicProps>, canvas: fabric.Canvas): GraphicData[] {
        const data: GraphicData[] = [];

        const transformation = fabric.util.qrDecompose(canvas.viewportTransform);

        for (const key in graphicItems) {
            const color = graphicItems[key].fill;
            const angle = graphicItems[key].angle;

            const boundingRect = graphicItems[key].getBoundingRect();

            const rectBoundI = new fabric.Rect({
                left: (boundingRect.left - transformation.translateX) / transformation.scaleX,
                top: (boundingRect.top - transformation.translateY) / transformation.scaleY,
                width: boundingRect.width / transformation.scaleX,
                height: boundingRect.height / transformation.scaleY,
                objectCaching: false
            });

            rectBoundI.rotate(angle);

            const boundingRectI = rectBoundI.getBoundingRect();

            const topLeft = graphicItems[key].aCoords.tl;
            const bottomRight = graphicItems[key].aCoords.br;

            const xCenter = (topLeft.x + bottomRight.x) / 2;
            const yCenter = (topLeft.y + bottomRight.y) / 2;

            const topLeftRotX = (((topLeft.x - xCenter) * Math.cos((angle * (-1)) * (Math.PI / 180))) - ((topLeft.y - yCenter) * Math.sin((angle * (-1)) * (Math.PI / 180)))) + xCenter;
            const topLeftRotY = (((topLeft.x - xCenter) * Math.sin((angle * (-1)) * (Math.PI / 180))) + ((topLeft.y - yCenter) * Math.cos((angle * (-1)) * (Math.PI / 180)))) + yCenter;

            const offsetX = Math.abs(topLeftRotX - boundingRectI.left);
            const offsetY = Math.abs(topLeftRotY - boundingRectI.top);

            const graphic: GraphicData = {
                bound: [(boundingRect.left - transformation.translateX) / transformation.scaleX, (boundingRect.top - transformation.translateY) / transformation.scaleY, boundingRect.width / transformation.scaleX, boundingRect.height / transformation.scaleY],
                rect: [topLeftRotX, topLeftRotY, graphicItems[key].width * graphicItems[key].scaleX, graphicItems[key].height * graphicItems[key].scaleY],
                rotation: angle,
                offset: [offsetX, offsetY],
                color: color,
                masks: graphicItems[key].masks,
                masksColors: graphicItems[key].masksColors
            };

            data.push(graphic);
        }

        return data;
    },

    getRectProps(graphicRect: GraphicProps, canvas: fabric.Canvas): GraphicData {
        const transformation = fabric.util.qrDecompose(canvas.viewportTransform);

        const color = graphicRect.fill;
        const angle = graphicRect.angle;

        const boundingRect = graphicRect.getBoundingRect();

        const rectBoundI = new fabric.Rect({
            left: (boundingRect.left - transformation.translateX) / transformation.scaleX,
            top: (boundingRect.top - transformation.translateY) / transformation.scaleY,
            width: boundingRect.width / transformation.scaleX,
            height: boundingRect.height / transformation.scaleY,
            objectCaching: false
        });

        rectBoundI.rotate(angle);

        const boundingRectI = rectBoundI.getBoundingRect();

        const topLeft = graphicRect.aCoords.tl;
        const bottomRight = graphicRect.aCoords.br;

        const xCenter = (topLeft.x + bottomRight.x) / 2;
        const yCenter = (topLeft.y + bottomRight.y) / 2;

        const topLeftRotX = (((topLeft.x - xCenter) * Math.cos((angle * (-1)) * (Math.PI / 180))) - ((topLeft.y - yCenter) * Math.sin((angle * (-1)) * (Math.PI / 180)))) + xCenter;
        const topLeftRotY = (((topLeft.x - xCenter) * Math.sin((angle * (-1)) * (Math.PI / 180))) + ((topLeft.y - yCenter) * Math.cos((angle * (-1)) * (Math.PI / 180)))) + yCenter;

        const offsetX = Math.abs(topLeftRotX - boundingRectI.left);
        const offsetY = Math.abs(topLeftRotY - boundingRectI.top);

        const graphic: GraphicData = {
            bound: [(boundingRect.left - transformation.translateX) / transformation.scaleX, (boundingRect.top - transformation.translateY) / transformation.scaleY, boundingRect.width / transformation.scaleX, boundingRect.height / transformation.scaleY],
            rect: [topLeftRotX, topLeftRotY, graphicRect.width * graphicRect.scaleX, graphicRect.height * graphicRect.scaleY],
            rotation: angle,
            offset: [offsetX, offsetY],
            color: color,
            masks: graphicRect.masks,
            masksColors: graphicRect.masksColors
        };

        return graphic;
    },

    getUpdatedPolygonPoints(polygon: any, canvas: fabric.Canvas): fabric.Point[] {
        const matrix = polygon.calcTransformMatrix();

        let transformedPoints = polygon.get('points').map(function(p: any) {
            return new fabric.Point(p.x - polygon.pathOffset.x, p.y - polygon.pathOffset.y);
        }).map(function(p: fabric.Point) {
            return fabric.util.transformPoint(p, matrix);
        });

        return transformedPoints;
    }
};
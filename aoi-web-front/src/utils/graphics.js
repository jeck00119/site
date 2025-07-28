import * as fabric from 'fabric';

export default {
    getGraphicsProps(graphicItems, canvas) {
        const data = [];

        const transformation = fabric.util.qrDecompose(canvas.viewportTransform);

        for (const key in graphicItems) 
        {
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

            const graphic = {
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

    getRectProps(graphicRect, canvas) {
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

        const graphic = {
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

    getUpdatedPolygonPoints(polygon, canvas) {
        const matrix = polygon.calcTransformMatrix();

        let transformedPoints = polygon.get('points').map(function(p) {
            return new fabric.Point(p.x - polygon.pathOffset.x, p.y - polygon.pathOffset.y);
        }).map(function(p) {
            return fabric.util.transformPoint(p, matrix);
        });

        return transformedPoints;
    },

    cropImage(image, graphics) {
        if(image)
        {
            let width = image.width;
            let height = image.height;

            image.rotate(-graphics.rotation);

            image.set({
                clipPath:  new fabric.Rect({
                    left: (graphics.bound[0] + graphics.offset[0]) - width / 2,
                    top: (graphics.bound[1] + graphics.offset[1]) - height / 2,
                    width: graphics.rect[2],
                    height: graphics.rect[3]
                })
            });

            // image.set({
            //     width: graphics.bound[2],
            //     height: graphics.bound[3]
            // });
    
            // image.rotate(graphics.rotation);
    
            // image.set({
            //     left: graphics.offset[0],
            //     top: graphics.offset[1],
            //     width: graphics.rect[2],
            //     height: graphics.rect[3],
            //     clipPath:  new fabric.Rect({
            //         left: 0,
            //         top: 0,
            //         width: graphics.rect[2],
            //         height: graphics.rect[3]
            //     })
            // });
        }
        
        return image;
    }
}
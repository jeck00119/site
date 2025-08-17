import { ref, computed } from "vue";
import { v4 as uuidv4 } from "uuid";
import { useStore, useWebSocket, useAlgorithmsStore, useErrorsStore } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '@/utils/imageConstants';
import { logger } from '@/utils/logger';

import graphic from '../utils/graphics.js';

export default function useAlgorithms(algorithmUid: any, referenceUid: any, currentImageSourceId: any, moduleName: any, graphicsObject: any, ipAddress: any, port: any) {
    const { store } = useStore(); // Keep for backward compatibility with remaining store calls
    const { 
        configuredAlgorithms,
        referenceAlgorithms,
        algorithms: allAlgorithms,
        currentAlgorithm: currentAlgorithmFromStore,
        algorithmAttributes: currentAlgorithmAttributes
    } = useAlgorithmsStore();
    const errorStore = useErrorsStore();

    const loadedAlgorithm = ref(null);
    const algorithmTypeId = ref('');
    const algIsConfigured = ref(false);

    const currentAlgorithmInitial = ref(null);
    let liveProcessSocket: any = null; // Will hold the WebSocket composable instance

    const algorithms = computed(function() {
        // For ComponentsConfiguration, return all available algorithm types (not configured ones)
        // For ReferencesConfiguration, return reference algorithms
        // For other use cases, fall back to algorithm types
        if (moduleName === 'component') {
            return allAlgorithms.value || [];
        } else if (moduleName === 'reference') {
            return referenceAlgorithms.value || [];
        } else {
            return allAlgorithms.value || [];
        }
    });

    const currentAlgorithm = computed(function() {
        return currentAlgorithmFromStore.value;
    });

    const algorithmAttributes = computed(function() {
        return currentAlgorithmAttributes.value;
    });

    const parameters = computed(function() {
        if(currentAlgorithm.value)
            return currentAlgorithm.value.parameters;
        else
            return [];
    });

    const resultImage = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        if(result && result.frame)
        {
            if(Array.isArray(result.frame) && result.frame.length === 0)
            {
                return '';
            }
            else if(Array.isArray(result.frame))
            {
                return result.frame[0];
            }
            else
            {
                // Handle single frame case
                return result.frame;
            }
        }
        return '';
    });

    const outputImages = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        let outputImages = [];
        if(result && result.frame)
        {
            outputImages = Array.isArray(result.frame) ? result.frame : [result.frame];
        }
        logger.debug('outputImages computed:', { count: outputImages.length });
        return outputImages;
    });

    const data = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        return result ? result.data : null;
    });

    function setAlgorithmConfigured() {
        algIsConfigured.value = true;
    }

    async function loadUIandAlgorithm(type: any, uid: any)
    {
        await store.dispatch("algorithms/loadAlgorithm", {
            type: type
        });

        await store.dispatch("algorithms/setLiveAlgorithm", {
            type: type
        });

        if(algIsConfigured.value)
        {
            await store.dispatch("algorithms/loadCurrentAlgorithm", {
                uid: uid
            });
            algIsConfigured.value = false;
        }
        else
        {
            store.dispatch("algorithms/loadCurrentAlgorithmFromParameters", {
                attributes: algorithmAttributes.value,
                type: type
            });
        }

        currentAlgorithmInitial.value = JSON.parse(JSON.stringify(currentAlgorithm.value.parameters));
    }

    function onAlgorithmChanged(id: any){
        algorithmTypeId.value = id;

        const algorithm = store.getters["algorithms/getAlgorithmById"](id);

        if(algorithm)
        {
            // Extract the actual string value from the reactive ref
            const algorithmUidValue = algorithmUid?.value || algorithmUid;
            loadUIandAlgorithm(algorithm.type, algorithmUidValue);

            if(loadedAlgorithm.value)
            {
                store.dispatch("algorithms/loadCurrentAlgorithmFromObject", (loadedAlgorithm.value as any).parameters);
                loadedAlgorithm.value = null;
            }
        }
        else
        {
            store.dispatch("algorithms/setCurrentAlgorithm", null);
            store.dispatch("algorithms/setCurrentAlgorithmAttributes", []);
            store.dispatch("graphics/resetGraphicsItems", {});
            store.dispatch("algorithms/setAlgorithmResult", null);
        }
    }

    function onImportPathChanged(path: any) {
        let fileread = new FileReader();
        fileread.onload = function(e: any) {
            let content = e.target?.result as string;
            loadedAlgorithm.value = JSON.parse(content);

            const algorithm = store.getters["algorithms/getAlgorithmByType"]((loadedAlgorithm.value as any).type);

            if(algorithm !== undefined)
            {
                if(algorithm.uid === algorithmTypeId.value)
                {
                    store.dispatch("algorithms/loadCurrentAlgorithmFromObject", (loadedAlgorithm.value as any).parameters);
                    loadedAlgorithm.value = null;
                }
                else
                {
                    algorithmTypeId.value = algorithm.uid;
                }
            }
        };

        fileread.readAsText(path);
    }

    function download(algorithm: any){
        let text = JSON.stringify(algorithm);
        const currentDate = new Date();

        let suffix = currentDate.getDate() + "_" + (currentDate.getMonth() + 1) + "_"
            + currentDate.getFullYear() + "_" + currentDate.getHours() + "_"
            + currentDate.getMinutes() + "_" + currentDate.getSeconds() + ".json";

        let filename = algorithm.type.replace(/\s/g, '') + suffix;

        let element = document.createElement('a');
        element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();
        document.body.removeChild(element);
    }

    async function saveAlgorithm() {
        const algorithm = store.getters["algorithms/getConfiguredAlgorithmById"](currentAlgorithm.value.uid);

        if(algorithm)
        {
            await store.dispatch("algorithms/updateConfiguredAlgorithm", currentAlgorithm.value);
        }
        else
        {
            await store.dispatch("algorithms/addConfiguredAlgorithm", currentAlgorithm.value);
        }
    }

    async function singleRunAlgorithm(imageSourceUid: any) {
        const graphicItems = store.getters["graphics/getCurrentGraphics"];
        const canvas = store.getters["graphics/getCanvas"];

        const data = graphic.getGraphicsProps(graphicItems, canvas);

        await store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
            name: 'graphics',
            value: data
        });

        if(referenceUid !== '')
        {
            await store.dispatch("algorithms/setLiveAlgorithmReferenceRepository", {
                id: referenceUid
            });
        }
       
        store.dispatch("algorithms/singleProcessAlgorithmCamera", {
            uid: imageSourceUid,
            type: moduleName
        }).catch((err: any) => {    
            store.dispatch("errors/addError", {
                id: uuidv4(),
                title: "Component Run Error",
                description: err
            });
        });
    }

    async function liveProcessAlgorithm(state: any) {
        if(state)
        {
            const graphicItems = store.getters["graphics/getCurrentGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            const data = graphic.getGraphicsProps(graphicItems, canvas);

            await store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
                name: 'graphics',
                value: data
            });

            await store.dispatch("algorithms/setLiveAlgorithmReference", {
                id: referenceUid
            });

            let id = uuidv4();

            let url = `ws://${ipAddress}:${port}/algorithm/live_algorithm_result/${currentImageSourceId}/${id}/ws`;

            // Use centralized WebSocket composable
            liveProcessSocket = useWebSocket(url, {
                autoConnect: true,
                reconnectAttempts: 3,
                reconnectInterval: 2000,
                onOpen: onSocketOpen,
                onMessage: liveResultMsgRecv
            });
        }
        else
        {
            if(liveProcessSocket)
            {
                liveProcessSocket.send(JSON.stringify({command: "disconnect"}));
                liveProcessSocket.disconnect();
                liveProcessSocket = null;
            }
        }
    }

    function onSocketOpen() {
        if(liveProcessSocket)
        {
            liveProcessSocket.send(JSON.stringify({
                command: ''
            }));
        }
    }

    function liveResultMsgRecv(event: any) {
        let recvData = JSON.parse(event.data);

        let outputImages = [];
        if (recvData.frame && Array.isArray(recvData.frame)) {
            for(const frame of recvData.frame)
            {
                outputImages.push(ImageDataUtils.createJpegDataURI(frame));
            }
        } else {
            // Handle single frame or undefined case
            if (recvData.frame) {
                outputImages.push(ImageDataUtils.createJpegDataURI(recvData.frame));
            }
        }

        store.dispatch("algorithms/setAlgorithmResult", {
            frame: outputImages,
            data: recvData.data
        });

        if(graphicsObject.value)
        {
            liveProcessSocket.send(JSON.stringify({
                command: 'set',
                key: 'graphics',
                value: graphicsObject.value
            }));
            graphicsObject.value = null;
        }
        else
        {
            liveProcessSocket.send(JSON.stringify({command: ''}));
        }
    }

    function setLiveAlgorithmSocket(socket: any) {
        liveProcessSocket = socket;
    }

    return {
        algorithmTypeId,
        algorithms,
        currentAlgorithm,
        algorithmAttributes,
        parameters,
        resultImage,
        outputImages,
        data,
        loadUIandAlgorithm,
        setAlgorithmConfigured,
        onAlgorithmChanged,
        download,
        saveAlgorithm,
        singleRunAlgorithm,
        liveProcessAlgorithm,
        liveResultMsgRecv,
        setLiveAlgorithmSocket
    }
}
import { ref, computed } from "vue";
import { useStore } from "vuex";
import { uuid } from "vue3-uuid";

import graphic from '../utils/graphics.js';

export default function useAlgorithms(algorithmUid, referenceUid, currentImageSourceId, moduleName, graphicsObject, ipAddress, port) {
    const store = useStore();

    const loadedAlgorithm = ref(null);
    const algorithmTypeId = ref('');
    const algIsConfigured = ref(false);

    const currentAlgorithmInitial = ref(null);
    let liveProcessSocket = null;

    const algorithms = computed(function() {
        return store.getters["algorithms/getAlgorithms"];
    });

    const currentAlgorithm = computed(function() {
        return store.getters["algorithms/getCurrentAlgorithm"];
    });

    const algorithmAttributes = computed(function() {
        return store.getters["algorithms/getCurrentAlgorithmAttributes"];
    });

    const parameters = computed(function() {
        if(currentAlgorithm.value)
            return currentAlgorithm.value.parameters;
        else
            return [];
    });

    const resultImage = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        if(result)
        {
            if(result.frame.length === 0)
            {
                return '';
            }
            else
            {
                return result.frame[0];
            }
        }
        return '';
    });

    const outputImages = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        let outputImages = [];
        if(result)
        {
            outputImages = result.frame;
        }
        return outputImages;
    });

    const data = computed(function() {
        const result = store.getters["algorithms/getAlgorithmResult"];
        return result ? result.data : null;
    });

    function setAlgorithmConfigured() {
        algIsConfigured.value = true;
    }

    async function loadUIandAlgorithm(type, uid)
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

    function onAlgorithmChanged(id){
        algorithmTypeId.value = id;

        const algorithm = store.getters["algorithms/getAlgorithmById"](id);

        if(algorithm)
        {
            loadUIandAlgorithm(algorithm.type, algorithmUid.value);

            if(loadedAlgorithm.value)
            {
                store.dispatch("algorithms/loadCurrentAlgorithmFromObject", loadedAlgorithm.value.parameters);
                loadedAlgorithm.value = null;
            }
        }
        else
        {
            store.dispatch("algorithms/setCurrentAlgorithm", null);
            store.dispatch("algorithms/setCurrentAlgorithmAttributes", []);
            store.dispatch("graphics/resetGraphicsItems");
            store.dispatch("algorithms/setAlgorithmResult", null);
        }
    }

    function onImportPathChanged(path) {
        let fileread = new FileReader();
        fileread.onload = function(e) {
            let content = e.target.result;
            loadedAlgorithm.value = JSON.parse(content);

            const algorithm = store.getters["algorithms/getAlgorithmByType"](loadedAlgorithm.value.type);

            if(algorithm !== undefined)
            {
                if(algorithm.uid === algorithmTypeId.value)
                {
                    store.dispatch("algorithms/loadCurrentAlgorithmFromObject", loadedAlgorithm.value.parameters);
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

    function download(algorithm){
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

    async function singleRunAlgorithm(imageSourceUid) {
        const graphicItems = store.getters["graphics/getCurrentGraphics"];
        const canvas = store.getters["graphics/getCanvas"];

        const data = graphic.getGraphicsProps(graphicItems, canvas);

        await store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
            name: 'graphics',
            value: data
        });

        if(referenceUid.value !== '')
        {
            await store.dispatch("algorithms/setLiveAlgorithmReferenceRepository", {
                id: referenceUid.value
            });
        }
       
        store.dispatch("algorithms/singleProcessAlgorithmCamera", {
            uid: imageSourceUid,
            type: moduleName
        }).catch((err) => {    
            store.dispatch("errors/addError", {
                id: uuid.v4(),
                title: "Component Run Error",
                description: err
            });
        });
    }

    async function liveProcessAlgorithm(state) {
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
                id: referenceUid.value
            });

            let id = uuid.v4();

            let url = `ws://${ipAddress}:${port}/algorithm/live_algorithm_result/${currentImageSourceId.value}/${id}/ws`;

            liveProcessSocket = new WebSocket(url);

            liveProcessSocket.addEventListener('open', onSocketOpen);
            liveProcessSocket.addEventListener('message', liveResultMsgRecv);
        }
        else
        {
            if(liveProcessSocket)
            {
                liveProcessSocket.send(JSON.stringify({command: "disconnect"}));

                liveProcessSocket.removeEventListener('open', onSocketOpen);
                liveProcessSocket.removeEventListener('message', liveResultMsgRecv);

                liveProcessSocket.close();
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

    function liveResultMsgRecv(event) {
        let recvData = JSON.parse(event.data);

        let outputImages = [];
        for(const frame of recvData.frame)
        {
            outputImages.push('data:image/png;base64,' + frame);
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

    function setLiveAlgorithmSocket(socket) {
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
        currentAlgorithmInitial,
        setAlgorithmConfigured,
        loadUIandAlgorithm,
        onAlgorithmChanged,
        onImportPathChanged,
        download,
        saveAlgorithm,
        singleRunAlgorithm,
        liveProcessAlgorithm,
        liveResultMsgRecv,
        setLiveAlgorithmSocket
    }
}
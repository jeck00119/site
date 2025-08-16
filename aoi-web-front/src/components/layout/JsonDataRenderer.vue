<template>
    <div class="flex-container" :style="{width: width, height: height}">
        <div class="json-container">
            <json-viewer :value="data" :showDoubleQuotes="true" :copyable="false" theme="jv-dark" :style="{width: '100%', height: '100%'}">
            </json-viewer>
        </div>
        <div class="close">
            <button @click="close()">&#10006;</button>
        </div>
    </div>
</template>

<script>
import VueJsonPretty from 'vue-json-pretty';
import JsonViewer from 'vue-json-viewer';

export default{
    components: {
        VueJsonPretty,
        JsonViewer
    },

    props: ['width', 'height', 'data'],

    emits: ['closed'],

    setup(props, context) {
        function close() {
            context.emit('closed');
        }

        return {
            close
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: start;
    width: 100%;
    color: white;
}

.close {
    position: absolute;
    top: 0;
    right: 0;
}

.close > button {
    background-color: inherit;
    border: none;
}

.close > button:hover {
    border: none;
}

.json-container {
    min-height: 100%;
    /* overflow-y: auto; - moved scrolling to body level */
    width: 100%;
    /* display: flex; */
    background-color: rgb(21, 20, 20);
    text-align: left; /* Ensure text alignment is set to left */
    margin: 0;
    padding: 0;
}
</style>
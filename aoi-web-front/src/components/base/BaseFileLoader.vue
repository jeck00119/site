<template>
    <div :data-active="active" @dragenter.prevent="setActive" @dragover.prevent="setActive"
    @dragleave.prevent="setInactive" @drop.prevent="onDrop" :style="{width: width, height: height}">
        <slot></slot>
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
    props: ['path', 'update', 'width', 'height'],

    emits: ['files-dropped'],

    setup(props, context) {
        const active = ref(false);
        const events = ['dragenter', 'dragover', 'dragleave', 'drop'];

        let inActiveTimeout = null;

        function setActive() {
            active.value = true;
            clearTimeout(inActiveTimeout)
        }

        function setInactive() {
            inActiveTimeout = setTimeout(() => {
                active.value = false
            }, 50);
        }

        function onDrop(e) {
            setInactive();
            context.emit('files-dropped', props.path, props.update, [...e.dataTransfer.files]);
        }

        function preventDefaults(e) {
            e.preventDefault()
        }

        onMounted(() => {
            events.forEach((eventName) => {
                document.body.addEventListener(eventName, preventDefaults)
            })
        });

        onUnmounted(() => {
            events.forEach((eventName) => {
                document.body.removeEventListener(eventName, preventDefaults)
            })
        });

        return {
            active,
            onDrop,
            setActive,
            setInactive
        }
    }
}
</script>

<style scoped>
div {
    width: 100%;
    height: 100%;
    background-color: black;
    border-radius: 10px;
}
</style>
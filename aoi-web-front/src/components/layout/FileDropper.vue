<template>
    <div :data-active="active" @dragenter.prevent="setActive" @dragover.prevent="setActive"
    @dragleave.prevent="setInactive" @drop.prevent="onDrop">
        <slot></slot>
    </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue'

export default {
    emits: ['files-dropped', 'state-changed'],

    setup(_, context) {
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
            context.emit('files-dropped', [...e.dataTransfer.files]);
        }

        function preventDefaults(e) {
            e.preventDefault()
        }

        watch(active, (newValue) => {
            context.emit('state-changed', newValue);
        });

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
}
</style>
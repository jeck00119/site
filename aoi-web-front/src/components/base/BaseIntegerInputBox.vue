<template>
    <input type="number" :min="min" :max="max" :step="step" :value="current" @input="handleInput" :style="{width: width}">
</template>

<script>
import { watch } from 'vue';

export default {
    props: ['min', 'max', 'step', 'name', 'current', 'width'],
    emits: ['update-value'],

    setup(props, context){
        const handleInput = (event) => {
            context.emit('update-value', props.name, parseInt(event.target.value));
        };

        return {
            handleInput
        };
    }
};
</script>

<style scoped>
    input {
        border: none;
        background-color: rgb(41, 41, 41);
        color: white;
    }
</style>
<template>
    <input class="slider-range" id="slider" type="range" :min="min" :max="max" :step="step" 
    :value="current" @input="handleInput" :style="{width: width}">
</template>

<script>
import { watch, onMounted, ref, toRef } from 'vue';


export default {
    props: ['min', 'max', 'step', 'name', 'current', 'width', 'icon'],
    emits: ['update-value'],

    setup(props, context){
        
        const handleInput = (event) => {
            context.emit('update-value', props.name, event.target.value);
        };

        return {
            handleInput
        };
    },

    
};
</script>

<style scoped>

    .slider-range {
        -webkit-appearance: none;
        height: 7px;
        border-radius: 5px;  
        background: rgb(41, 41, 41);
        outline: none;
        opacity: 1.0;
        -webkit-transition: .2s;
        transition: opacity .2s;
    }

    .slider-range::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 25px;
        height: 25px;
        border-radius: 50%; 
        background-color: rgba(204, 161, 82);
        border:none;
        cursor: pointer;
    }

    .slider-range::-moz-range-thumb {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        background-color: rgba(204, 161, 82);
        border:none;
        cursor: pointer;
    }

    .slider-range::-moz-range-thumb:hover {
        transform:scale(1.2);

    }
</style>
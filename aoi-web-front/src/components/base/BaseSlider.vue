<template>
    <input class="slider-range" id="slider" type="range" :min="min" :max="max" :step="step" 
    :value="current" @input="handleInput" :style="{width: width}">
</template>

<script setup lang="ts">
interface Props {
  min: number;
  max: number;
  step: number;
  name: string;
  current: number;
  width?: string;
  icon?: string;
}

interface Emits {
  (e: 'update-value', name: string, value: number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update-value', props.name, Number(target.value));
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
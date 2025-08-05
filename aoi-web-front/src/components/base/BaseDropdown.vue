<template>
    <select :style="{width: width}" v-model="currentValue" :disabled="disabled">
        <option v-for="value in values" :value="value">{{ convertValueToStr(value) }}</option>
    </select>
</template>

<script setup lang="ts">
import { ref, watch, toRef } from 'vue';

interface Props {
  current: string | number;
  values: (string | number)[];
  width?: string;
  name: string;
  disabled?: boolean;
}

interface Emits {
  (e: 'update-value', name: string, value: string | number): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const currentProp = toRef(props, "current");
const currentValue = ref<string | number>(props.current);

watch(currentValue, (newValue) => {
    emit('update-value', props.name, newValue);
});

watch(currentProp, (newValue) => {
    currentValue.value = newValue;
});

function convertValueToStr(val: string | number): string {
    const valAsStr = val.toString();
    
    if (valAsStr.length > 0) {
        return valAsStr[0].toUpperCase() + valAsStr.substring(1);
    } else {
        return valAsStr;
    }
}
</script>

<style scoped>
select {
    background-color: rgb(204, 161, 82);
    padding-left: 0.2vw;
    padding-right: 0.2vw;
    margin: 0;
    border: none;
}
</style>
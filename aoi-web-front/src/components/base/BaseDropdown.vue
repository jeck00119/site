<template>
    <select :style="{width: width}" v-model="currentValue" :disabled="disabled">
        <option v-for="value in values" :value="value">{{ convertValueToStr(value) }}</option>
    </select>
</template>

<script>
import { ref, watch, toRef } from 'vue';

export default {
    props: ['current', 'values', 'width', 'name', 'disabled'],
    emits: ['update-value'],

    setup(props, context){
        const currentProp = toRef(props, "current");
        const currentValue = ref(props.current);

        watch(currentValue, (newValue) => {
            context.emit('update-value', props.name, newValue);
        });

        watch(currentProp, (newValue) => {
            currentValue.value = newValue;
        });

        function convertValueToStr(val) {
            let valAsStr = val.toString();
            
            if(valAsStr.length > 0)
            {
                return valAsStr[0].toUpperCase() + valAsStr.substring(1);
            }
            else
            {
                return valAsStr;
            }
        }

        return {
            currentValue,
            convertValueToStr
        }
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
<template>
    <input type="color" id="picker" name="picker" v-model.lazy="currentValue">
</template>

<script>
import { ref, watch, toRef } from 'vue';

export default {
    props: ['current', 'width', 'name', 'disabled'],
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

        return {
            currentValue
        }
    }
}
</script>

<style scoped>
input {
    padding-left: 0.2vw;
    padding-right: 0.2vw;
    margin: 0;
}
</style>
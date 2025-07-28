<template>
    <button :class="buttonClass" @click="switchState" :style="{width: width, height: height, fontSize: fontSize}">
        <slot></slot>
    </button>
</template>

<script>
import { ref, watch, computed } from 'vue';

export default {
    props: ["mode", "active", "showActive", 'width', 'height', 'fontSize'],

    emits: ["state-changed"],

    setup(props, context) {
        const isActive = ref(props.active);

        function switchState() {
            isActive.value = !isActive.value;

            context.emit('state-changed', isActive.value);
        };

        watch(props, () => {
            isActive.value = props.active;
        });

        const buttonClass = computed(function() {
            return {
                'flat': props.mode === 'flat',
                'active': isActive.value && props.showActive
            }
        });

        return {
            buttonClass,
            switchState
        }
    }
}
</script>

<style scoped>
button {
  text-decoration: none;
  font: inherit;
  background-color: black;
  border: 1px solid black;
  color: rgba(204, 161, 82);
  cursor: pointer;
  border-radius: 30px;
  display: inline-block;
}

button:hover,
button:active {
  background-color: rgb(32, 31, 31);
  border-color: rgb(32, 31, 31);
}

button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.flat {
  background-color: rgba(204, 161, 82);
  color: black;
  border: none;
}

.outline {
  background-color: transparent;
  border-color: rgb(32, 31, 31);
  color: rgb(32, 31, 31);
}

.active {
    background-color: rgba(204, 161, 82);
    color: black;
}

.active:hover {
    background-color: rgb(251, 197, 97);
}

.flat:hover,
.flat:active,
.outline:hover,
.outline:active {
  background-color: rgb(251, 197, 97);
}
</style>
<template>
    <button :class="{'active': mode === 'flat'}" :style="{width: width, height: height, fontSize: fontSize}">
        <slot></slot>
    </button>
</template>

<script setup lang="ts">
interface Props {
  mode?: 'flat' | 'outline' | string;
  width?: string;
  height?: string;
  fontSize?: string;
}

defineProps<Props>();
</script>

<style scoped>
button {
  text-decoration: none;
  /* padding: 0.25rem 0.5rem; */
  font: inherit;
  background-color: black;
  /* border: 1px solid rgb(84, 82, 82); */
  color: rgba(204, 161, 82);
  cursor: pointer;
  border-radius: 30px;
  /* display: inline-block; */
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
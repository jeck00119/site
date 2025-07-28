<template>
    <div class="card" :style="{width: width, height: height}">
        <slot></slot>
    </div>
</template>

<script>
export default {
  props: ['width', 'height']
}
</script>

<style scoped>

.card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
  /* padding: 1rem; */
  /* max-width: 40rem; */
  background-color: rgb(56, 51, 51);
  padding: 1px;
  /* background-color: rgb(200, 120, 23); */
  /* width: 100%;
  height: 100%; */
}

</style>
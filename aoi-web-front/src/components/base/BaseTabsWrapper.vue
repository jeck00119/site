<template>
    <div class="tabs">
        <ul class="tabs-header">
            <li v-for="title in tabTitles" :key="title" @click="selectedTitle = title" :class="{'selected': title === selectedTitle}">
                {{ title }}
            </li>
        </ul>
        <slot></slot>
    </div>
</template>

<script>
import { ref, watch, provide } from 'vue';

export default {
    emits: ['tab-changed'],

    setup(props, context) {
        const tabTitles = ref(context.slots.default().map(tab => tab.props.title));
        const selectedTitle = ref(tabTitles.value[0]);

        watch(selectedTitle, (newValue) => {
            context.emit('tab-changed', newValue);
        });

        provide("selectedTitle", selectedTitle);

        return{
            selectedTitle,
            tabTitles
        }
    }
}
</script>

<style scoped>
.tabs {
    width: 100%;
    margin: 0 auto;
    /* background-color: red; */
    height: 100%;
}

.tabs-header {
    list-style: none;
    padding: 0;
    display: flex;
}

.tabs-header li {
    text-align: center;
    padding: 5px 10px;
    background-color: rgb(0, 0, 0);
    border-radius: 5px;
    cursor: pointer;
    transition: 0.4s all ease-out;
    margin-right: 1px;
    width: 25%;
}

.tabs-header li.selected {
    background-color: rgb(219, 147, 12);
}
</style>
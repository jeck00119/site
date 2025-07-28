<template>
    <div class="container">
        <div class="primary-button-container" @click="toggleVisibiltySubpages">
            <div class="icon-wrapper">
                <div>
                    <font-awesome-icon :icon="iconName"/>
                </div>
            </div>
            <div class="name prevent-select">
                {{ name }}
            </div>
        </div>
        <transition name="fade" mode="out-in">
            <div v-if="showSubPages">
                <div class="sub-page-flex-container">
                    <div class="sub-page-button" v-for="subpage in subpages" @click="sendRouteChanged">
                        <router-link class="prevent-select" :to="'/' + subpage.split(' ').join('-').toLowerCase()">{{ subpage }}</router-link>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import {ref, toRef} from 'vue';

export default{
    props: ['id', 'name', 'subpages', 'iconName', 'showSubPages'],
    emits: ['route-changed', 'collapse'],

    setup(props, context) {
        // const showSubPages = toRef(props, 'showSubPages');

        function toggleVisibiltySubpages() {
            // props.showSubPages.value = !showSubPages.value;
            context.emit('collapse', props.id);
        }

        function sendRouteChanged() {
            context.emit('route-changed');
        }

        return {
            toggleVisibiltySubpages,
            sendRouteChanged
        }
    }
}
</script>

<style scoped>
    .container {
        padding: 0px;
    }
    .primary-button-container {
        height: 10vh;
        border-top: 1px solid rgb(53, 53, 53);
        border-bottom: 1px solid rgb(53, 53, 53);
        color: rgb(204, 161, 82);
        font-weight: 800;
        font-size: 1.5vw;
        display: flex;
        justify-content: flex-start;
        align-items: center;
    }
    
    .primary-button-container:hover {
        cursor: pointer;
        background-color: rgb(204, 161, 82);
        color: black;
    }

    .icon-wrapper {
        height: 5vh;
        margin-left: 1vw;
    }

    .icon {
        height: 5vh;
        margin: 0 1vw 0 1vw;
        padding: 0;
    }

    .name {
        margin-left: 1vw;
    }

    ul {
        list-style-type: none;
    }

    .sub-pages-list-show {
        display: block;
        /* position: absolute; */
    }

    .sub-pages-list-hide {
        display: none;
        /* position: absolute; */
    }

    .sub-page-flex-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .sub-page-button {
        display: flex;
        background-color: rgb(204, 161, 82);
        color: black;
        height: 5vh;
        justify-content: center;
        align-items: center;
        border-bottom: 1px solid black;
    }

    .prevent-select {
        -webkit-user-select: none; /* Safari */
        -ms-user-select: none; /* IE 10 and IE 11 */
        user-select: none;
    }

    .sub-page-button:hover {
        background-color: rgba(204, 161, 82, 0.783);
    }

    a {
        color: black;
        width: 100%;
        height: 100%;
        padding-top: auto;
        padding-bottom: auto;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    a:hover {
        color: black;
    }

    .fade-enter-active {
        transition: all .3s ease-in;
    }
    .fade-leave-active {
        transition: all .3s ease-out;
    }

    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }

    .fade-enter-to,
    .fade-leave-from {
        opacity: 1;
    }
</style>
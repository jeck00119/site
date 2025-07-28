<template>
    <label class="switch">
        <input type="checkbox" :checked="current" @change="handleChange">
        <span class="slider-toggle round"></span>
    </label>
</template>

<script>
import { watch } from 'vue';

export default {
    props: ['width', 'height', 'current', 'name'],
    emits: ['update-value'],

    setup(props, context) {
        function handleChange(event) {
            context.emit('update-value', props.name, event.target.checked);
        }

        return {
            handleChange
        }
    }
}
</script>

<style scoped>
.switch {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 34px;
    /* background-color: #ccc; */
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

/* The slider */
.slider-toggle {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    -webkit-transition: .4s;
    transition: .4s;
}

.slider-toggle:before {
    position: absolute;
    content: "";
    height: 99%;
    width: 50%;
    left: 2%;
    bottom: 1%;
    background-color: white;
    -webkit-transition: .4s;
    transition: .4s;
}

input:checked + .slider-toggle {
    background-color: rgb(204, 161, 82);
}

input:focus + .slider-toggle {
    box-shadow: 0 0 1px rgb(204, 161, 82);
}

input:checked + .slider-toggle:before {
    -webkit-transform: translateX(90%);
    -ms-transform: translateX(90%);
    transform: translateX(90%);
}

/* Rounded sliders */
.slider-toggle.round {
    border-radius: 34px;
}

.slider-toggle.round:before {
    border-radius: 50%;
}
</style>
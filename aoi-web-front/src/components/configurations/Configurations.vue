<template>
    <div class="flex-container">
        <!-- <div class="title">
            <h1>Configurations</h1>
        </div> -->
        <div class="list-container">
            <configurations-list></configurations-list>
        </div>
    </div>
</template>

<script>
import ConfigurationsList from './ConfigurationsList.vue';
export default{
    components: {
        ConfigurationsList
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    /* align-items: center; */
    /* width: 100%;
    height: 100%;
    color: white;
    background-color: blueviolet;
    margin: auto;
    overflow-y: auto; */
}

.title {
    /* background-color: brown; */
    height: 5vh;
    margin: 1vh 1vw;
}

.list-container {
    height: 90vh;
    width: 100%;
}
</style>
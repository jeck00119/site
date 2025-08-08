<template>
    <div class="flex-container" :style="{width: width, height: height}">
        <div class="table-wrapper">
            <table class="result-table">
                <thead>
                    <tr>
                        <th>Result Name</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tr v-for="value, key in data" :key="key" v-memo="[value]">
                    <td>{{ key }}</td>
                    <td>{{ value }}</td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script>
export default{
    props: ['width', 'height', 'data'],

    setup() {
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    width: 100%;
    color: white;
    background-color: rgb(32, 30, 30);
}

.table-wrapper {
    height: 70vh;
    overflow-y: auto;
    width: 100%;
}

.table-wrapper thead th {
    position: sticky;
    top: 0;
    z-index: 1;
}

table {
    border-collapse: collapse;
    width: 100%;
    background-color: antiquewhite;
}

.result-table {
    background-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    width: 100%;
    border-collapse: collapse;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.26);
    margin: 0;
}

.result-table tr{
    border-bottom: 1px solid #696464;
}

.result-table td{
    background-color: #524d4d;
}
</style>